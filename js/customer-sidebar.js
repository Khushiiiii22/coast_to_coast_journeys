/**
 * Customer Sidebar Component
 * Provides navigation sidebar for customer-facing booking pages
 */

class CustomerSidebar {
    constructor() {
        this.sidebar = null;
        this.isCollapsed = localStorage.getItem('sidebar_collapsed') === 'true';
        this.isMobileOpen = false;
        this.currentUser = null;
    }

    /**
     * Initialize the sidebar
     */
    async init() {
        // Check authentication status
        await this.checkAuthStatus();
        // Render sidebar
        this.render();
        // Attach event listeners
        this.attachEventListeners();
        // Set initial state
        this.updateActiveLink();
    }

    /**
     * Check if user is logged in
     */
    async checkAuthStatus() {
        if (typeof SupabaseDB !== 'undefined') {
            try {
                const session = await SupabaseDB.getSession();
                if (session && session.user) {
                    this.currentUser = {
                        email: session.user.email,
                        name: session.user.user_metadata?.full_name ||
                            session.user.user_metadata?.name ||
                            session.user.email?.split('@')[0] || 'User'
                    };
                }
            } catch (error) {
                console.log('Auth check failed:', error);
            }
        }
    }

    /**
     * Get user initials for avatar
     */
    getInitials(name) {
        if (!name) return 'U';
        return name.split(' ').map(n => n[0]).join('').substring(0, 2).toUpperCase();
    }

    /**
     * Get sidebar HTML for logged-in user
     */
    getLoggedInUserSection() {
        const initials = this.getInitials(this.currentUser?.name);
        const name = this.currentUser?.name || 'User';
        const email = this.currentUser?.email || 'user@example.com';

        return `
            <div class="sidebar-user">
                <div class="sidebar-user-avatar">${initials}</div>
                <div class="sidebar-user-info">
                    <div class="sidebar-user-name">${name}</div>
                    <div class="sidebar-user-email">${email}</div>
                </div>
            </div>
        `;
    }

    /**
     * Get sidebar HTML for guest user
     */
    getGuestUserSection() {
        return `
            <div class="sidebar-login-banner">
                <p>Sign in to access your bookings and wishlist</p>
                <a href="auth.html" class="sidebar-login-btn">
                    <i class="fas fa-sign-in-alt"></i> Sign In
                </a>
            </div>
        `;
    }

    /**
     * Render the sidebar HTML
     */
    render() {
        const sidebarHTML = `
            <div class="sidebar-mobile-overlay" id="sidebarOverlay"></div>
            
            <aside class="customer-sidebar ${this.isCollapsed ? 'collapsed' : ''}" id="customerSidebar">
                <!-- Header -->
                <div class="sidebar-header">
                    <a href="index.html" class="sidebar-logo">
                        <img src="assets/images/logo.jpg" alt="Coast to Coast">
                        <span class="sidebar-logo-text">Coast to Coast</span>
                    </a>
                    <button class="sidebar-toggle" id="sidebarToggle" title="Toggle Sidebar">
                        <i class="fas fa-chevron-left"></i>
                    </button>
                </div>

                <!-- User Section -->
                ${this.currentUser ? this.getLoggedInUserSection() : this.getGuestUserSection()}

                <!-- Navigation -->
                <nav class="sidebar-nav">
                    <!-- Main Navigation Section -->
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Navigation</div>
                        <ul class="sidebar-menu">
                            <li class="sidebar-menu-item">
                                <a href="index.html" class="sidebar-menu-link" data-tooltip="Home" data-page="index">
                                    <span class="sidebar-menu-icon"><i class="fas fa-home"></i></span>
                                    <span class="sidebar-menu-text">Home</span>
                                </a>
                            </li>
                            <li class="sidebar-menu-item">
                                <a href="index.html#flights" class="sidebar-menu-link" data-tooltip="Flights" data-page="flights">
                                    <span class="sidebar-menu-icon"><i class="fas fa-plane"></i></span>
                                    <span class="sidebar-menu-text">Search Flights</span>
                                </a>
                            </li>
                            <li class="sidebar-menu-item">
                                <a href="index.html#hotels" class="sidebar-menu-link" data-tooltip="Hotels" data-page="hotels">
                                    <span class="sidebar-menu-icon"><i class="fas fa-hotel"></i></span>
                                    <span class="sidebar-menu-text">Search Hotels</span>
                                </a>
                            </li>
                        </ul>
                    </div>

                    <!-- Results Section -->
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Booking</div>
                        <ul class="sidebar-menu">
                            <li class="sidebar-menu-item">
                                <a href="flight-results.html" class="sidebar-menu-link" data-tooltip="Flight Results" data-page="flight-results">
                                    <span class="sidebar-menu-icon"><i class="fas fa-list-ul"></i></span>
                                    <span class="sidebar-menu-text">Flight Results</span>
                                </a>
                            </li>
                            <li class="sidebar-menu-item">
                                <a href="hotel-results.html" class="sidebar-menu-link" data-tooltip="Hotel Results" data-page="hotel-results">
                                    <span class="sidebar-menu-icon"><i class="fas fa-bed"></i></span>
                                    <span class="sidebar-menu-text">Hotel Results</span>
                                </a>
                            </li>
                        </ul>
                    </div>

                    <!-- My Account Section (only for logged in users) -->
                    ${this.currentUser ? `
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">My Account</div>
                        <ul class="sidebar-menu">
                            <li class="sidebar-menu-item">
                                <a href="my-bookings.html" class="sidebar-menu-link" data-tooltip="My Bookings" data-page="my-bookings">
                                    <span class="sidebar-menu-icon"><i class="fas fa-calendar-check"></i></span>
                                    <span class="sidebar-menu-text">My Bookings</span>
                                    <span class="sidebar-menu-badge" id="bookingsCount" style="display: none;">0</span>
                                </a>
                            </li>
                            <li class="sidebar-menu-item">
                                <a href="wishlist.html" class="sidebar-menu-link" data-tooltip="Wishlist" data-page="wishlist">
                                    <span class="sidebar-menu-icon"><i class="fas fa-heart"></i></span>
                                    <span class="sidebar-menu-text">Wishlist</span>
                                </a>
                            </li>
                            <li class="sidebar-menu-item">
                                <a href="my-profile.html" class="sidebar-menu-link" data-tooltip="Profile" data-page="my-profile">
                                    <span class="sidebar-menu-icon"><i class="fas fa-user-cog"></i></span>
                                    <span class="sidebar-menu-text">Profile Settings</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                    ` : ''}

                    <!-- Deals Section -->
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Offers</div>
                        <ul class="sidebar-menu">
                            <li class="sidebar-menu-item">
                                <a href="index.html#deals" class="sidebar-menu-link" data-tooltip="Deals" data-page="deals">
                                    <span class="sidebar-menu-icon"><i class="fas fa-tags"></i></span>
                                    <span class="sidebar-menu-text">Special Deals</span>
                                    <span class="sidebar-menu-badge">New</span>
                                </a>
                            </li>
                        </ul>
                    </div>

                    <!-- Support Section -->
                    <div class="sidebar-section">
                        <div class="sidebar-section-title">Help</div>
                        <ul class="sidebar-menu">
                            <li class="sidebar-menu-item">
                                <a href="support.html" class="sidebar-menu-link" data-tooltip="Support" data-page="support">
                                    <span class="sidebar-menu-icon"><i class="fas fa-headset"></i></span>
                                    <span class="sidebar-menu-text">Support</span>
                                </a>
                            </li>
                            <li class="sidebar-menu-item">
                                <a href="faqs.html" class="sidebar-menu-link" data-tooltip="FAQs" data-page="faqs">
                                    <span class="sidebar-menu-icon"><i class="fas fa-question-circle"></i></span>
                                    <span class="sidebar-menu-text">FAQs</span>
                                </a>
                            </li>
                        </ul>
                    </div>
                </nav>

                <!-- Quick Actions -->
                <div class="sidebar-quick-actions">
                    <div class="quick-search-box">
                        <a href="index.html#flights" class="quick-search-btn flights">
                            <i class="fas fa-plane"></i>
                            <span>Flights</span>
                        </a>
                        <a href="index.html#hotels" class="quick-search-btn hotels">
                            <i class="fas fa-hotel"></i>
                            <span>Hotels</span>
                        </a>
                    </div>
                </div>

                <!-- Footer -->
                <div class="sidebar-footer">
                    <div class="sidebar-footer-links">
                        <a href="terms.html" class="sidebar-footer-link">Terms</a>
                        <a href="privacy-policy.html" class="sidebar-footer-link">Privacy</a>
                        <a href="about.html" class="sidebar-footer-link">About</a>
                    </div>
                    <div class="sidebar-copyright">© 2026 Coast to Coast</div>
                </div>
            </aside>

            <!-- Mobile Toggle Button -->
            <button class="mobile-sidebar-toggle" id="mobileSidebarToggle">
                <i class="fas fa-bars"></i>
            </button>
        `;

        // Wrap existing content
        const body = document.body;
        const existingContent = body.innerHTML;

        // Only wrap if not already wrapped
        if (!document.querySelector('.customer-sidebar')) {
            body.innerHTML = sidebarHTML + `<div class="main-content-wrapper" id="mainContentWrapper">${existingContent}</div>`;
        }
    }

    /**
     * Attach event listeners
     */
    attachEventListeners() {
        // Sidebar toggle (desktop)
        const sidebarToggle = document.getElementById('sidebarToggle');
        if (sidebarToggle) {
            sidebarToggle.addEventListener('click', () => this.toggleSidebar());
        }

        // Mobile toggle button
        const mobileToggle = document.getElementById('mobileSidebarToggle');
        if (mobileToggle) {
            mobileToggle.addEventListener('click', () => this.toggleMobileSidebar());
        }

        // Overlay click to close
        const overlay = document.getElementById('sidebarOverlay');
        if (overlay) {
            overlay.addEventListener('click', () => this.closeMobileSidebar());
        }

        // Close sidebar on link click (mobile)
        const sidebarLinks = document.querySelectorAll('.sidebar-menu-link');
        sidebarLinks.forEach(link => {
            link.addEventListener('click', () => {
                if (window.innerWidth <= 992) {
                    this.closeMobileSidebar();
                }
            });
        });

        // Handle window resize
        window.addEventListener('resize', () => {
            if (window.innerWidth > 992) {
                this.closeMobileSidebar();
            }
        });
    }

    /**
     * Toggle sidebar collapsed state (desktop)
     */
    toggleSidebar() {
        this.isCollapsed = !this.isCollapsed;
        const sidebar = document.getElementById('customerSidebar');
        if (sidebar) {
            sidebar.classList.toggle('collapsed', this.isCollapsed);
        }
        localStorage.setItem('sidebar_collapsed', this.isCollapsed);
    }

    /**
     * Toggle mobile sidebar
     */
    toggleMobileSidebar() {
        this.isMobileOpen = !this.isMobileOpen;
        const sidebar = document.getElementById('customerSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const mobileBtn = document.getElementById('mobileSidebarToggle');

        if (sidebar) {
            sidebar.classList.toggle('mobile-open', this.isMobileOpen);
        }
        if (overlay) {
            overlay.classList.toggle('active', this.isMobileOpen);
        }
        if (mobileBtn) {
            mobileBtn.innerHTML = this.isMobileOpen
                ? '<i class="fas fa-times"></i>'
                : '<i class="fas fa-bars"></i>';
        }
    }

    /**
     * Close mobile sidebar
     */
    closeMobileSidebar() {
        this.isMobileOpen = false;
        const sidebar = document.getElementById('customerSidebar');
        const overlay = document.getElementById('sidebarOverlay');
        const mobileBtn = document.getElementById('mobileSidebarToggle');

        if (sidebar) {
            sidebar.classList.remove('mobile-open');
        }
        if (overlay) {
            overlay.classList.remove('active');
        }
        if (mobileBtn) {
            mobileBtn.innerHTML = '<i class="fas fa-bars"></i>';
        }
    }

    /**
     * Update active link based on current page
     */
    updateActiveLink() {
        const currentPage = window.location.pathname.split('/').pop().replace('.html', '') || 'index';
        const links = document.querySelectorAll('.sidebar-menu-link');

        links.forEach(link => {
            const linkPage = link.getAttribute('data-page');
            if (linkPage && currentPage.includes(linkPage)) {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    }

    /**
     * Update bookings badge count
     */
    updateBookingsCount(count) {
        const badge = document.getElementById('bookingsCount');
        if (badge) {
            if (count > 0) {
                badge.textContent = count > 99 ? '99+' : count;
                badge.style.display = 'inline-block';
            } else {
                badge.style.display = 'none';
            }
        }
    }
}

// Initialize sidebar when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    // Initialize sidebar on all customer-facing pages
    const currentPath = window.location.pathname;
    const pageName = currentPath.split('/').pop() || 'index.html';

    // Pages that should show the sidebar (NOT the main landing page)
    const sidebarPages = [
        'flight-results',
        'hotel-results',
        'hotel-details',
        'hotel-booking',
        'booking-confirmation',
        'my-bookings',
        'wishlist',
        'my-profile',
        'support'
    ];

    // Check if current page should show sidebar (strict match, NOT homepage)
    const shouldShowSidebar = sidebarPages.some(page =>
        pageName.includes(page) && pageName !== 'index.html' && pageName !== ''
    );

    if (shouldShowSidebar) {
        const sidebar = new CustomerSidebar();
        sidebar.init();

        // Make sidebar available globally
        window.customerSidebar = sidebar;
    }
});
