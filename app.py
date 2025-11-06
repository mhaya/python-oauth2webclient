from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_session import Session
import requests
import secrets
import base64
import hashlib
import urllib.parse
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
Config.init_app(app)
Session(app)

def generate_pkce_pair():
    """PKCE用のcode_verifierとcode_challengeを生成"""
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8').rstrip('=')
    code_challenge = base64.urlsafe_b64encode(
        hashlib.sha256(code_verifier.encode('utf-8')).digest()
    ).decode('utf-8').rstrip('=')
    return code_verifier, code_challenge

@app.route('/')
def index():
    """メインページ"""
    # デバッグ情報として現在のリダイレクトURIを渡す
    current_redirect_uri = Config.get_redirect_uri()
    
    # 保存されたフォーム設定を取得
    saved_config = session.get('form_config')
    
    return render_template('index.html', 
                         redirect_uri=current_redirect_uri,
                         saved_config=saved_config)

@app.route('/authorize', methods=['POST'])
def authorize():
    """OAuth2認可フローを開始"""
    try:
        # フォームデータを取得
        auth_url = request.form.get('auth_url')
        token_url = request.form.get('token_url')
        client_id = request.form.get('client_id')
        client_secret = request.form.get('client_secret')
        scope = request.form.get('scope', '')
        flow_type = request.form.get('flow_type', 'authorization_code')
        
        # 必須パラメータのチェック
        if not all([auth_url, token_url, client_id]):
            flash('必須項目が入力されていません', 'error')
            return redirect(url_for('index'))
        
        # セッションにデータを保存
        session['oauth_config'] = {
            'auth_url': auth_url,
            'token_url': token_url,
            'client_id': client_id,
            'client_secret': client_secret,
            'scope': scope,
            'flow_type': flow_type
        }
        
        # フォーム設定も保存（再表示用）
        session['form_config'] = {
            'auth_url': auth_url,
            'token_url': token_url,
            'client_id': client_id,
            'client_secret': client_secret,  # セキュリティ上の理由で実際の環境では保存しない方が良い
            'scope': scope,
            'flow_type': flow_type
        }
        
        if flow_type == 'client_credentials':
            # Client Credentials Flowの場合は直接トークンを取得
            return redirect(url_for('get_client_credentials_token'))
        else:
            # Authorization Code Flowの場合
            state = secrets.token_urlsafe(32)
            code_verifier, code_challenge = generate_pkce_pair()
            
            session['oauth_state'] = state
            session['code_verifier'] = code_verifier
            
            # 認可URLを構築
            redirect_uri = Config.get_redirect_uri()
            print(f"[DEBUG] Using redirect URI: {redirect_uri}")  # デバッグ情報
            
            params = {
                'response_type': 'code',
                'client_id': client_id,
                'redirect_uri': redirect_uri,
                'scope': scope,
                'state': state,
                'code_challenge': code_challenge,
                'code_challenge_method': 'S256'
            }
            
            auth_redirect_url = f"{auth_url}?{urllib.parse.urlencode(params)}"
            print(f"[DEBUG] Authorization URL: {auth_redirect_url}")  # デバッグ情報
            return redirect(auth_redirect_url)
            
    except Exception as e:
        flash(f'エラーが発生しました: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/callback')
@app.route('/callback/')
def callback():
    """OAuth2認可コールバック"""
    try:
        # エラーチェック
        error = request.args.get('error')
        if error:
            error_description = request.args.get('error_description', '')
            flash(f'認可エラー: {error} - {error_description}', 'error')
            return redirect(url_for('index'))
        
        # パラメータ取得
        code = request.args.get('code')
        state = request.args.get('state')
        
        # stateの検証
        if not state or state != session.get('oauth_state'):
            flash('無効なstateパラメータです', 'error')
            return redirect(url_for('index'))
        
        if not code:
            flash('認可コードが取得できませんでした', 'error')
            return redirect(url_for('index'))
        
        # トークン交換
        oauth_config = session.get('oauth_config')
        if not oauth_config:
            flash('OAuth設定が見つかりません', 'error')
            return redirect(url_for('index'))
        
        # トークンリクエスト
        token_data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': Config.get_redirect_uri(),
            'client_id': oauth_config['client_id'],
            'code_verifier': session.get('code_verifier')
        }
        
        # デバッグ情報
        print(f"[DEBUG] Token request URL: {oauth_config['token_url']}")
        print(f"[DEBUG] Token request data: {token_data}")
        print(f"[DEBUG] Client ID: {oauth_config['client_id']}")
        print(f"[DEBUG] Client Secret provided: {'Yes' if oauth_config['client_secret'] else 'No'}")
        
        # クライアント認証
        auth = None
        headers = {'Accept': 'application/json', 'Content-Type': 'application/x-www-form-urlencoded'}
        
        if oauth_config['client_secret']:
            # まずBasic認証を試す
            auth = (oauth_config['client_id'], oauth_config['client_secret'])
            print(f"[DEBUG] Using Basic Authentication")
        else:
            # パブリッククライアントの場合はclient_idをフォームデータに含める
            print(f"[DEBUG] Using public client (no authentication)")
        
        print(f"[DEBUG] Request headers: {headers}")
        
        response = requests.post(
            oauth_config['token_url'],
            data=token_data,
            auth=auth,
            headers=headers
        )
        
        # Basic認証が失敗した場合、POSTボディでクライアント認証を試す
        if response.status_code == 401 and oauth_config['client_secret']:
            print(f"[DEBUG] Basic auth failed, trying client credentials in POST body")
            token_data_with_secret = token_data.copy()
            token_data_with_secret['client_secret'] = oauth_config['client_secret']
            
            response = requests.post(
                oauth_config['token_url'],
                data=token_data_with_secret,
                headers=headers
            )
        
        if response.status_code == 200:
            token_response = response.json()
            session['tokens'] = token_response
            flash('トークンの取得に成功しました', 'success')
        else:
            flash(f'トークン取得エラー: {response.status_code} - {response.text}', 'error')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'コールバック処理エラー: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/client_credentials_token')
def get_client_credentials_token():
    """Client Credentials Flowでトークンを取得"""
    try:
        oauth_config = session.get('oauth_config')
        if not oauth_config:
            flash('OAuth設定が見つかりません', 'error')
            return redirect(url_for('index'))
        
        token_data = {
            'grant_type': 'client_credentials',
            'scope': oauth_config['scope']
        }
        
        auth = (oauth_config['client_id'], oauth_config['client_secret'])
        
        response = requests.post(
            oauth_config['token_url'],
            data=token_data,
            auth=auth,
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            token_response = response.json()
            session['tokens'] = token_response
            flash('トークンの取得に成功しました', 'success')
        else:
            flash(f'トークン取得エラー: {response.status_code} - {response.text}', 'error')
        
        return redirect(url_for('index'))
        
    except Exception as e:
        flash(f'Client Credentialsトークン取得エラー: {str(e)}', 'error')
        return redirect(url_for('index'))

@app.route('/refresh_token', methods=['POST'])
def refresh_token():
    """リフレッシュトークンを使用してアクセストークンを更新"""
    try:
        tokens = session.get('tokens')
        oauth_config = session.get('oauth_config')
        
        if not tokens or not oauth_config:
            return jsonify({'error': 'トークンまたは設定が見つかりません'}), 400
        
        refresh_token = tokens.get('refresh_token')
        if not refresh_token:
            return jsonify({'error': 'リフレッシュトークンが見つかりません'}), 400
        
        token_data = {
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token
        }
        
        auth = None
        if oauth_config['client_secret']:
            auth = (oauth_config['client_id'], oauth_config['client_secret'])
        
        response = requests.post(
            oauth_config['token_url'],
            data=token_data,
            auth=auth,
            headers={'Accept': 'application/json'}
        )
        
        if response.status_code == 200:
            new_tokens = response.json()
            # 新しいリフレッシュトークンが返されない場合は既存のものを保持
            if 'refresh_token' not in new_tokens:
                new_tokens['refresh_token'] = refresh_token
            
            session['tokens'] = new_tokens
            return jsonify({'success': True, 'tokens': new_tokens})
        else:
            return jsonify({'error': f'リフレッシュエラー: {response.status_code} - {response.text}'}), 400
        
    except Exception as e:
        return jsonify({'error': f'リフレッシュトークン処理エラー: {str(e)}'}), 500

@app.route('/clear_session', methods=['POST'])
def clear_session():
    """セッションをクリア"""
    session.clear()
    flash('セッションをクリアしました', 'info')
    return redirect(url_for('index'))

@app.route('/api/tokens')
def get_tokens():
    """現在のトークン情報をJSON形式で返す"""
    tokens = session.get('tokens', {})
    return jsonify(tokens)

@app.route('/clear_form_data', methods=['POST'])
def clear_form_data():
    """フォーム設定をクリア"""
    if 'form_config' in session:
        del session['form_config']
    flash('フォームデータをクリアしました', 'info')
    return '', 200

if __name__ == '__main__':
    # HTTP版（開発用）
    app.run(
        debug=True, 
        host='0.0.0.0', 
        port=5000
    )