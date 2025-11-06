// OAuth2 Token Generator JavaScript

// ページ読み込み時にトークンを確認
document.addEventListener('DOMContentLoaded', function() {
    loadTokens();
    toggleFlowFields();
});

// フロータイプに応じてフィールドの表示を切り替え
function toggleFlowFields() {
    const flowType = document.getElementById('flow_type').value;
    const authUrlField = document.getElementById('auth_url').parentElement;
    
    if (flowType === 'client_credentials') {
        authUrlField.style.display = 'none';
        document.getElementById('auth_url').required = false;
    } else {
        authUrlField.style.display = 'block';
        document.getElementById('auth_url').required = true;
    }
}

// トークン情報を読み込み
async function loadTokens() {
    try {
        const response = await fetch('/api/tokens');
        const tokens = await response.json();
        
        if (tokens && Object.keys(tokens).length > 0) {
            displayTokens(tokens);
        }
    } catch (error) {
        console.error('トークン読み込みエラー:', error);
    }
}

// トークンを画面に表示
function displayTokens(tokens) {
    const tokenDisplay = document.getElementById('token-display');
    const accessTokenField = document.getElementById('access_token');
    const refreshTokenField = document.getElementById('refresh_token');
    const refreshTokenGroup = document.getElementById('refresh_token_group');
    const tokenInfo = document.getElementById('token_info');
    
    // アクセストークンを表示
    if (tokens.access_token) {
        accessTokenField.value = tokens.access_token;
        tokenDisplay.style.display = 'block';
    }
    
    // リフレッシュトークンを表示
    if (tokens.refresh_token) {
        refreshTokenField.value = tokens.refresh_token;
        refreshTokenGroup.style.display = 'block';
    } else {
        refreshTokenGroup.style.display = 'none';
    }
    
    // トークン情報を表示
    let infoHtml = '<dl class="row token-info">';
    
    if (tokens.token_type) {
        infoHtml += `<dt class="col-sm-3">トークンタイプ:</dt><dd class="col-sm-9">${tokens.token_type}</dd>`;
    }
    
    if (tokens.expires_in) {
        const expiryTime = new Date(Date.now() + tokens.expires_in * 1000);
        infoHtml += `<dt class="col-sm-3">有効期限:</dt><dd class="col-sm-9">${tokens.expires_in}秒 (${expiryTime.toLocaleString()})</dd>`;
    }
    
    if (tokens.scope) {
        infoHtml += `<dt class="col-sm-3">スコープ:</dt><dd class="col-sm-9">${tokens.scope}</dd>`;
    }
    
    infoHtml += '</dl>';
    tokenInfo.innerHTML = infoHtml;
}

// クリップボードにコピー
async function copyToClipboard(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.parentElement.querySelector('button');
    const originalText = button.textContent;
    
    try {
        await navigator.clipboard.writeText(field.value);
        
        // コピー成功のフィードバック
        button.textContent = 'コピー済み!';
        button.classList.add('btn-success');
        button.classList.remove('btn-outline-secondary');
        field.classList.add('copy-success');
        
        setTimeout(() => {
            button.textContent = originalText;
            button.classList.remove('btn-success');
            button.classList.add('btn-outline-secondary');
            field.classList.remove('copy-success');
        }, 2000);
        
    } catch (error) {
        console.error('コピーエラー:', error);
        
        // フォールバック: テキストを選択
        field.select();
        field.setSelectionRange(0, 99999); // モバイル対応
        
        try {
            document.execCommand('copy');
            button.textContent = 'コピー済み!';
            setTimeout(() => {
                button.textContent = originalText;
            }, 2000);
        } catch (fallbackError) {
            alert('コピーに失敗しました。手動でテキストを選択してコピーしてください。');
        }
    }
}

// リフレッシュトークンを使用してトークンを更新
async function refreshTokens() {
    const refreshButton = document.querySelector('[onclick="refreshTokens()"]');
    const originalText = refreshButton.textContent;
    
    try {
        // ローディング状態
        refreshButton.disabled = true;
        refreshButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>更新中...';
        
        const response = await fetch('/refresh_token', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            }
        });
        
        const result = await response.json();
        
        if (result.success) {
            displayTokens(result.tokens);
            showAlert('トークンが正常に更新されました', 'success');
        } else {
            showAlert(`リフレッシュエラー: ${result.error}`, 'danger');
        }
        
    } catch (error) {
        console.error('リフレッシュエラー:', error);
        showAlert('トークンの更新に失敗しました', 'danger');
    } finally {
        // ローディング状態を解除
        refreshButton.disabled = false;
        refreshButton.textContent = originalText;
    }
}

// セッションをクリア
async function clearSession() {
    if (confirm('セッションをクリアしますか？すべてのトークンが削除されます。')) {
        try {
            const response = await fetch('/clear_session', {
                method: 'POST'
            });
            
            if (response.ok) {
                // ページをリロード
                window.location.reload();
            }
        } catch (error) {
            console.error('セッションクリアエラー:', error);
            showAlert('セッションのクリアに失敗しました', 'danger');
        }
    }
}

// アラートメッセージを表示
function showAlert(message, type) {
    const alertContainer = document.querySelector('.container .row .col-md-8');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    // 既存のアラートの後に挿入
    const existingAlerts = alertContainer.querySelectorAll('.alert');
    if (existingAlerts.length > 0) {
        existingAlerts[existingAlerts.length - 1].after(alert);
    } else {
        const title = alertContainer.querySelector('h1');
        title.after(alert);
    }
    
    // 5秒後に自動削除
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// フォームデータをクリア
async function clearFormData() {
    if (confirm('フォームの入力内容をクリアしますか？')) {
        try {
            const response = await fetch('/clear_form_data', {
                method: 'POST'
            });
            
            if (response.ok) {
                // フォームフィールドをクリア
                document.getElementById('flow_type').selectedIndex = 0;
                document.getElementById('auth_url').value = '';
                document.getElementById('token_url').value = '';
                document.getElementById('client_id').value = '';
                document.getElementById('client_secret').value = '';
                document.getElementById('scope').value = '';
                
                // フロータイプの表示を更新
                toggleFlowFields();
                
                showAlert('フォームデータをクリアしました', 'info');
            }
        } catch (error) {
            console.error('フォームクリアエラー:', error);
            showAlert('フォームのクリアに失敗しました', 'danger');
        }
    }
}

// フォーム送信前のバリデーション
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form[action="/authorize"]');
    
    form.addEventListener('submit', function(e) {
        const authUrl = document.getElementById('auth_url').value;
        const tokenUrl = document.getElementById('token_url').value;
        const clientId = document.getElementById('client_id').value;
        
        // URL形式のチェック
        try {
            if (authUrl) new URL(authUrl);
            new URL(tokenUrl);
        } catch (error) {
            e.preventDefault();
            showAlert('有効なURL形式で入力してください', 'danger');
            return;
        }
        
        // 必須フィールドのチェック
        if (!clientId.trim()) {
            e.preventDefault();
            showAlert('クライアントIDは必須です', 'danger');
            return;
        }
        
        // ローディング状態
        const submitButton = form.querySelector('button[type="submit"]');
        submitButton.disabled = true;
        submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>処理中...';
    });
});