# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

OAuth2トークンを取得できるWebアプリケーションです。ブラウザからアクセスして、任意のOAuth2サーバーからアクセストークンとリフレッシュトークンを取得できます。開発環境から本番環境まで柔軟に対応し、0.0.0.0バインドによる外部アクセスも可能です。

### 主な機能
- OAuth2サーバーのURL、クライアントID/シークレット、スコープの入力
- Authorization Code FlowとClient Credentials Flowに対応
- 取得したトークンの表示とワンクリックコピー機能
- PKCE（Proof Key for Code Exchange）対応
- リフレッシュトークンによるアクセストークン更新
- フォーム値の自動保存・復元機能
- フォームクリア機能
- HTTPS/HTTP両対応（開発・本番環境設定）
- 動的リダイレクトURI生成（環境変数ベース）
- レスポンシブWebUI（Bootstrap 5使用）
- デバッグ機能（リクエスト内容とレスポンスの詳細ログ）

### 技術スタック
- **バックエンド**: Python Flask 2.2.5+
- **フロントエンド**: HTML5 + Bootstrap 5 + Vanilla JavaScript
- **セッション管理**: Flask-Session（ファイルシステムベース）
- **パッケージ管理**: uv（推奨）またはpip
- **HTTPS**: 自己署名SSL証明書（開発用）
- **セキュリティ**: CSRF保護、PKCE、SSL/TLS暗号化

## 開発コマンド

### uv使用（推奨）

```bash
# uvのインストール（初回のみ）
curl -LsSf https://astral.sh/uv/install.sh | sh

# プロジェクトの初期化と依存関係の同期
uv sync

# 開発サーバーの起動（HTTP）
uv run python app.py

# 開発サーバーの起動（HTTPS - ポート8443）
uv run python run_https.py

# 外部アクセス用ホスト名指定
HOST=your-server-ip uv run python run_https.py

# 本番環境でポート443使用（管理者権限必要）
sudo env PATH="$HOME/.local/bin:$PATH" HOST=your-domain.com HTTPS_PORT=443 uv run python run_https.py

# 依存関係の追加
uv add package-name

# 開発依存関係の追加
uv add --dev package-name

# 依存関係の削除
uv remove package-name

# コードの整形
uv run black app.py
uv run flake8 app.py

# テスト実行
uv run pytest
```

### 従来のpip/venv使用

```bash
# 仮想環境の作成・有効化
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 依存関係のインストール
pip install -r requirements.txt

# 開発サーバーの起動（HTTP）
python app.py

# 開発サーバーの起動（HTTPS - ポート8443）
python run_https.py

# 外部アクセス用ホスト名指定
HOST=your-server-ip python run_https.py

# 本番環境でポート443使用（管理者権限必要）
sudo env PATH="$PATH" HOST=your-domain.com HTTPS_PORT=443 python run_https.py

# 依存関係の更新
pip freeze > requirements.txt

# コードの整形
black app.py
flake8 app.py
```

## アプリケーション構成

```
oauth2app/
├── app.py                 # メインアプリケーション
├── config.py             # 設定ファイル
├── pyproject.toml        # プロジェクト設定（uv管理）
├── uv.lock               # ロックファイル（uv管理）
├── requirements.txt      # Python依存関係（従来用）
├── run_https.py          # HTTPS起動スクリプト
├── certs/               # SSL証明書（自動生成）
│   ├── cert.pem         # SSL証明書
│   └── key.pem          # SSL秘密鍵
├── templates/            # HTMLテンプレート
│   └── index.html       # メインページ
├── static/              # 静的ファイル
│   ├── css/
│   │   └── style.css   # カスタムCSS
│   └── js/
│       └── script.js   # JavaScript
└── CLAUDE.md           # このファイル
```

## アーキテクチャ

### アプリケーション構成
- **Webサーバー**: Flask（0.0.0.0バインド、ポート設定可能）
- **セッション管理**: ファイルシステムベース（`/tmp/oauth2app_sessions`）
- **SSL/TLS**: 自己署名証明書による開発環境HTTPS対応
- **設定管理**: 環境変数ベースの動的設定

### OAuth2フロー実装
- **Authorization Code Flow**: 一般的なWebアプリケーション向け
  - PKCE対応（SHA256）による セキュリティ強化
  - 認可エンドポイントへのリダイレクト（stateパラメータ付き）
  - 認可コードの受け取りとバリデーション
  - アクセストークンとリフレッシュトークンの取得
  - 動的リダイレクトURI生成
  - 複数クライアント認証方法対応（Basic認証・POSTボディ）
- **Client Credentials Flow**: サーバー間通信向け
  - 直接トークンエンドポイントへのアクセス
  - Basic認証によるクライアント認証
- **詳細デバッグ機能**:
  - リクエストURL・パラメータのコンソール出力
  - クライアント認証方法の明示
  - 認証失敗時の代替方法自動試行

### セキュリティ機能
- **CSRF防止**: stateパラメータによる攻撃防止
- **コード横取り防止**: PKCEによる認可コード保護
- **セッション管理**: セッションベースの一時的なデータ保存
- **HTTPS強制**: 本番環境での暗号化通信
- **入力値検証**: URL形式チェック、パラメータサニタイズ

### UI/UX
- **レスポンシブデザイン**: Bootstrap 5による モバイル対応
- **トークン表示**: ワンクリックコピー機能付き
- **フォーム機能**: OAuth2フロータイプ選択、動的フィールド表示
- **フォーム値保持**: セッションベースの入力値自動保存・復元
- **フォーム管理**: ワンクリックでの入力値クリア機能
- **リダイレクトURI表示**: 現在の設定を画面上で確認可能
- **エラーハンドリング**: ユーザーフレンドリーなメッセージ表示
- **リアルタイム更新**: JavaScriptによるAPIアクセスとUI更新
- **セッション管理**: クリア機能とセッション状態表示
- **ローディング状態**: ボタンのスピナー表示とフィードバック

## セキュリティ考慮事項

- **機密情報の取り扱い**:
  - クライアントシークレットはセッション内のみで保持
  - フォーム値の保存（利便性とセキュリティのバランス）
  - トークンはメモリ内のみ、永続化しない
  - 本番環境では必ずHTTPS使用

- **HTTPS設定**:
  - 開発環境用自己署名証明書を使用
  - `run_https.py`でHTTPS起動（0.0.0.0で全インターフェース受信）
  - 開発環境: ポート8443（https://localhost:8443またはhttps://IPアドレス:8443）
  - 本番環境: HTTPS_PORT=443環境変数でポート443使用
  - ホスト名設定: HOST環境変数でアクセス用ホスト名指定（デフォルト: localhost）
  - ポート443使用時は管理者権限が必要
  - ブラウザの証明書警告を承認して使用
  - 本番環境では正式なSSL証明書を使用すること

- **OAuth2 Redirect URI設定**:
  - リダイレクトURIは環境変数に基づいて動的生成
  - 開発環境（デフォルト）: `https://localhost:8443/callback`
  - カスタムホスト指定: `https://your-host:8443/callback`
  - 本番環境（ポート443）: `https://your-domain.com/callback`
  - OAuth2プロバイダーの設定で上記URIを登録する必要がある
  - 環境変数による制御:
    - `HOST`: ホスト名（デフォルト: localhost）
    - `HTTPS_PORT`: ポート番号（デフォルト: 8443、443の場合はURI省略）
  - 動的生成ロジック: `config.py`の`get_redirect_uri()`メソッド

- **入力値検証**:
  - URLの妥当性チェック
  - リダイレクトURIの検証
  - パラメータのサニタイズ

- **エラーハンドリング**:
  - OAuth2エラーレスポンスの適切な処理
  - 詳細なエラー情報をログに記録（UIには表示しない）

## 開発手順

### uv使用（推奨手順）

1. **環境セットアップ**:
   ```bash
   # uvのインストール（初回のみ）
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # プロジェクトの初期化と依存関係の同期
   uv sync
   ```

2. **基本アプリケーション作成**:
   - `app.py`でFlaskアプリケーション作成
   - ルーティングとセッション管理の実装
   - 開発サーバーの起動テスト: `uv run python app.py`

3. **OAuth2フロー実装**:
   - Authorization Code Flow実装
   - Client Credentials Flow実装
   - Token exchange処理とエラーハンドリング
   - テスト: `uv run python app.py`でHTTP版確認

4. **HTTPS対応**:
   - SSL証明書生成（自動生成済み）
   - HTTPS設定の実装
   - テスト: `uv run python run_https.py`でHTTPS版確認

5. **フロントエンド作成**:
   - HTMLテンプレート作成（Bootstrap使用）
   - JavaScript機能実装（コピー機能、API連携）
   - CSS スタイリング

6. **テストとデバッグ**:
   - 各OAuth2フローのテスト
   - エラーケースの確認
   - セキュリティチェック
   - コード品質チェック: `uv run black .` / `uv run flake8 .`

7. **本番デプロイ準備**:
   - 環境変数設定（HTTPS_PORT=443等）
   - 正式SSL証明書の設定
   - セキュリティ設定の確認
   - 本番起動: `sudo env PATH="$HOME/.local/bin:$PATH" HTTPS_PORT=443 uv run python run_https.py`

### 従来のpip/venv使用

1. **環境セットアップ**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **開発とテスト**:
   - 基本的な手順はuv版と同様
   - コマンド実行時は仮想環境を有効化してから実行

## トラブルシューティング

### ポート443でのsudo実行エラー

**問題**: `sudo python run_https.py`実行時に「ModuleNotFoundError: No module named 'flask'」

**解決方法**:
```bash
# uv使用時
sudo env PATH="$HOME/.local/bin:$PATH" HTTPS_PORT=443 uv run python run_https.py

# HOST指定時
sudo env HOST=api.example.org HTTPS_PORT=443 env PATH="$HOME/.local/bin:$PATH" uv run python run_https.py

# pip/venv使用時（仮想環境有効化後）
sudo env PATH="$PATH" HTTPS_PORT=443 python run_https.py
```

**原因**: sudoは通常、セキュリティのため環境変数をリセットするため、uvやvenv環境が認識されない

### SSL証明書警告

**問題**: ブラウザで「この接続ではプライバシーが保護されません」警告

**解決方法**:
- Chrome/Edge: 「詳細設定」→「localhost にアクセスする (安全ではありません)」
- Firefox: 「詳細情報」→「危険性を承知で続行」
- 本番環境では正式なSSL証明書を使用してください

### OAuth2認証エラー

**問題**: `invalid_client`エラーまたは`Mismatching redirect URI`エラー

**デバッグ手順**:
1. アプリケーションのコンソール出力でデバッグ情報を確認
2. リダイレクトURIが画面に表示されるので、OAuth2プロバイダーの設定と一致するかチェック
3. クライアントID/シークレットが正しいかダブルチェック
4. 異なるクライアント認証方法（Basic認証・POSTボディ）を自動試行

**解決方法**:
- HOST環境変数を正しいドメインに設定（例: `HOST=dev.ir.rcos.nii.ac.jp`）
- OAuth2プロバイダーでリダイレクトURIを正確に登録
- クライアント認証情報を再確認

### フォーム値が保存されない

**問題**: フォームに入力した値が次回アクセス時に復元されない

**解決方法**:
- 一度OAuth2フローを実行すると値が保存される
- 「フォームクリア」ボタンで明示的にクリア可能
- 「セッションクリア」ですべての情報をリセット可能

## 環境変数設定

| 変数名 | デフォルト値 | 説明 |
|--------|-------------|------|
| `HOST` | `localhost` | アクセス用ホスト名（リダイレクトURI生成に使用） |
| `HTTPS_PORT` | `8443` | HTTPSポート番号（443の場合はURI省略） |
| `SECRET_KEY` | 自動生成 | Flaskセッション暗号化キー |
| `FLASK_ENV` | - | `development`設定でデバッグモード有効 |

### 設定例

```bash
# 開発環境（デフォルト）
uv run python run_https.py

# 外部アクセス用（IPアドレス指定）
HOST=192.168.1.100 uv run python run_https.py

# 本番環境
HOST=api.example.com HTTPS_PORT=443 SECRET_KEY=your-secret-key uv run python run_https.py
```

## APIエンドポイント

| エンドポイント | メソッド | 説明 |
|---------------|---------|------|
| `/` | GET | メインページ（UI） |
| `/authorize` | POST | OAuth2認可フロー開始 |
| `/callback` | GET | OAuth2認可コールバック |
| `/client_credentials_token` | GET | Client Credentialsトークン取得 |
| `/refresh_token` | POST | リフレッシュトークンによる更新 |
| `/clear_session` | POST | セッションクリア |
| `/api/tokens` | GET | 現在のトークン情報（JSON） |
| `/clear_form_data` | POST | フォーム設定のクリア |

## 実装ファイル詳細

| ファイル | 説明 | 主な機能 |
|---------|------|----------|
| `app.py` | メインアプリケーション | ルーティング、OAuth2フロー、API実装 |
| `config.py` | 設定管理 | 環境変数、動的設定、リダイレクトURI生成 |
| `run_https.py` | HTTPS起動スクリプト | SSL設定、起動メッセージ、エラーハンドリング |
| `templates/index.html` | UIテンプレート | Bootstrap UI、フォーム、トークン表示 |
| `static/js/script.js` | JavaScript機能 | API通信、UI操作、コピー機能 |
| `static/css/style.css` | CSS スタイル | カスタムスタイル、レスポンシブ対応 |
| `pyproject.toml` | プロジェクト設定 | uv管理、依存関係、メタデータ |
| `uv.lock` | ロックファイル | 厳密な依存関係バージョン管理 |