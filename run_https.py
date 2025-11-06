#!/usr/bin/env python3
"""
OAuth2 Token Generator - HTTPS起動スクリプト
"""
import os
import sys
from app import app

def check_ssl_files():
    """SSL証明書ファイルの存在を確認"""
    cert_path = 'certs/cert.pem'
    key_path = 'certs/key.pem'
    
    if not os.path.exists(cert_path) or not os.path.exists(key_path):
        print("SSL証明書が見つかりません。証明書を生成してください:")
        print("openssl req -x509 -newkey rsa:4096 -nodes -out certs/cert.pem -keyout certs/key.pem -days 365 -subj \"/C=JP/ST=Tokyo/L=Tokyo/O=OAuth2App/OU=Development/CN=localhost\"")
        sys.exit(1)

def main():
    """HTTPSでアプリケーションを起動"""
    check_ssl_files()
    
    # 環境変数の確認
    print(f"[DEBUG] HOST環境変数: {os.environ.get('HOST', 'localhost')}")
    print(f"[DEBUG] HTTPS_PORT環境変数: {os.environ.get('HTTPS_PORT', '8443')}")
    
    port = app.config['HTTPS_PORT']
    host = app.config['HOST']
    
    print(f"[DEBUG] 設定されたHOST: {host}")
    print(f"[DEBUG] 設定されたHTTPS_PORT: {port}")
    
    print("OAuth2 Token Generator を HTTPS で起動しています...")
    print(f"サーバー: 0.0.0.0:{port} (すべてのネットワークインターフェースで受信)")
    
    if port == 443:
        print(f"アクセスURL: https://{host}")
        print("注意: ポート443で起動するため、管理者権限が必要です。")
    else:
        print(f"アクセスURL: https://{host}:{port}")
        print("注意: 開発環境用ポートを使用しています。")
        print("本番環境ではHTTPS_PORT=443環境変数を設定してください。")
    
    print("注意: 自己署名証明書を使用しているため、ブラウザで警告が表示されます。")
    print("Chrome/Edge: \"詳細設定\" → \"<hostname> にアクセスする (安全ではありません)\"")
    print("Firefox: \"詳細情報\" → \"危険性を承知で続行\"")
    print("")
    print("停止するには Ctrl+C を押してください")
    print("-" * 50)
    
    try:
        app.run(
            debug=True,
            host='0.0.0.0',
            port=port,
            ssl_context=app.config['SSL_CONTEXT']
        )
    except KeyboardInterrupt:
        print("\nアプリケーションを停止しました")
    except Exception as e:
        print(f"エラーが発生しました: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()