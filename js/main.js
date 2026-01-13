/**
 * Coast to Coast Journeys - Main JavaScript
 * Handles all interactive functionality
 */

// ========================================
// Global Variables & DOM Elements
// ========================================
const DOM = {
    preloader: document.getElementById('preloader'),
    header: document.getElementById('header'),
    mobileMenuToggle: document.getElementById('mobileMenuToggle'),
    navMenu: document.getElementById('navMenu'),

    // Slider
    heroSlides: document.querySelectorAll('.hero-slider .slide'),
    sliderDots: document.getElementById('sliderDots'),
    prevSlide: document.getElementById('prevSlide'),
    nextSlide: document.getElementById('nextSlide'),

    // Search Tabs
    searchTabs: document.querySelectorAll('.search-tab'),
    searchPanels: document.querySelectorAll('.search-panel'),

    // Trip Type
    tripOptions: document.querySelectorAll('.trip-option input'),
    returnDateGroup: document.getElementById('returnDateGroup'),
    returnDate: document.getElementById('returnDate'),

    // Swap Button
    swapBtn: document.getElementById('swapLocations'),
    flightFrom: document.getElementById('flightFrom'),
    flightTo: document.getElementById('flightTo'),

    // Travelers
    travelersSelector: document.getElementById('travelersSelector'),
    travelersDropdown: document.getElementById('travelersDropdown'),
    travelersCount: document.getElementById('travelersCount'),
    travelClass: document.getElementById('travelClass'),
    applyTravelers: document.getElementById('applyTravelers'),

    // Rooms
    roomsSelector: document.getElementById('roomsSelector'),
    roomsDropdown: document.getElementById('roomsDropdown'),
    roomsCount: document.getElementById('roomsCount'),
    guestsCount: document.getElementById('guestsCount'),
    applyRooms: document.getElementById('applyRooms'),

    // Forms
    flightSearchForm: document.getElementById('flightSearchForm'),
    hotelSearchForm: document.getElementById('hotelSearchForm'),
    contactForm: document.getElementById('contactForm'),
    newsletterForm: document.getElementById('newsletterForm'),

    // Modal
    loginBtn: document.getElementById('loginBtn'),
    loginModal: document.getElementById('loginModal'),
    closeModal: document.getElementById('closeModal'),

    // Section Navigation
    sectionDots: document.querySelectorAll('.section-dot'),
    sections: document.querySelectorAll('.fullpage-section')
};

let currentSlide = 0;
let slideInterval;

// ========================================
// Preloader
// ========================================
function hidePreloader() {
    setTimeout(() => {
        DOM.preloader.classList.add('hidden');
        document.body.style.overflow = 'auto';
    }, 1500);
}

// ========================================
// Header Scroll Effect
// ========================================
function handleScroll() {
    if (window.scrollY > 100) {
        DOM.header.classList.add('scrolled');
    } else {
        DOM.header.classList.remove('scrolled');
    }

    // Hide slider controls when scrolled past hero section
    const sliderControls = document.querySelector('.slider-controls');
    const heroSection = document.getElementById('home');
    if (sliderControls && heroSection) {
        const heroBottom = heroSection.offsetTop + heroSection.offsetHeight;
        if (window.scrollY > heroBottom - 200) {
            sliderControls.style.opacity = '0';
            sliderControls.style.visibility = 'hidden';
        } else {
            sliderControls.style.opacity = '1';
            sliderControls.style.visibility = 'visible';
        }
    }

    // Update section navigation
    updateSectionNav();
}

function updateSectionNav() {
    let currentSection = '';

    DOM.sections.forEach(section => {
        const sectionTop = section.offsetTop - 200;
        const sectionHeight = section.offsetHeight;

        if (window.scrollY >= sectionTop && window.scrollY < sectionTop + sectionHeight) {
            currentSection = section.getAttribute('id');
        }
    });

    DOM.sectionDots.forEach(dot => {
        dot.classList.remove('active');
        if (dot.getAttribute('data-section') === currentSection) {
            dot.classList.add('active');
        }
    });
}

// ========================================
// Mobile Menu
// ========================================
function toggleMobileMenu() {
    DOM.navMenu.classList.toggle('active');
    DOM.mobileMenuToggle.classList.toggle('active');
}

// ========================================
// Hero Slider
// ========================================
function initSlider() {
    // Create dots
    DOM.heroSlides.forEach((_, index) => {
        const dot = document.createElement('span');
        dot.classList.add('dot');
        if (index === 0) dot.classList.add('active');
        dot.addEventListener('click', () => goToSlide(index));
        DOM.sliderDots.appendChild(dot);
    });

    // Start auto slide
    startSlideInterval();
}

function goToSlide(index) {
    DOM.heroSlides[currentSlide].classList.remove('active');
    DOM.sliderDots.children[currentSlide].classList.remove('active');

    currentSlide = index;
    if (currentSlide >= DOM.heroSlides.length) currentSlide = 0;
    if (currentSlide < 0) currentSlide = DOM.heroSlides.length - 1;

    DOM.heroSlides[currentSlide].classList.add('active');
    DOM.sliderDots.children[currentSlide].classList.add('active');
}

function nextSlide() {
    goToSlide(currentSlide + 1);
}

function prevSlide() {
    goToSlide(currentSlide - 1);
}

function startSlideInterval() {
    slideInterval = setInterval(nextSlide, 5000);
}

function stopSlideInterval() {
    clearInterval(slideInterval);
}

// ========================================
// Search Tabs
// ========================================
function handleSearchTabs(e) {
    const tab = e.currentTarget;
    const tabName = tab.dataset.tab;

    // Update tabs
    DOM.searchTabs.forEach(t => t.classList.remove('active'));
    tab.classList.add('active');

    // Update panels
    DOM.searchPanels.forEach(panel => {
        panel.classList.remove('active');
        if (panel.id === `${tabName}Panel`) {
            panel.classList.add('active');
        }
    });
}

// ========================================
// Trip Type Handler
// ========================================
function handleTripType(e) {
    const value = e.target.value;

    // Update active class on labels
    DOM.tripOptions.forEach(option => {
        option.closest('.trip-option').classList.remove('active');
    });
    e.target.closest('.trip-option').classList.add('active');

    // Show/hide return date
    if (value === 'oneway') {
        DOM.returnDateGroup.classList.add('disabled');
        DOM.returnDate.disabled = true;
    } else {
        DOM.returnDateGroup.classList.remove('disabled');
        DOM.returnDate.disabled = false;
    }
}

// ========================================
// Swap Locations
// ========================================
function swapLocations() {
    const temp = DOM.flightFrom.value;
    DOM.flightFrom.value = DOM.flightTo.value;
    DOM.flightTo.value = temp;
}

// ========================================
// Travelers Dropdown
// ========================================
function toggleTravelersDropdown(e) {
    e.stopPropagation();
    DOM.travelersDropdown.classList.toggle('show');
    DOM.roomsDropdown.classList.remove('show');
}

function toggleRoomsDropdown(e) {
    e.stopPropagation();
    DOM.roomsDropdown.classList.toggle('show');
    DOM.travelersDropdown.classList.remove('show');
}

function handleCounter(e) {
    const btn = e.target.closest('.counter-btn');
    if (!btn) return;

    const target = btn.dataset.target;
    const input = document.getElementById(target);
    let value = parseInt(input.value);
    const min = parseInt(input.min);
    const max = parseInt(input.max);

    if (btn.classList.contains('plus') && value < max) {
        input.value = value + 1;
    } else if (btn.classList.contains('minus') && value > min) {
        input.value = value - 1;
    }
}

function applyTravelers() {
    const adults = parseInt(document.getElementById('adults').value);
    const children = parseInt(document.getElementById('children').value);
    const infants = parseInt(document.getElementById('infants').value);
    const classSelect = document.getElementById('classSelect');

    const total = adults + children + infants;
    DOM.travelersCount.textContent = `${total} Traveler(s)`;
    DOM.travelClass.textContent = classSelect.options[classSelect.selectedIndex].text;
    DOM.travelersDropdown.classList.remove('show');
}

function applyRooms() {
    const rooms = parseInt(document.getElementById('rooms').value);
    const adults = parseInt(document.getElementById('hotelAdults').value);
    const children = parseInt(document.getElementById('hotelChildren').value);

    const totalGuests = adults + children;
    DOM.roomsCount.textContent = `${rooms} Room${rooms > 1 ? 's' : ''}`;
    DOM.guestsCount.textContent = `${totalGuests} Guest${totalGuests > 1 ? 's' : ''}`;
    DOM.roomsDropdown.classList.remove('show');
}

// ========================================
// Form Submissions
// ========================================
async function handleFlightSearch(e) {
    e.preventDefault();

    const formData = {
        from: DOM.flightFrom.value,
        to: DOM.flightTo.value,
        departDate: document.getElementById('departDate').value,
        returnDate: document.getElementById('returnDate').value,
        travelers: DOM.travelersCount.textContent,
        class: DOM.travelClass.textContent,
        tripType: document.querySelector('input[name="tripType"]:checked').value
    };

    console.log('Flight Search:', formData);

    // Show notification
    showNotification('Searching for flights...', 'info');

    // Save search to database if Supabase is available
    if (window.SupabaseService) {
        await window.SupabaseService.saveFlightSearch(formData);
    }

    // Here you would integrate with flight API
    setTimeout(() => {
        showNotification('Flight search saved! Booking feature coming soon.', 'success');
    }, 1500);
}

async function handleHotelSearch(e) {
    e.preventDefault();

    const formData = {
        destination: document.getElementById('hotelDestination').value,
        checkIn: document.getElementById('checkInDate').value,
        checkOut: document.getElementById('checkOutDate').value,
        rooms: DOM.roomsCount.textContent,
        guests: DOM.guestsCount.textContent
    };

    console.log('Hotel Search:', formData);

    // Show notification
    showNotification('Searching for hotels...', 'info');

    // Save search to database if Supabase is available
    if (window.SupabaseService) {
        await window.SupabaseService.saveHotelSearch(formData);
    }

    // Here you would integrate with hotel API
    setTimeout(() => {
        showNotification('Hotel search saved! Booking feature coming soon.', 'success');
    }, 1500);
}

async function handleContactForm(e) {
    e.preventDefault();

    const formData = {
        name: document.getElementById('contactName').value,
        email: document.getElementById('contactEmail').value,
        phone: document.getElementById('contactPhone').value,
        subject: document.getElementById('contactSubject').value,
        message: document.getElementById('contactMessage').value
    };

    console.log('Contact Form:', formData);
    showNotification('Sending your message...', 'info');

    // Save to database using Supabase
    if (window.SupabaseService) {
        const result = await window.SupabaseService.saveContactMessage(formData);
        if (result.success) {
            showNotification(result.message, 'success');
            e.target.reset();
        } else {
            showNotification(result.message, 'error');
        }
    } else {
        setTimeout(() => {
            showNotification('Message sent successfully! We will get back to you soon.', 'success');
            e.target.reset();
        }, 1500);
    }
}

async function handleNewsletter(e) {
    e.preventDefault();

    const email = e.target.querySelector('input[type="email"]').value;
    console.log('Newsletter subscription:', email);

    showNotification('Subscribing...', 'info');

    // Subscribe using Supabase
    if (window.SupabaseService) {
        const result = await window.SupabaseService.subscribeNewsletter(email);
        if (result.success) {
            showNotification(result.message, 'success');
            e.target.reset();
        } else {
            showNotification(result.message, 'error');
        }
    } else {
        setTimeout(() => {
            showNotification('Successfully subscribed to our newsletter!', 'success');
            e.target.reset();
        }, 1000);
    }
}

// ========================================
// Modal
// ========================================
function openLoginModal(e) {
    e.preventDefault();
    DOM.loginModal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeLoginModal() {
    DOM.loginModal.classList.remove('show');
    document.body.style.overflow = 'auto';
}

// ========================================
// Notifications
// ========================================
function showNotification(message, type = 'info') {
    // Remove existing notifications
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${getNotificationIcon(type)}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;

    // Add styles
    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${getNotificationColor(type)};
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        display: flex;
        align-items: center;
        gap: 15px;
        z-index: 9999;
        animation: slideIn 0.3s ease;
        max-width: 400px;
    `;

    document.body.appendChild(notification);

    // Add slide in animation
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

    // Close button
    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => notification.remove(), 300);
    });

    // Auto remove
    setTimeout(() => {
        if (notification.parentNode) {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => notification.remove(), 300);
        }
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
        success: 'linear-gradient(135deg, #10b981, #047857)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
        info: 'linear-gradient(135deg, #3b82f6, #2563eb)'
    };
    return colors[type] || colors.info;
}

// ========================================
// Smooth Scroll
// ========================================
function smoothScroll(e) {
    e.preventDefault();
    const targetId = e.currentTarget.getAttribute('href');
    const targetSection = document.querySelector(targetId);

    if (targetSection) {
        targetSection.scrollIntoView({
            behavior: 'smooth',
            block: 'start'
        });
    }
}

// ========================================
// Date Picker Defaults
// ========================================
function setDateDefaults() {
    const today = new Date();
    const tomorrow = new Date(today);
    tomorrow.setDate(tomorrow.getDate() + 1);
    const nextWeek = new Date(today);
    nextWeek.setDate(nextWeek.getDate() + 7);

    const formatDate = (date) => date.toISOString().split('T')[0];

    // Set min dates
    document.getElementById('departDate').min = formatDate(today);
    document.getElementById('departDate').value = formatDate(tomorrow);

    document.getElementById('returnDate').min = formatDate(tomorrow);
    document.getElementById('returnDate').value = formatDate(nextWeek);

    document.getElementById('checkInDate').min = formatDate(today);
    document.getElementById('checkInDate').value = formatDate(tomorrow);

    document.getElementById('checkOutDate').min = formatDate(tomorrow);
    document.getElementById('checkOutDate').value = formatDate(nextWeek);
}

// ========================================
// Wishlist Toggle
// ========================================
function toggleWishlist(e) {
    const btn = e.currentTarget;
    const icon = btn.querySelector('i');

    if (icon.classList.contains('far')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        icon.style.color = '#ef4444';
        showNotification('Added to wishlist!', 'success');
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        icon.style.color = '';
        showNotification('Removed from wishlist', 'info');
    }
}

// ========================================
// Close Dropdowns on Outside Click
// ========================================
function closeDropdowns(e) {
    if (!e.target.closest('.travelers-group')) {
        DOM.travelersDropdown.classList.remove('show');
    }
    if (!e.target.closest('.rooms-group')) {
        DOM.roomsDropdown.classList.remove('show');
    }
}

// ========================================
// Initialize Event Listeners
// ========================================
function initEventListeners() {
    // Scroll
    window.addEventListener('scroll', handleScroll);

    // Mobile Menu
    if (DOM.mobileMenuToggle) {
        DOM.mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }

    // Slider Controls
    if (DOM.prevSlide) DOM.prevSlide.addEventListener('click', prevSlide);
    if (DOM.nextSlide) DOM.nextSlide.addEventListener('click', nextSlide);

    // Pause slider on hover
    const heroSlider = document.querySelector('.hero-slider');
    if (heroSlider) {
        heroSlider.addEventListener('mouseenter', stopSlideInterval);
        heroSlider.addEventListener('mouseleave', startSlideInterval);
    }

    // Search Tabs
    DOM.searchTabs.forEach(tab => {
        tab.addEventListener('click', handleSearchTabs);
    });

    // Trip Type
    DOM.tripOptions.forEach(option => {
        option.addEventListener('change', handleTripType);
    });

    // Swap Button
    if (DOM.swapBtn) {
        DOM.swapBtn.addEventListener('click', swapLocations);
    }

    // Travelers Dropdown
    if (DOM.travelersSelector) {
        DOM.travelersSelector.addEventListener('click', toggleTravelersDropdown);
    }
    if (DOM.applyTravelers) {
        DOM.applyTravelers.addEventListener('click', applyTravelers);
    }

    // Rooms Dropdown
    if (DOM.roomsSelector) {
        DOM.roomsSelector.addEventListener('click', toggleRoomsDropdown);
    }
    if (DOM.applyRooms) {
        DOM.applyRooms.addEventListener('click', applyRooms);
    }

    // Counter Buttons
    document.querySelectorAll('.counter-btn').forEach(btn => {
        btn.addEventListener('click', handleCounter);
    });

    // Forms
    if (DOM.flightSearchForm) {
        DOM.flightSearchForm.addEventListener('submit', handleFlightSearch);
    }
    if (DOM.hotelSearchForm) {
        DOM.hotelSearchForm.addEventListener('submit', handleHotelSearch);
    }
    if (DOM.contactForm) {
        DOM.contactForm.addEventListener('submit', handleContactForm);
    }
    if (DOM.newsletterForm) {
        DOM.newsletterForm.addEventListener('submit', handleNewsletter);
    }

    // Modal
    if (DOM.loginBtn) {
        DOM.loginBtn.addEventListener('click', openLoginModal);
    }
    if (DOM.closeModal) {
        DOM.closeModal.addEventListener('click', closeLoginModal);
    }
    if (DOM.loginModal) {
        DOM.loginModal.querySelector('.modal-overlay').addEventListener('click', closeLoginModal);
    }

    // Login Form with Supabase Authentication
    const loginForm = document.getElementById('loginForm');
    if (loginForm) {
        loginForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const email = loginForm.querySelector('input[type="text"]').value;
            const password = loginForm.querySelector('input[type="password"]').value;

            showNotification('Logging in...', 'info');

            if (window.SupabaseService) {
                const result = await window.SupabaseService.signIn(email, password);
                if (result.success) {
                    showNotification(result.message, 'success');
                    closeLoginModal();
                    window.location.reload();
                } else {
                    showNotification(result.message, 'error');
                }
            }
        });

        // Google Login
        const googleBtn = loginForm.querySelector('.social-btn.google');
        if (googleBtn) {
            googleBtn.addEventListener('click', async () => {
                if (window.SupabaseService) {
                    await window.SupabaseService.signInWithGoogle();
                }
            });
        }

        // Facebook Login
        const facebookBtn = loginForm.querySelector('.social-btn.facebook');
        if (facebookBtn) {
            facebookBtn.addEventListener('click', async () => {
                if (window.SupabaseService) {
                    await window.SupabaseService.signInWithFacebook();
                }
            });
        }
    }

    // Section Navigation
    DOM.sectionDots.forEach(dot => {
        dot.addEventListener('click', smoothScroll);
    });

    // Nav Links
    document.querySelectorAll('.nav-link').forEach(link => {
        if (link.getAttribute('href').startsWith('#')) {
            link.addEventListener('click', smoothScroll);
        }
    });

    // Wishlist Buttons
    document.querySelectorAll('.wishlist-btn').forEach(btn => {
        btn.addEventListener('click', toggleWishlist);
    });

    // Close dropdowns on outside click
    document.addEventListener('click', closeDropdowns);

    // Escape key to close modal
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            closeLoginModal();
        }
    });
}

// ========================================
// Initialize App
// ========================================
function init() {
    hidePreloader();
    initSlider();
    setDateDefaults();
    initEventListeners();

    // Initial scroll check
    handleScroll();

    // Initialize Supabase if available
    if (window.SupabaseService) {
        window.SupabaseService.init();
    }

    console.log('Coast to Coast Journeys - Website Loaded Successfully!');
}

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', init);
