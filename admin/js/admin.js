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
                    <td><button class="btn-pdf"><i class="fas fa-file-pdf"></i></button></td>
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
                    <td style="padding: 1rem;"><i class="fas fa-file-download" style="color: #ef4444; cursor: pointer; font-size: 1.2rem;"></i></td>
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
                        { name: 'Incomplete Booking', icon: 'fa-exclamation-triangle', href: 'bookings.html?status=created' }
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
                        { name: 'Block Booking Markup', icon: 'fa-ban', href: 'block-markup.html' },
                        { name: 'Manage Coupons', icon: 'fa-tags', href: 'coupons.html' },
                        { name: 'B2B Markup', icon: 'fa-user-tie', href: 'b2b-markup.html' },
                        { name: 'Convenience Charge', icon: 'fa-hand-holding-usd', href: 'convenience-charge.html' },
                        { name: 'Cancellation Charge', icon: 'fa-times-circle', href: 'cancellation-charge.html' }
                    ]
                },
                { 
                    name: 'MY Account', 
                    icon: 'fa-user-circle', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('account_submenu_open') === 'true',
                    subItems: [
                        { name: 'Statement', icon: 'fa-file-invoice-dollar', href: 'statement.html' },
                        { name: 'My Invoices', icon: 'fa-file-invoice', href: 'invoices.html' },
                        { name: 'Credit Notes', icon: 'fa-clipboard-list', href: 'credit-notes.html' },
                        { name: 'Debit Notes', icon: 'fa-clipboard-list', href: 'debit-notes.html' },
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
                { 
                    name: 'Utility', 
                    icon: 'fa-tools', 
                    href: '#',
                    hasSub: true,
                    isOpen: localStorage.getItem('utility_submenu_open') === 'true',
                    subItems: [
                        { name: 'Meeting Slots', icon: 'fa-calendar-alt', href: 'meeting-slots.html' },
                        { name: 'Generate Invoice', icon: 'fa-file-invoice', href: 'generate-invoice.html' }
                    ]
                },
                { name: 'Customers', icon: 'fa-users', href: 'customers.html' },
                { name: 'Activity Logs', icon: 'fa-history', href: 'activity-logs.html' }
            ]
        },
        {
            section: 'System', items: [
                { name: 'Settings', icon: 'fa-cog', href: 'settings.html' },
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
                        if (item.name === 'MY Account') storageKey = 'account_submenu_open';
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
// Notifications
// ========================================
function showNotification(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `admin-notification ${type}`;
    notification.innerHTML = `
        <i class="fas ${getNotificationIcon(type)}"></i>
        <span>${message}</span>
        <button onclick="this.parentElement.remove()">&times;</button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 80px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        display: flex;
        align-items: center;
        gap: 10px;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
        z-index: 9999;
        animation: slideIn 0.3s ease;
    `;

    document.body.appendChild(notification);

    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
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

function getNotificationColor(type) {
    const colors = {
        success: '#10b981',
        error: '#ef4444',
        warning: '#f59e0b',
        info: '#0e64a6'
    };
    return colors[type] || colors.info;
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

    // Add animation keyframes
    const style = document.createElement('style');
    style.textContent = `
        @keyframes slideIn {
            from { transform: translateX(100%); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        @keyframes slideOut {
            from { transform: translateX(0); opacity: 1; }
            to { transform: translateX(100%); opacity: 0; }
        }
    `;
    document.head.appendChild(style);
});
