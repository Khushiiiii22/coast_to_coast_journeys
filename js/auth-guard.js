/**
 * C2C Journeys - Auth Guard
 * Handles mandatory login checks and session timeouts
 */

const AuthGuard = {
    timer: null,
    warningShown: false,
    checkInterval: 60000, // 1 minute in milliseconds

    /**
     * Initialize the Auth Guard
     */
    init: async function () {
        console.log('🛡️ AuthGuard Initializing...');

        // Check initial session
        const session = await this.checkSession();

        if (!session) {
            this.startLoginTimer();
        } else {
            console.log('✅ User is logged in');
            this.updateUIForLoggedInUser(session.user);
        }

        // Listen for auth state changes
        if (window.supabase) {
            window.supabase.auth.onAuthStateChange((event, session) => {
                if (event === 'SIGNED_IN') {
                    this.stopLoginTimer();
                    this.closeLoginModal();
                    this.updateUIForLoggedInUser(session.user);
                } else if (event === 'SIGNED_OUT') {
                    this.startLoginTimer();
                    this.updateUIForLoggedOutUser();
                }
            });
        }
    },

    /**
     * Check if user is authenticated
     */
    isAuthenticated: async function () {
        if (!window.supabase) return false;
        const { data: { session } } = await window.supabase.auth.getSession();
        return !!session;
    },

    /**
     * Get current session
     */
    checkSession: async function () {
        if (!window.supabase) return null;
        try {
            const { data: { session } } = await window.supabase.auth.getSession();
            return session;
        } catch (e) {
            console.error('Session check failed', e);
            return null;
        }
    },

    /**
     * Start the 1-minute timer for login warning
     */
    startLoginTimer: function () {
        if (this.timer) clearTimeout(this.timer);
        console.log('⏳ Login timer started (1 minute)');

        this.timer = setTimeout(() => {
            this.showLoginModal();
        }, this.checkInterval);
    },

    /**
     * Stop the timer
     */
    stopLoginTimer: function () {
        if (this.timer) {
            clearTimeout(this.timer);
            this.timer = null;
        }
    },

    /**
     * Show the login requirement modal
     */
    showLoginModal: function () {
        if (this.warningShown) return; // Don't show multiple times immediately

        // Check if modal already exists
        let modal = document.getElementById('authGuardModal');

        if (!modal) {
            this.createModal();
            modal = document.getElementById('authGuardModal');
        }

        modal.classList.add('active');
        this.warningShown = true;
    },

    /**
     * Close the login modal
     */
    closeLoginModal: function () {
        const modal = document.getElementById('authGuardModal');
        if (modal) {
            modal.classList.remove('active');
        }
        this.warningShown = false;

        // Restart timer if still not logged in? 
        // Requirement says: "after evry 1 minute if the user has not logged in they should get a message"
        // So yes, restart timer.
        this.isAuthenticated().then(isAuth => {
            if (!isAuth) this.startLoginTimer();
        });
    },

    /**
     * Create the modal HTML
     */
    createModal: function () {
        const modalHtml = `
            <div class="modal auth-guard-modal" id="authGuardModal">
                <div class="modal-overlay"></div>
                <div class="modal-content" style="max-width: 400px; text-align: center; padding: 30px;">
                    <div style="width: 60px; height: 60px; background: #e0f2fe; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px;">
                        <i class="fas fa-lock" style="font-size: 24px; color: #0e64a6;"></i>
                    </div>
                    <h2 style="font-size: 1.5rem; margin-bottom: 10px; color: #1e293b;">Login Required</h2>
                    <p style="color: #64748b; margin-bottom: 25px;">Please log in to continue browsing and booking hotels. This ensures you receive booking confirmations successfully.</p>
                    
                    <div style="display: flex; gap: 10px; justify-content: center;">
                        <a href="auth.html?redirect=${encodeURIComponent(window.location.pathname)}" class="btn btn-primary" style="flex: 1;">
                            Login / Sign Up
                        </a>
                        <button class="btn btn-outline" style="padding: 10px 20px;" onclick="AuthGuard.closeLoginModal()">
                            Detailed View
                        </button>
                    </div>
                </div>
            </div>
            <style>
                .auth-guard-modal {
                    display: none;
                    position: fixed;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    z-index: 9999;
                    align-items: center;
                    justify-content: center;
                }
                .auth-guard-modal.active {
                    display: flex;
                }
                .auth-guard-modal .modal-overlay {
                    position: absolute;
                    top: 0;
                    left: 0;
                    width: 100%;
                    height: 100%;
                    background: rgba(0, 0, 0, 0.5);
                    backdrop-filter: blur(2px);
                }
                .auth-guard-modal .modal-content {
                    position: relative;
                    background: white;
                    border-radius: 16px;
                    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.2);
                    z-index: 10;
                    animation: modalSlideUp 0.3s ease-out;
                }
                .auth-guard-modal .btn-outline:hover {
                    background: #f1f5f9;
                }
                @keyframes modalSlideUp {
                    from { transform: translateY(20px); opacity: 0; }
                    to { transform: translateY(0); opacity: 1; }
                }
            </style>
        `;
        document.body.insertAdjacentHTML('beforeend', modalHtml);
    },

    updateUIForLoggedInUser: function (user) {
        // Find header login/user elements
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) {
            loginBtn.innerHTML = '<i class="fas fa-user-circle"></i> Account';
            loginBtn.href = 'dashboard.html';
        }

        // Update any other UI elements?
        console.log('👤 User logged in:', user.email);
    },

    updateUIForLoggedOutUser: function () {
        const loginBtn = document.getElementById('loginBtn');
        if (loginBtn) {
            loginBtn.innerHTML = '<i class="fas fa-user"></i> Login';
            loginBtn.href = 'auth.html';
        }
    }
};

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    AuthGuard.init();
});
