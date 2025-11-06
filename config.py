import os
import secrets

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or secrets.token_hex(16)
    SESSION_TYPE = 'filesystem'
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True
    SESSION_KEY_PREFIX = 'oauth2app:'
    SESSION_FILE_DIR = '/tmp/oauth2app_sessions'
    
    # OAuth2設定
    HOST = os.environ.get('HOST', 'localhost')
    HTTPS_PORT = int(os.environ.get('HTTPS_PORT', 8443))
    
    @staticmethod
    def get_redirect_uri():
        host = os.environ.get('HOST', 'localhost')
        port = int(os.environ.get('HTTPS_PORT', 8443))
        if port == 443:
            return f'https://{host}/callback'
        else:
            return f'https://{host}:{port}/callback'
    
    # HTTPS設定
    SSL_CONTEXT = ('certs/cert.pem', 'certs/key.pem')
    
    # 開発環境設定
    DEBUG = os.environ.get('FLASK_ENV') == 'development'
    
    @staticmethod
    def init_app(app):
        os.makedirs(app.config['SESSION_FILE_DIR'], exist_ok=True)