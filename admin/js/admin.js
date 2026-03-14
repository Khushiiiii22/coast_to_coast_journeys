/**
 * C2C Journeys - Admin Panel JavaScript
 */

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
});

// ========================================
// Sidebar Management
// ========================================
function initSidebar() {
    const sidebar = document.getElementById('adminSidebar');
    if (!sidebar) return;

    const currentPath = window.location.pathname.split('/').pop() || 'dashboard.html';

    const navItems = [
        {
            section: 'Main', items: [
                { name: 'Dashboard', icon: 'fa-home', href: 'dashboard.html' },
                { name: 'Hotel Bookings', icon: 'fa-calendar-check', href: 'bookings.html' },
                { name: 'Flight Bookings', icon: 'fa-plane', href: 'flights.html' }
            ]
        },
        {
            section: 'Finance', items: [
                { name: 'Payments', icon: 'fa-credit-card', href: 'payments.html' },
                { name: 'Invoices', icon: 'fa-file-invoice', href: 'invoices.html' },
                { name: 'Refunds', icon: 'fa-undo', href: 'refunds.html' }
            ]
        },
        {
            section: 'Operations', items: [
                { name: 'Markup Tool', icon: 'fa-percentage', href: 'markup.html' },
                { name: 'Suppliers', icon: 'fa-handshake', href: 'suppliers.html' },
                { name: 'Customers', icon: 'fa-users', href: 'customers.html' }
            ]
        },
        {
            section: 'Analytics', items: [
                { name: 'Reports', icon: 'fa-chart-bar', href: 'reports.html' }
            ]
        },
        {
            section: 'System', items: [
                { name: 'Admin Users', icon: 'fa-user-shield', href: 'users.html' },
                { name: 'Settings', icon: 'fa-cog', href: 'settings.html' },
                { name: 'Activity Logs', icon: 'fa-history', href: 'activity-logs.html' },
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
                ${section.items.map(item => `
                    <a href="${item.href}" 
                       class="nav-item ${currentPath === item.href ? 'active' : ''}" 
                       ${item.onclick ? `onclick="${item.onclick}"` : ''}
                       ${item.style ? `style="${item.style}"` : ''}>
                        <i class="fas ${item.icon}"></i>
                        <span>${item.name}</span>
                    </a>
                `).join('')}
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
        const result = await response.json();

        if (!response.ok) {
            throw new Error(result.error || 'Request failed');
        }

        return result;
    } catch (error) {
        console.error('API Error:', error);
        showNotification(error.message, 'error');
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
