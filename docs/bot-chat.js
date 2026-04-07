/*
 * Copyright (c) 2026 Yuri Tijerino. All rights reserved.
 * Unauthorized copying, modification, or distribution of this file is prohibited.
 */
// WP-200 Bot Chat Interface
// Connects to backend API - automatically detects environment

class WP200BotChat {
    constructor() {
        this.apiUrl = this.getApiUrl();
        this.conversationHistory = [];
        this.currentUserId = this.getUserId();
        this.currentLanguage = 'en';
        this.isLoading = false;
        this.init();
    }

    getApiUrl() {
        const isLocal = window.location.hostname === 'localhost' ||
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '';
        const isHttps = window.location.protocol === 'https:';

        if (isLocal) {
            const port = localStorage.getItem('bot_api_port') || '8001';
            return `http://localhost:${port}/api`;
        } else if (isHttps) {
            const cloudflareUrl = localStorage.getItem('bot_cloudflare_url');
            if (cloudflareUrl) return `${cloudflareUrl}/api`;
            return localStorage.getItem('wp200_api_url') || 'https://wp200bot.tijerino.ai/api';
        } else {
            const port = localStorage.getItem('bot_api_port') || '8001';
            return `http://localhost:${port}/api`;
        }
    }

    getUserId() {
        let userId = localStorage.getItem('bot_user_id');
        if (!userId) {
            userId = 'user_' + Math.random().toString(36).substr(2, 9);
            localStorage.setItem('bot_user_id', userId);
        }
        return userId;
    }

    init() {
        this.setupEventListeners();
        this.loadConversationHistory();
    }

    setupEventListeners() {
        const sendButton = document.getElementById('bot-send-btn');
        const messageInput = document.getElementById('bot-message-input');
        const languageToggle = document.getElementById('bot-language-toggle');

        if (sendButton) {
            sendButton.addEventListener('click', () => this.sendMessage());
        }

        if (messageInput) {
            messageInput.addEventListener('keypress', (e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    this.sendMessage();
                }
            });
        }

        if (languageToggle) {
            languageToggle.addEventListener('change', (e) => {
                this.currentLanguage = e.target.value;
            });
        }
    }

    loadConversationHistory() {
        const saved = localStorage.getItem('wp200_conversation');
        if (saved) {
            try {
                this.conversationHistory = JSON.parse(saved);
                this.renderConversationHistory();
            } catch (e) {
                console.error('Error loading conversation:', e);
            }
        }
    }

    saveConversationHistory() {
        localStorage.setItem('wp200_conversation', JSON.stringify(this.conversationHistory));
    }

    async sendMessage() {
        const messageInput = document.getElementById('bot-message-input');
        if (!messageInput) return;

        const message = messageInput.value.trim();
        if (!message || this.isLoading) return;

        this.addMessageToUI('user', message);
        messageInput.value = '';
        this.setLoading(true);

        try {
            const history = this.conversationHistory.map(msg => ({
                role: msg.role,
                content: msg.content
            }));
            history.push({ role: 'user', content: message });

            const response = await fetch(`${this.apiUrl}/chat`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'ngrok-skip-browser-warning': 'true'
                },
                body: JSON.stringify({
                    user_id: this.currentUserId,
                    message: message,
                    language: this.currentLanguage,
                    conversation_history: history.slice(0, -1),
                    use_rag: true
                })
            });

            if (!response.ok) {
                const errorText = await response.text();
                throw new Error(`API error: ${response.status} - ${errorText.substring(0, 100)}`);
            }

            const responseText = await response.text();
            let data;
            try {
                data = JSON.parse(responseText);
            } catch (parseError) {
                if (responseText.includes('ngrok') || responseText.includes('html')) {
                    throw new Error('Received non-JSON response. Please visit the API URL in your browser first to bypass any warnings.');
                }
                throw new Error(`Invalid JSON response: ${responseText.substring(0, 200)}`);
            }

            this.conversationHistory.push({ role: 'user', content: message });
            this.conversationHistory.push({ role: 'assistant', content: data.response });
            this.saveConversationHistory();
            this.addMessageToUI('assistant', data.response);

        } catch (error) {
            console.error('Chat error:', error);

            const errorMessages = {
                mixed_content: {
                    en: 'Cannot connect to HTTP API from HTTPS page (mixed content blocked).',
                    ja: 'セキュリティ上の理由により、HTTPSページからHTTP APIに接続できません。',
                    zh: '无法从HTTPS页面连接到HTTP API（混合内容被阻止）。',
                    ko: 'HTTPS 페이지에서 HTTP API에 연결할 수 없습니다 (혼합 콘텐츠 차단).',
                    es: 'No se puede conectar a la API HTTP desde una página HTTPS (contenido mixto bloqueado).'
                },
                connection: {
                    en: 'Cannot connect to API server. Please ensure the backend server is running at ' + this.apiUrl,
                    ja: 'APIサーバーに接続できません。バックエンドサーバーが起動しているか確認してください。',
                    zh: '无法连接到API服务器。请确保后端服务器正在运行。',
                    ko: 'API 서버에 연결할 수 없습니다. 백엔드 서버가 실행 중인지 확인하세요.',
                    es: 'No se puede conectar al servidor API. Asegúrese de que el servidor backend esté en ejecución.'
                },
                generic: {
                    en: 'An error occurred: ',
                    ja: 'エラーが発生しました: ',
                    zh: '发生错误: ',
                    ko: '오류가 발생했습니다: ',
                    es: 'Se produjo un error: '
                }
            };
            const lang = this.currentLanguage;

            let errorMessage = '';
            if (error.name === 'TypeError' && error.message.includes('Failed to fetch')) {
                const isHttps = window.location.protocol === 'https:';
                const apiIsHttp = this.apiUrl.startsWith('http://');

                if (isHttps && apiIsHttp) {
                    errorMessage = (errorMessages.mixed_content[lang] || errorMessages.mixed_content.en);
                } else {
                    errorMessage = (errorMessages.connection[lang] || errorMessages.connection.en);
                }
            } else {
                errorMessage = (errorMessages.generic[lang] || errorMessages.generic.en) + error.message;
            }

            this.addMessageToUI('system', errorMessage);
        } finally {
            this.setLoading(false);
        }
    }

    addMessageToUI(role, content) {
        const messagesContainer = document.getElementById('bot-messages');
        if (!messagesContainer) return;

        const messageDiv = document.createElement('div');
        messageDiv.className = `bot-message bot-message-${role}`;

        if (role === 'user') {
            messageDiv.innerHTML = `
                <div class="bot-message-content">
                    <strong>You:</strong> ${this.escapeHtml(content)}
                </div>`;
        } else if (role === 'assistant') {
            messageDiv.innerHTML = `
                <div class="bot-message-content">
                    <strong>WP-200 Bot:</strong> ${this.formatBotResponse(content)}
                </div>`;
        } else {
            messageDiv.innerHTML = `
                <div class="bot-message-content bot-message-system">
                    ${this.escapeHtml(content)}
                </div>`;
        }

        messagesContainer.appendChild(messageDiv);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    formatBotResponse(text) {
        return this.escapeHtml(text)
            .replace(/```(\w*)\n([\s\S]*?)```/g, '<pre><code>$2</code></pre>')
            .replace(/`([^`]+)`/g, '<code>$1</code>')
            .replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.+?)\*/g, '<em>$1</em>')
            .replace(/\n/g, '<br>');
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    setLoading(loading) {
        this.isLoading = loading;
        const sendButton = document.getElementById('bot-send-btn');
        const messageInput = document.getElementById('bot-message-input');

        const sendLabels = { en: 'Send', ja: '送信', zh: '发送', ko: '전송', es: 'Enviar' };
        const sendingLabels = { en: 'Sending...', ja: '送信中...', zh: '发送中...', ko: '전송 중...', es: 'Enviando...' };
        if (sendButton) {
            sendButton.disabled = loading;
            sendButton.textContent = loading
                ? (sendingLabels[this.currentLanguage] || sendingLabels.en)
                : (sendLabels[this.currentLanguage] || sendLabels.en);
        }

        if (messageInput) {
            messageInput.disabled = loading;
        }

        const loadingIndicator = document.getElementById('bot-loading');
        if (loadingIndicator) {
            loadingIndicator.style.display = loading ? 'block' : 'none';
        }
    }

    renderConversationHistory() {
        const messagesContainer = document.getElementById('bot-messages');
        if (!messagesContainer) return;

        // Keep the welcome message
        const welcome = messagesContainer.querySelector('.bot-message-welcome');
        messagesContainer.innerHTML = '';
        if (welcome) {
            const wrapper = document.createElement('div');
            wrapper.className = 'bot-message bot-message-assistant';
            wrapper.appendChild(welcome);
            messagesContainer.appendChild(wrapper);
        }

        this.conversationHistory.forEach(msg => {
            this.addMessageToUI(msg.role, msg.content);
        });
    }

    clearConversation() {
        const clearPrompts = {
            en: 'Clear conversation history?', ja: '会話履歴をクリアしますか？',
            zh: '清除对话记录？', ko: '대화 기록을 삭제하시겠습니까?', es: '¿Borrar historial de conversación?'
        };
        if (confirm(clearPrompts[this.currentLanguage] || clearPrompts.en)) {
            this.conversationHistory = [];
            this.saveConversationHistory();
            const messagesContainer = document.getElementById('bot-messages');
            if (messagesContainer) {
                messagesContainer.innerHTML = `
                    <div class="bot-message bot-message-assistant">
                        <div class="bot-message-content bot-message-welcome">
                            <strong>WP-200 Bot:</strong>
                            Conversation cleared. How can I help you?
                            <br>会話がクリアされました。何かお手伝いできますか？
                        </div>
                    </div>`;
            }
        }
    }
}

// Initialize chat when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.wp200BotChat = new WP200BotChat();
    });
} else {
    window.wp200BotChat = new WP200BotChat();
}
