// WP-200 Site Authentication
// Requires student handle + OTP email verification to access course content

class SiteAuth {
    constructor() {
        this.apiUrl = this._getApiUrl();
        this.session = null;
        this.init();
    }

    _getApiUrl() {
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

    init() {
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', () => this._start());
        } else {
            this._start();
        }
    }

    _start() {
        this._injectLoginOverlay();
        this._hideContent();
        this._checkExistingSession();
    }

    _injectLoginOverlay() {
        const overlay = document.createElement('div');
        overlay.id = 'auth-overlay';
        overlay.innerHTML = `
            <div id="auth-box">
                <div id="auth-header">
                    <h2>💻 WP-200</h2>
                    <p>Web Programming</p>
                </div>
                <div id="auth-body">
                    <!-- Step 1: Enter handle -->
                    <div id="auth-step-handle">
                        <h3 id="auth-login-title">Student Login</h3>
                        <p id="auth-login-desc">Enter your university handle to receive a verification code.</p>
                        <div class="auth-input-group">
                            <input type="text" id="auth-handle" placeholder="e.g., abc12345" autocomplete="username" spellcheck="false">
                            <span class="auth-domain">@kwansei.ac.jp</span>
                        </div>
                        <button id="auth-request-btn" onclick="siteAuth.requestOTP()">Send Verification Code</button>
                        <p id="auth-handle-error" class="auth-error"></p>
                    </div>

                    <!-- Step 2: Enter OTP -->
                    <div id="auth-step-otp" style="display: none;">
                        <h3>Enter Verification Code</h3>
                        <p id="auth-otp-sent-msg">A 6-digit code has been sent to your email.</p>
                        <input type="text" id="auth-otp" placeholder="000000" maxlength="6" autocomplete="one-time-code" style="text-align: center; font-size: 1.8rem; letter-spacing: 8px;">
                        <button id="auth-verify-btn" onclick="siteAuth.verifyOTP()">Verify</button>
                        <p id="auth-otp-error" class="auth-error"></p>
                        <p class="auth-link"><a href="#" onclick="siteAuth.showHandleStep(); return false;">Back / Change handle</a></p>
                    </div>
                </div>
            </div>
        `;
        document.body.prepend(overlay);

        // Enter key handlers
        document.getElementById('auth-handle').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.requestOTP();
        });
        document.getElementById('auth-otp').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.verifyOTP();
        });
    }

    _hideContent() {
        const main = document.querySelector('main');
        const nav = document.querySelector('.main-nav');
        if (main) main.style.display = 'none';
        if (nav) nav.style.display = 'none';
    }

    _showContent() {
        const main = document.querySelector('main');
        const nav = document.querySelector('.main-nav');
        const overlay = document.getElementById('auth-overlay');
        if (main) main.style.display = '';
        if (nav) nav.style.display = '';
        if (overlay) overlay.style.display = 'none';
    }

    async _checkExistingSession() {
        const token = localStorage.getItem('wp200_session_token');
        if (!token) return;

        try {
            const res = await fetch(`${this.apiUrl}/auth/validate-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                body: JSON.stringify({ token }),
            });
            const data = await res.json();
            if (data.valid) {
                this.session = data;
                this._onAuthenticated(data);
            } else {
                localStorage.removeItem('wp200_session_token');
            }
        } catch (e) {
            // Can't reach server - still allow cached session for basic navigation
            const cached = localStorage.getItem('wp200_session_data');
            if (cached) {
                try {
                    this.session = JSON.parse(cached);
                    this._onAuthenticated(this.session);
                } catch (_) {}
            }
        }
    }

    async requestOTP() {
        const handleInput = document.getElementById('auth-handle');
        const errorEl = document.getElementById('auth-handle-error');
        const btn = document.getElementById('auth-request-btn');
        const handle = handleInput.value.trim().toLowerCase();

        errorEl.textContent = '';

        if (!handle) {
            errorEl.textContent = 'Please enter your handle.';
            return;
        }

        // Basic format validation: 3 alpha + 5 digits
        if (!/^[a-z]{3}\d{5}$/.test(handle)) {
            errorEl.textContent = 'Handle format: 3 letters + 5 digits (e.g., abc12345)';
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Sending...';

        try {
            const res = await fetch(`${this.apiUrl}/auth/request-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                body: JSON.stringify({ handle }),
            });

            if (res.ok) {
                const data = await res.json();
                document.getElementById('auth-otp-sent-msg').textContent =
                    `A 6-digit code has been sent to ${data.email_masked}`;
                this.showOTPStep();
            } else {
                const err = await res.json();
                errorEl.textContent = err.detail || 'Failed to send code. Please try again.';
            }
        } catch (e) {
            errorEl.textContent = 'Cannot connect to server. Please try again later.';
        } finally {
            btn.disabled = false;
            btn.textContent = 'Send Verification Code';
        }
    }

    async verifyOTP() {
        const handle = document.getElementById('auth-handle').value.trim().toLowerCase();
        const otpInput = document.getElementById('auth-otp');
        const errorEl = document.getElementById('auth-otp-error');
        const btn = document.getElementById('auth-verify-btn');
        const otp = otpInput.value.trim();

        errorEl.textContent = '';

        if (!otp || otp.length !== 6) {
            errorEl.textContent = 'Please enter the 6-digit code.';
            return;
        }

        btn.disabled = true;
        btn.textContent = 'Verifying...';

        try {
            const res = await fetch(`${this.apiUrl}/auth/verify-otp`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                body: JSON.stringify({ handle, otp }),
            });

            if (res.ok) {
                const data = await res.json();
                localStorage.setItem('wp200_session_token', data.token);
                localStorage.setItem('wp200_session_data', JSON.stringify(data.student));
                this.session = data.student;
                this._onAuthenticated(data.student);
            } else {
                const err = await res.json();
                errorEl.textContent = err.detail || 'Invalid code. Please try again.';
                otpInput.value = '';
                otpInput.focus();
            }
        } catch (e) {
            errorEl.textContent = 'Cannot connect to server. Please try again later.';
        } finally {
            btn.disabled = false;
            btn.textContent = 'Verify';
        }
    }

    _onAuthenticated(student) {
        this._showContent();

        // Pre-fill student ID in submission forms
        const studentIdField = document.getElementById('student-id');
        const gradeStudentIdField = document.getElementById('grade-student-id');
        if (studentIdField && student.student_id) {
            studentIdField.value = student.student_id;
            studentIdField.readOnly = true;
        }
        if (gradeStudentIdField && student.student_id) {
            gradeStudentIdField.value = student.student_id;
            gradeStudentIdField.readOnly = true;
        }

        // Update bot user ID
        if (student.handle) {
            localStorage.setItem('bot_user_id', student.handle);
        }

        // Add user info + logout to nav
        this._addUserNav(student);
    }

    _addUserNav(student) {
        const nav = document.querySelector('.main-nav .container');
        if (!nav || document.getElementById('auth-user-nav')) return;

        const name = student.name || student.handle || '';
        const userSpan = document.createElement('span');
        userSpan.id = 'auth-user-nav';
        userSpan.style.cssText = 'margin-left: auto; display: flex; align-items: center; gap: 10px; font-size: 0.9rem;';
        userSpan.innerHTML = `
            <span style="color: var(--text-light);">${name}</span>
            <a href="#" onclick="siteAuth.logout(); return false;" style="color: var(--text-light); font-size: 0.85rem;">Logout</a>
        `;
        nav.appendChild(userSpan);
    }

    logout() {
        const token = localStorage.getItem('wp200_session_token');
        if (token) {
            fetch(`${this.apiUrl}/auth/logout`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json', 'ngrok-skip-browser-warning': 'true' },
                body: JSON.stringify({ token }),
            }).catch(() => {});
        }
        localStorage.removeItem('wp200_session_token');
        localStorage.removeItem('wp200_session_data');
        location.reload();
    }

    showHandleStep() {
        document.getElementById('auth-step-handle').style.display = '';
        document.getElementById('auth-step-otp').style.display = 'none';
        document.getElementById('auth-otp').value = '';
        document.getElementById('auth-otp-error').textContent = '';
    }

    showOTPStep() {
        document.getElementById('auth-step-handle').style.display = 'none';
        document.getElementById('auth-step-otp').style.display = '';
        document.getElementById('auth-otp').value = '';
        document.getElementById('auth-otp').focus();
    }

    getToken() {
        return localStorage.getItem('wp200_session_token');
    }

    getStudentId() {
        return this.session?.student_id || '';
    }
}

const siteAuth = new SiteAuth();
