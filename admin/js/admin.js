/**
 * C2C Journeys - Admin Panel JavaScript
 */

/* ========================================
   Account & Statement Logic
======================================== */
async function loadLedger() {
    const tableBody = document.getElementById('statementBody');
    if (!tableBody) return;

    try {
        const result = await apiRequest('/account/ledger');

        if (result.status === 'success') {
            const data = result.data;
            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="9" class="empty-row" style="text-align: center; padding: 2rem;">No Transactions Found</td></tr>';
                return;
            }

            tableBody.innerHTML = data.map(item => `
                <tr>
                    <td>${new Date(item.date).toLocaleDateString()} ${new Date(item.date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</td>
                    <td>
                        <div class="txn-id-box">Txn. Id: ${item.txn_id}</div>
                        <div>Ref Id: <a href="#" class="booking-id-link">${item.order_id}</a></div>
                        <span class="pg-badge">PAYMENT</span>
                    </td>
                    <td>
                        <div class="description-box">
                            <b>${item.description}</b><br>
                            Status: <b style="text-transform: uppercase;">${item.status}</b><br>
                            <span class="remark-pill">automated entry</span>
                        </div>
                    </td>
                    <td style="text-align: center;"><i class="fas fa-bed fa-lg"></i></td>
                    <td class="na-text">---</td>
                    <td class="val-credit">${item.credit > 0 ? '₹' + item.credit.toLocaleString() : ''}</td>
                    <td class="val-debit">${item.debit > 0 ? '₹' + item.debit.toLocaleString() : ''}</td>
                    <td>₹ ${item.amount.toLocaleString()}</td>
                    <td>₹ ${item.amount.toLocaleString()}</td>
                </tr>
            `).join('');

            // Update balance if element exists
            const balanceEl = document.querySelector('.balance-amount');
            if (balanceEl && result.balance) {
                balanceEl.textContent = `₹ ${result.balance.toLocaleString()}`;
            }
        }
    } catch (error) {
        console.error('Error loading ledger:', error);
    }
}

async function loadInvoices() {
    const tableBody = document.getElementById('invoiceBody');
    if (!tableBody) return;

    try {
        const result = await apiRequest('/account/invoices');

        if (result.status === 'success') {
            const data = result.data;
            window.allInvoices = data;
            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="12" class="empty-row" style="text-align: center; padding: 2rem; color: #64748b;">No Invoices Found</td></tr>';
                return;
            }

            tableBody.innerHTML = data.map(item => `
                <tr>
                    <td>${item.lead_pax.split('@')[0].toUpperCase()}</td>
                    <td>${item.lead_email}</td>
                    <td>${item.lead_phone}</td>
                    <td><a href="#" class="pnr-link">${item.ref_no}</a></td>
                    <td>${item.hotel_name}</td>
                    <td>${item.destination}</td>
                    <td>${item.check_in}</td>
                    <td><span class="status-confirm">${item.status}</span></td>
                    <td>${item.markup}</td>
                    <td>0</td>
                    <td>₹${item.total_fare.toLocaleString()}</td>
                    <td><button class="btn-pdf" onclick="downloadInvoice('${item.invoice_id}')"><i class="fas fa-file-pdf"></i></button></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading invoices:', error);
    }
}

async function loadHotelEnquiries() {
    const tableBody = document.getElementById('hotelEnquiryBody');
    if (!tableBody) return;

    try {
        const result = await apiRequest('/queries/hotel');

        if (result.status === 'success') {
            const data = result.data;
            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="9" class="empty-row" style="text-align: center; padding: 2rem;">No Enquiries Found</td></tr>';
                return;
            }

            tableBody.innerHTML = data.map((item, idx) => `
                <tr>
                    <td>${idx + 1}.</td>
                    <td><span class="col-link">${item.name}</span></td>
                    <td>
                        <div class="col-email">${item.email}</div>
                        <div>${item.phone || '---'}</div>
                    </td>
                    <td><b>${item.destination || 'N/A'}</b></td>
                    <td>${item.travel_date ? new Date(item.travel_date).toLocaleDateString() : '---'}</td>
                    <td>---</td>
                    <td><span class="badge-rooms">${item.travelers || '---'}</span></td>
                    <td style="max-width: 250px;">${item.special_requirements || '---'}</td>
                    <td>${new Date(item.created_at).toLocaleDateString()}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading hotel enquiries:', error);
    }
}

async function loadContactEnquiries() {
    const tableBody = document.getElementById('contactEnquiryBody');
    if (!tableBody) return;

    try {
        const result = await apiRequest('/queries/contact');

        if (result.status === 'success') {
            const data = result.data;
            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="7" class="empty-row" style="text-align: center; padding: 2rem;">No Messages Found</td></tr>';
                return;
            }

            tableBody.innerHTML = data.map((item, idx) => `
                <tr>
                    <td>${idx + 1}.</td>
                    <td><span class="col-link">${item.name}</span></td>
                    <td><span class="col-email">${item.email}</span></td>
                    <td>${item.phone || '---'}</td>
                    <td class="col-message">${item.message}</td>
                    <td>1</td>
                    <td>${new Date(item.created_at).toLocaleString()}</td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading contact enquiries:', error);
    }
}

async function loadInvoicesList() {
    const tableBody = document.getElementById('manualInvoiceBody');
    if (!tableBody) return;

    try {
        const result = await apiRequest('/account/invoices');

        if (result.status === 'success') {
            const data = result.data;
            if (data.length === 0) {
                tableBody.innerHTML = '<tr><td colspan="5" class="empty-row" style="text-align: center; padding: 2rem;">No Invoices Found</td></tr>';
                return;
            }

            tableBody.innerHTML = data.map((item, idx) => `
                <tr style="border-bottom: 1px solid #f1f5f9;">
                    <td style="padding: 1rem;">${idx + 1}</td>
                    <td style="padding: 1rem;">${item.invoice_id}</td>
                    <td style="padding: 1rem;">${item.lead_pax}</td>
                    <td style="padding: 1rem;">₹ ${parseFloat(item.total_fare).toLocaleString()}</td>
                    <td style="padding: 1rem;"><i class="fas fa-file-download" style="color: #ef4444; cursor: pointer; font-size: 1.2rem;" onclick="downloadInvoice('${item.invoice_id}')"></i></td>
                </tr>
            `).join('');
        }
    } catch (error) {
        console.error('Error loading invoices list:', error);
    }
}

// Trigger loading on page load
document.addEventListener('DOMContentLoaded', () => {
    loadLedger();
    loadInvoices();
    loadHotelEnquiries();
    loadContactEnquiries();
    loadInvoicesList();
});

// ========================================
// Sidebar Toggle
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.getElementById('adminSidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            sidebar.classList.toggle('collapsed');

            // Save preference
            localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
        });

        // Restore preference
        if (localStorage.getItem('sidebarCollapsed') === 'true') {
            sidebar.classList.add('collapsed');
        }
    }

    // Mobile sidebar
    if (window.innerWidth <= 1024) {
        sidebarToggle?.addEventListener('click', function () {
            sidebar.classList.toggle('open');
        });
    }

    // Initialize dynamic components
    initSidebar();
    restoreSidebarScroll();
});

// ========================================
// Sidebar Management
// ========================================
function initSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    if (!sidebar) return;

    // Save sidebar scroll position before re-rendering
    const scrollPos = sidebar.querySelector('.sidebar-nav')?.scrollTop || 0;

    const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';

    const navItems = [
        {
            section: 'Main', items: [
                { name: 'Dashboard', icon: 'fa-home', href: 'dashboard.html' },
                { 
                    name: 'All Bookings', 
                    icon: 'fa-briefcase', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('bookings_submenu_open') === 'true',
                    subItems: [
                        { name: 'Hotel', icon: 'fa-bed', href: 'bookings.html' },
                        { name: 'Flight', icon: 'fa-plane', href: 'flights.html' },
                        { name: 'Incomplete', icon: 'fa-exclamation-triangle', href: 'bookings.html?status=created' }
                    ]
                }
            ]
        },
        {
            section: 'Operations', items: [
                { 
                    name: 'Manage Markup', 
                    icon: 'fa-percentage', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('markup_submenu_open') === 'true',
                    subItems: [
                        { name: 'Currency Setting', icon: 'fa-money-bill-wave', href: 'markup.html' },
                        { name: 'Block Booking Markup', icon: 'fa-file-invoice', href: 'block-markup.html' },
                        { name: 'B2C Markup', icon: 'fa-money-bill-alt', href: 'b2c-markup.html' },
                        { name: 'Convenience Charge', icon: 'fa-credit-card', href: 'convenience-charge.html' },
                        { name: 'Cancellation Charge', icon: 'fa-times-circle', href: 'cancellation-charge.html' }
                    ]
                },
                { 
                    name: 'Finance', 
                    icon: 'fa-file-invoice-dollar', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('account_submenu_open') === 'true',
                    subItems: [
                        { name: 'Payments', icon: 'fa-credit-card', href: 'payments.html' },
                        { name: 'Invoices', icon: 'fa-file-invoice', href: 'invoices.html' },
                        { name: 'Refunds', icon: 'fa-undo', href: 'refunds.html' }
                    ]
                },
                { 
                    name: 'Queries', 
                    icon: 'fa-question-circle', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('queries_submenu_open') === 'true',
                    subItems: [
                        { name: 'Hotel Enquiry', icon: 'fa-bed', href: 'hotel-enquiry.html' },
                        { name: 'Contact-Us Enquiry', icon: 'fa-envelope', href: 'contact-enquiry.html' }
                    ]
                },
                { name: 'Suppliers', icon: 'fa-handshake', href: 'suppliers.html' },
                { name: 'Customers', icon: 'fa-users', href: 'customers.html' },
                { name: 'Activity Logs', icon: 'fa-history', href: 'activity-logs.html' }
            ]
        },
        {
            section: 'System', items: [
                { name: 'Admin Users', icon: 'fa-user-shield', href: 'users.html' },
                { 
                    name: 'Website Setting', 
                    icon: 'fa-cog', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('website_setting_submenu_open') === 'true',
                    subItems: [
                        { name: 'General Setting', icon: 'fa-sliders-h', href: 'general-settings.html' }
                    ]
                },
                { name: 'Logout', icon: 'fa-sign-out-alt', href: '#', onclick: 'logout(); return false;', style: 'color: #ef4444;' }
            ]
        }
    ];

    let html = `
        <div class="sidebar-header">
            <div class="sidebar-logo">C</div>
            <span class="sidebar-brand">CTC Admin</span>
        </div>
        <nav class="sidebar-nav">
    `;

    navItems.forEach(section => {
        html += `
            <div class="nav-section">
                <span class="nav-section-title">${section.section}</span>
                ${section.items.map(item => {
                    const isActive = currentPath === item.href || (item.subItems && item.subItems.some(sub => currentPath === sub.href));
                    
                    if (item.hasSub) {
                        let storageKey = 'bookings_submenu_open';
                        if (item.name === 'Manage Markup') storageKey = 'markup_submenu_open';
                        if (item.name === 'Finance') storageKey = 'account_submenu_open';
                        if (item.name === 'Website Setting') storageKey = 'website_setting_submenu_open';
                        if (item.name === 'Queries') storageKey = 'queries_submenu_open';
                        if (item.name === 'Utility') storageKey = 'utility_submenu_open';
                        
                        return `
                            <div class="nav-item-dropdown ${item.isOpen ? 'open' : ''}">
                                <a href="#" class="nav-item ${isActive ? 'active' : ''}" onclick="toggleSubMenu(event, '${storageKey}')">
                                    <i class="fas ${item.icon}"></i>
                                    <span>${item.name}</span>
                                    <i class="fas fa-chevron-down dropdown-arrow"></i>
                                </a>
                                <div class="nav-sub-items">
                                    ${item.subItems.map(sub => `
                                        <a href="${sub.href}" class="nav-sub-item ${currentPath === sub.href ? 'active' : ''}">
                                            <i class="fas ${sub.icon}"></i>
                                            <span>${sub.name}</span>
                                        </a>
                                    `).join('')}
                                </div>
                            </div>
                        `;
                    }
                    
                    return `
                        <a href="${item.href}" 
                           class="nav-item ${currentPath === item.href ? 'active' : ''}" 
                           ${item.onclick ? `onclick="${item.onclick}"` : ''}
                           ${item.style ? `style="${item.style}"` : ''}>
                            <i class="fas ${item.icon}"></i>
                            <span>${item.name}</span>
                        </a>
                    `;
                }).join('')}
            </div>
        `;
    });

    html += `
        </nav>
        <div class="sidebar-footer">
            <div class="admin-profile">
                <div class="admin-avatar">SA</div>
                <div class="admin-info">
                    <div class="admin-name">Super Admin</div>
                    <div class="admin-role">Administrator</div>
                </div>
            </div>
        </div>
    `;

    sidebar.innerHTML = html;

    // Attach scroll listener to preserve position
    const nav = sidebar.querySelector('.sidebar-nav');
    if (nav) {
        nav.addEventListener('scroll', () => {
            localStorage.setItem('admin_sidebar_scroll', nav.scrollTop);
        });
    }

    // Scroll active item into view
    setTimeout(() => {
        const activeItem = sidebar.querySelector('.nav-item.active');
        if (activeItem) {
            activeItem.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
    }, 100);
}

function toggleSubMenu(event, storageKey) {
    event.preventDefault();
    const dropdown = event.currentTarget.closest('.nav-item-dropdown');
    const isOpen = dropdown.classList.toggle('open');
    localStorage.setItem(storageKey, isOpen);
}

function restoreSidebarScroll() {
    const nav = document.querySelector('.sidebar-nav');
    if (nav) {
        const scrollPos = localStorage.getItem('admin_sidebar_scroll');
        if (scrollPos) {
            nav.scrollTop = parseInt(scrollPos);
        }
    }
}

// ========================================
// Notifications System
// ========================================
let notificationsData = [];
let notificationDropdownOpen = false;

// Initialize notification bell on all admin pages
document.addEventListener('DOMContentLoaded', function() {
    initNotificationBell();
});

function initNotificationBell() {
    // Find the bell button (look for the fa-bell icon)
    const bellIcon = document.querySelector('.header-btn .fa-bell');
    if (!bellIcon) return;

    const bellBtn = bellIcon.closest('.header-btn');
    if (!bellBtn) return;

    // Wrap the bell button in a notification-wrapper for positioning
    const wrapper = document.createElement('div');
    wrapper.className = 'notification-wrapper';
    bellBtn.parentNode.insertBefore(wrapper, bellBtn);
    wrapper.appendChild(bellBtn);

    // Update the badge to show count
    let badge = bellBtn.querySelector('.notification-badge');
    if (!badge) {
        badge = document.createElement('span');
        badge.className = 'notification-badge hidden';
        bellBtn.appendChild(badge);
    }
    badge.className = 'notification-badge hidden';
    badge.textContent = '';

    // Create dropdown panel
    const dropdown = document.createElement('div');
    dropdown.className = 'notification-dropdown';
    dropdown.id = 'notificationDropdown';
    dropdown.innerHTML = `
        <div class="notif-header">
            <div class="notif-header-title">
                Notifications <span class="count-badge" id="notifCountBadge">0</span>
            </div>
            <button class="notif-mark-read" onclick="markAllNotificationsRead(event)">
                <i class="fas fa-check-double"></i> Mark all read
            </button>
        </div>
        <div class="notif-list" id="notifList">
            <div class="notif-empty">
                <i class="fas fa-spinner fa-spin"></i>
                <p>Loading...</p>
            </div>
        </div>
        <div class="notif-footer">
            <a href="activity-logs.html">View All Activity <i class="fas fa-arrow-right"></i></a>
        </div>
    `;
    wrapper.appendChild(dropdown);

    // Bell click handler
    bellBtn.addEventListener('click', function(e) {
        e.stopPropagation();
        toggleNotificationDropdown();
    });

    // Close on outside click
    document.addEventListener('click', function(e) {
        if (notificationDropdownOpen && !wrapper.contains(e.target)) {
            closeNotificationDropdown();
        }
    });

    // Load notifications
    loadNotifications();
}

function toggleNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (!dropdown) return;

    if (notificationDropdownOpen) {
        closeNotificationDropdown();
    } else {
        dropdown.classList.add('open');
        notificationDropdownOpen = true;
        loadNotifications();
    }
}

function closeNotificationDropdown() {
    const dropdown = document.getElementById('notificationDropdown');
    if (dropdown) {
        dropdown.classList.remove('open');
        notificationDropdownOpen = false;
    }
}

async function loadNotifications() {
    const list = document.getElementById('notifList');
    if (!list) return;

    try {
        const result = await apiRequest('/notifications?limit=20');

        if (!result || !result.success) {
            renderNotifEmpty(list, 'Failed to load notifications');
            return;
        }

        notificationsData = result.data || [];
        renderNotifications(notificationsData);
        updateNotificationBadge(notificationsData);

    } catch (error) {
        console.error('Error loading notifications:', error);
        renderNotifEmpty(list, 'Could not load notifications');
    }
}

function renderNotifications(notifications) {
    const list = document.getElementById('notifList');
    if (!list) return;

    const readIds = getReadNotificationIds();

    if (!notifications || notifications.length === 0) {
        renderNotifEmpty(list, 'No new notifications');
        return;
    }

    const countBadge = document.getElementById('notifCountBadge');
    const unreadCount = notifications.filter(n => !readIds.includes(n.id)).length;
    if (countBadge) countBadge.textContent = unreadCount;

    list.innerHTML = notifications.map(n => {
        const isRead = readIds.includes(n.id);
        const timeAgo = getTimeAgo(n.time);

        return `
            <a href="${n.link}" class="notif-item ${isRead ? '' : 'unread'}" data-notif-id="${n.id}">
                <div class="notif-icon ${n.type}">
                    <i class="fas ${n.icon}"></i>
                </div>
                <div class="notif-content">
                    <div class="notif-title">${n.title}</div>
                    <div class="notif-message">${n.message}</div>
                    <div class="notif-time">
                        <i class="fas fa-clock"></i> ${timeAgo}
                    </div>
                </div>
            </a>
        `;
    }).join('');
}

function renderNotifEmpty(container, message) {
    container.innerHTML = `
        <div class="notif-empty">
            <i class="fas fa-bell-slash"></i>
            <p>${message}</p>
            <span>You're all caught up!</span>
        </div>
    `;
}

function updateNotificationBadge(notifications) {
    const badge = document.querySelector('.notification-badge');
    if (!badge) return;

    const readIds = getReadNotificationIds();
    const unreadCount = notifications.filter(n => !readIds.includes(n.id)).length;

    if (unreadCount > 0) {
        badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

function markAllNotificationsRead(event) {
    if (event) event.stopPropagation();

    const allIds = notificationsData.map(n => n.id);
    localStorage.setItem('admin_read_notifications', JSON.stringify(allIds));

    // Re-render
    renderNotifications(notificationsData);
    updateNotificationBadge(notificationsData);

    showNotification('All notifications marked as read', 'success');
}

function getReadNotificationIds() {
    try {
        return JSON.parse(localStorage.getItem('admin_read_notifications') || '[]');
    } catch {
        return [];
    }
}

function getTimeAgo(dateString) {
    if (!dateString) return 'Unknown';

    const now = new Date();
    const date = new Date(dateString);
    const diffMs = now - date;
    const diffMins = Math.floor(diffMs / 60000);
    const diffHours = Math.floor(diffMs / 3600000);
    const diffDays = Math.floor(diffMs / 86400000);

    if (diffMins < 1) return 'Just now';
    if (diffMins < 60) return `${diffMins}m ago`;
    if (diffHours < 24) return `${diffHours}h ago`;
    if (diffDays < 7) return `${diffDays}d ago`;
    return date.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' });
}

// ========================================
// Toast Notifications
// ========================================
let toastStack = 0;

function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove(); toastStack--;">&times;</button>
    `;

    // Stack multiple toasts
    const topOffset = 80 + (toastStack * 70);
    notification.style.top = `${topOffset}px`;
    toastStack++;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease forwards';
        setTimeout(() => {
            notification.remove();
            toastStack--;
        }, 300);
    }, 5000);
}

function getNotificationIcon(type) {
    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };
    return icons[type] || icons.info;
}


// ========================================
// API Helpers
// ========================================
const API_BASE = '/api/admin';

async function apiRequest(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${getAuthToken()}`
        }
    };

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        
        if (response.status === 401) {
            localStorage.removeItem('admin_token');
            localStorage.removeItem('admin_user');
            window.location.href = 'login.html';
            return;
        }

        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        if (error.message !== 'Unexpected token < in JSON at position 0') {
            showNotification(error.message, 'error');
        }
        throw error;
    }
}

// ========================================
// Authentication
// ========================================
function getAuthToken() {
    return localStorage.getItem('admin_token') || '';
}

function setAuthToken(token) {
    localStorage.setItem('admin_token', token);
}

function logout() {
    localStorage.removeItem('admin_token');
    window.location.href = 'login.html';
}

function checkAuth() {
    const token = getAuthToken();
    if (!token && !window.location.href.includes('login.html')) {
        window.location.href = 'login.html';
    }
}

// ========================================
// Data Formatting
// ========================================
function formatCurrency(amount, currency = 'INR') {
    return new Intl.NumberFormat('en-IN', {
        style: 'currency',
        currency: currency,
        minimumFractionDigits: 0,
        maximumFractionDigits: 0
    }).format(amount);
}

function formatDate(dateString) {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric'
    });
}

function formatDateTime(dateString) {
    const date = new Date(dateString);
    return date.toLocaleString('en-IN', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// ========================================
// Table Utilities
// ========================================
function renderTable(tableId, data, columns) {
    const tbody = document.querySelector(`#${tableId} tbody`);
    if (!tbody) return;

    tbody.innerHTML = data.map(row => `
        <tr>
            ${columns.map(col => `<td>${col.render ? col.render(row) : row[col.key]}</td>`).join('')}
        </tr>
    `).join('');
}

function initTableSearch(inputId, tableId) {
    const input = document.getElementById(inputId);
    const table = document.getElementById(tableId);

    if (!input || !table) return;

    input.addEventListener('input', function () {
        const filter = this.value.toLowerCase();
        const rows = table.querySelectorAll('tbody tr');

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    });
}

// ========================================
// Invoice Download
// ========================================
function downloadInvoice(invoiceId) {
    if (!invoiceId) {
        showNotification('Invalid Invoice ID', 'error');
        return;
    }
    
    showNotification('Generating invoice PDF...', 'info');
    
    // Simulate generation delay
    setTimeout(() => {
        // Open a simple printable window
        const printWindow = window.open('', '_blank');
        if (!printWindow) {
            showNotification('Popup blocked! Please allow popups for this site.', 'error');
            return;
        }
        
        printWindow.document.write(`
            <html>
            <head>
                <title>Invoice - ${invoiceId}</title>
                <style>
                    body { font-family: 'Inter', Arial, sans-serif; padding: 40px; color: #1e293b; max-width: 800px; margin: 0 auto; }
                    .header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 40px; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; }
                    .logo { font-size: 24px; font-weight: 800; color: #0e64a6; margin-bottom: 10px; }
                    .invoice-title { font-size: 32px; font-weight: 800; color: #4db6ac; text-transform: uppercase; margin: 0; }
                    .info-grid { display: flex; justify-content: space-between; margin-bottom: 40px; }
                    .info-box { background: #f8fafc; padding: 20px; border-radius: 8px; flex: 1; margin: 0 10px; }
                    .info-box:first-child { margin-left: 0; }
                    .info-box:last-child { margin-right: 0; }
                    h3 { margin-top: 0; color: #64748b; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; }
                    table { width: 100%; border-collapse: collapse; margin-bottom: 40px; }
                    th, td { padding: 15px; text-align: left; border-bottom: 1px solid #e2e8f0; }
                    th { background: #f1f5f9; font-weight: 600; color: #475569; }
                    .total-row td { font-weight: 700; font-size: 18px; border-bottom: none; border-top: 2px solid #cbd5e1; }
                    .footer { text-align: center; color: #94a3b8; font-size: 14px; margin-top: 50px; border-top: 1px solid #e2e8f0; padding-top: 20px; }
                    .print-btn { display: block; width: 200px; margin: 40px auto; padding: 12px 24px; background: #0e64a6; color: white; border: none; border-radius: 6px; font-size: 16px; font-weight: 600; cursor: pointer; text-align: center; text-decoration: none; }
                    @media print {
                        .print-btn { display: none; }
                        body { padding: 0; }
                    }
                </style>
            </head>
            <body>
                <div class="header">
                    <div>
                        <div class="logo">COAST TO COAST JOURNEYS</div>
                        <div>123, Travel Plaza, Connaught Place</div>
                        <div>New Delhi - 110001, India</div>
                        <div>info@ctcjourneys.com</div>
                    </div>
                    <div style="text-align: right;">
                        <h1 class="invoice-title">INVOICE</h1>
                        <div><strong>Invoice #:</strong> ${invoiceId}</div>
                        <div><strong>Date:</strong> ${new Date().toLocaleDateString('en-IN')}</div>
                    </div>
                </div>
                
                <div class="info-grid">
                    <div class="info-box">
                        <h3>Bill To</h3>
                        <div><strong>Customer</strong></div>
                        <div>Standard booking details</div>
                        <div>Phone: N/A</div>
                    </div>
                    <div class="info-box">
                        <h3>Payment Details</h3>
                        <div><strong>Status:</strong> Paid</div>
                        <div><strong>Method:</strong> Online</div>
                    </div>
                </div>
                
                <table>
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Quantity</th>
                            <th>Rate</th>
                            <th>Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Travel Services Booking</td>
                            <td>1</td>
                            <td>Refer to Dashboard</td>
                            <td>As per Booking</td>
                        </tr>
                        <tr class="total-row">
                            <td colspan="3" style="text-align: right;">Total Amount:</td>
                            <td>Valid upon generation</td>
                        </tr>
                    </tbody>
                </table>
                
                <button class="print-btn" onclick="window.print()">Print Invoice</button>
                
                <div class="footer">
                    Thank you for choosing Coast To Coast Journeys!
                </div>
            </body>
            </html>
        `);
        printWindow.document.close();
        
        showNotification('Invoice ready for download/print', 'success');
    }, 800);
}

// ========================================
// Modal Utilities
// ========================================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

// Close modal on outside click
document.addEventListener('click', function (e) {
    if (e.target.classList.contains('modal-overlay')) {
        e.target.closest('.modal').style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});

// ========================================
// Form Validation
// ========================================
function validateForm(formId) {
    const form = document.getElementById(formId);
    if (!form) return false;

    const inputs = form.querySelectorAll('[required]');
    let isValid = true;

    inputs.forEach(input => {
        if (!input.value.trim()) {
            input.classList.add('error');
            isValid = false;
        } else {
            input.classList.remove('error');
        }
    });

    return isValid;
}

// ========================================
// Export Functions
// ========================================
function exportToCSV(data, filename) {
    const headers = Object.keys(data[0]);
    const csv = [
        headers.join(','),
        ...data.map(row => headers.map(h => `"${row[h] || ''}"`).join(','))
    ].join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${filename}.csv`;
    a.click();
    URL.revokeObjectURL(url);
}

// ========================================
// Initialize
// ========================================
document.addEventListener('DOMContentLoaded', function () {
    // Check auth on page load
    checkAuth();
});
