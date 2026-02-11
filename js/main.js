/**
 * C2C Journeys - Main JavaScript
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
    currencySelect: document.getElementById('currencySelect'),

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
    sections: document.querySelectorAll('.fullpage-section'),

    // Testimonial Slider
    testimonialTrack: document.querySelector('.testimonials-track'),
    testimonialDots: document.querySelectorAll('.carousel-indicators .dot')
};

let currentTestimonialSlide = 0;
let testimonialInterval;

let currentSlide = 0;
let slideInterval;

// ========================================
// Preloader
// ========================================
function hidePreloader() {
    setTimeout(() => {
        const preloader = document.getElementById('preloader') || document.querySelector('.preloader');
        if (preloader) {
            preloader.classList.add('hidden');
            preloader.style.display = 'none';
        }
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

    try {
        // Call Backend API
        const response = await fetch('/api/flights/search', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        });

        const data = await response.json();

        if (data.success) {
            // Save results to session storage for results page
            sessionStorage.setItem('ctc_flight_results', JSON.stringify(data.data));
            sessionStorage.setItem('ctc_flight_search_params', JSON.stringify(formData));

            // Redirect to results page
            window.location.href = 'flight-results.html';
        } else {
            showNotification(data.error || 'Failed to search flights', 'error');
        }
    } catch (error) {
        console.error('Search error:', error);
        showNotification('Error connecting to server', 'error');
    }
}

async function handleHotelSearch(e) {
    e.preventDefault();

    // Parse rooms and guests from display text
    const roomsText = DOM.roomsCount.textContent;
    const rooms = parseInt(roomsText) || 1;

    const adults = parseInt(document.getElementById('hotelAdults')?.value) || 2;
    const children = parseInt(document.getElementById('hotelChildren')?.value) || 0;
    const childrenAges = [];
    for (let i = 0; i < children; i++) {
        childrenAges.push(8); // Default child age
    }

    const regionId = document.getElementById('hotelRegionId')?.value || null;

    const searchParams = {
        destination: document.getElementById('hotelDestination').value,
        region_id: regionId,
        checkin: document.getElementById('checkInDate').value,
        checkout: document.getElementById('checkOutDate').value,
        rooms: rooms,
        adults: adults,
        children_ages: childrenAges,
        currency: DOM.currencySelect ? DOM.currencySelect.value : 'INR'
    };

    // Validate
    if (!searchParams.destination) {
        showNotification('Please enter a destination', 'warning');
        return;
    }

    if (!searchParams.checkin || !searchParams.checkout) {
        showNotification('Please select check-in and check-out dates', 'warning');
        return;
    }

    console.log('Hotel Search:', searchParams);
    showNotification('Searching for hotels...', 'info');

    // Save search params to session for results page
    if (window.SearchSession) {
        window.SearchSession.saveSearchParams(searchParams);
        window.SearchSession.remove(window.SearchSession.KEYS.SEARCH_RESULTS);
    } else {
        // Fallback if hotel-api.js not loaded
        sessionStorage.setItem('ctc_hotel_search_params', JSON.stringify(searchParams));
    }

    // Save search to database if Supabase is available (non-blocking)
    if (window.SupabaseService) {
        try {
            window.SupabaseService.saveHotelSearch({
                destination: searchParams.destination,
                check_in_date: searchParams.checkin,
                check_out_date: searchParams.checkout,
                rooms: searchParams.rooms,
                guests: searchParams.adults + childrenAges.length
            }).catch(err => console.log('Save hotel search skipped:', err.message));
        } catch (err) {
            console.log('Supabase not configured, skipping save');
        }
    }

    // Redirect to hotel results page
    window.location.href = 'hotel-results.html';
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
// Initialize Currency
// ========================================
function initCurrency() {
    if (DOM.currencySelect) {
        // Load saved currency
        const savedCurrency = localStorage.getItem('ctc_currency');
        if (savedCurrency) {
            DOM.currencySelect.value = savedCurrency;
        }

        // Save on change
        DOM.currencySelect.addEventListener('change', function () {
            localStorage.setItem('ctc_currency', this.value);
            // Optional: Reload page if on results page to refresh prices
            // window.location.reload(); 
        });
    }
}

// ========================================
// Initialize Event Listeners
// ========================================
function initEventListeners() {
    // Currency
    initCurrency();

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

    // Destination Quick Pills
    document.querySelectorAll('.dest-pill').forEach(pill => {
        pill.addEventListener('click', function () {
            const destination = this.dataset.destination;
            const regionId = this.dataset.regionId;

            // Switch to hotels tab
            const hotelTab = document.querySelector('.search-tab[data-tab="hotels"]');
            if (hotelTab) {
                hotelTab.click();
            }

            // Fill destination input
            const hotelDestination = document.getElementById('hotelDestination');
            if (hotelDestination) {
                hotelDestination.value = destination;
                hotelDestination.dataset.regionId = regionId;
            }

            // Add active state to clicked pill
            document.querySelectorAll('.dest-pill').forEach(p => p.classList.remove('active'));
            this.classList.add('active');

            // Show notification
            showNotification(`Searching hotels in ${destination}`, 'info');
        });
    });

    // Mobile Bottom Navigation
    document.querySelectorAll('.mobile-bottom-nav .nav-item').forEach(item => {
        item.addEventListener('click', function (e) {
            // Update active state
            document.querySelectorAll('.mobile-bottom-nav .nav-item').forEach(i => i.classList.remove('active'));
            this.classList.add('active');
        });
    });

    // Mobile Profile Button
    const mobileProfileBtn = document.getElementById('mobileProfileBtn');
    if (mobileProfileBtn) {
        mobileProfileBtn.addEventListener('click', function (e) {
            e.preventDefault();
            // Open login modal if not logged in
            if (DOM.loginModal) {
                DOM.loginModal.classList.add('show');
                document.body.style.overflow = 'hidden';
            }
        });
    }

    // Testimonial Slider Init
    if (DOM.testimonialTrack && DOM.testimonialDots.length > 0) {
        initTestimonialSlider();
    }
}

// ========================================
// Testimonial Slider Logic
// ========================================
function initTestimonialSlider() {
    DOM.testimonialDots.forEach((dot, index) => {
        dot.addEventListener('click', () => {
            goToTestimonialSlide(index);
            resetTestimonialInterval();
        });
    });

    startTestimonialInterval();
}

function goToTestimonialSlide(index) {
    const track = DOM.testimonialTrack;
    const cards = track.querySelectorAll('.testimonial-card');
    const totalSlides = cards.length;

    // Determine overlapping/visible items based on screen width
    // On mobile, 1 item visible (100% width). On desktop, 2 items (50% width).
    // The previous CSS sets width: calc(50% - 32px) and margin 0 16px.
    // Movement logic:
    // If we move by 1 slide index, we should translate by 50% (desktop) or 100% (mobile).

    // Check if mobile
    const isMobile = window.innerWidth <= 768;
    const slidePercentage = isMobile ? 100 : 50;

    // Cap index
    // For simple linear slider that stops at end:
    let maxIndex = totalSlides - (isMobile ? 1 : 2);
    if (maxIndex < 0) maxIndex = 0;

    // Handle index bounds
    if (index > maxIndex) {
        if (!isMobile && index === maxIndex + 1) {
            // Allow clicking the last dot to show the last view
            index = maxIndex;
        } else {
            index = 0;
        }
    }

    currentTestimonialSlide = index;

    // Update Dots
    DOM.testimonialDots.forEach(dot => dot.classList.remove('active'));
    // Activate the dot corresponding to current slide, or nearest
    if (DOM.testimonialDots[currentTestimonialSlide]) {
        DOM.testimonialDots[currentTestimonialSlide].classList.add('active');
    }

    // Update Track
    const translateX = -(currentTestimonialSlide * slidePercentage);
    track.style.transform = `translateX(${translateX}%)`;
}

function nextTestimonialSlide() {
    const track = DOM.testimonialTrack;
    if (!track) return;
    const cards = track.querySelectorAll('.testimonial-card');
    const isMobile = window.innerWidth <= 768;
    const totalSlides = cards.length;
    let maxIndex = totalSlides - (isMobile ? 1 : 2);
    if (maxIndex < 0) maxIndex = 0;

    let nextIndex = currentTestimonialSlide + 1;
    if (nextIndex > maxIndex) {
        nextIndex = 0;
    }
    goToTestimonialSlide(nextIndex);
}

function startTestimonialInterval() {
    if (testimonialInterval) clearInterval(testimonialInterval);
    testimonialInterval = setInterval(nextTestimonialSlide, 5000);
}

function resetTestimonialInterval() {
    clearInterval(testimonialInterval);
    startTestimonialInterval();
}

// ========================================
// Scroll Reveal Animation
// ========================================
function initScrollReveal() {
    const sections = document.querySelectorAll('.fullpage-section');
    const cards = document.querySelectorAll('.hotel-card, .category-card, .deal-card, .partner-card, .flight-route-card');

    const revealOptions = {
        threshold: 0.15,
        rootMargin: '0px 0px -50px 0px'
    };

    const revealOnScroll = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('visible');
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, revealOptions);

    sections.forEach(section => {
        if (!section.classList.contains('hero-section')) {
            revealOnScroll.observe(section);
        }
    });

    // Staggered reveal for cards
    const cardObserver = new IntersectionObserver((entries) => {
        entries.forEach((entry, index) => {
            if (entry.isIntersecting) {
                setTimeout(() => {
                    entry.target.style.opacity = '1';
                    entry.target.style.transform = 'translateY(0)';
                }, index * 100);
            }
        });
    }, { threshold: 0.1 });

    cards.forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(30px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        cardObserver.observe(card);
    });
}

// ========================================
// Smooth Number Counter Animation
// ========================================
function animateCounter(element, target, duration = 2000) {
    let start = 0;
    const increment = target / (duration / 16);

    const updateCounter = () => {
        start += increment;
        if (start < target) {
            element.textContent = Math.floor(start).toLocaleString();
            requestAnimationFrame(updateCounter);
        } else {
            element.textContent = target.toLocaleString();
        }
    };

    updateCounter();
}

// ========================================
// Enhanced Hover Effects
// ========================================
function initEnhancedHovers() {
    // 3D tilt effect on cards
    const cards = document.querySelectorAll('.hotel-card, .category-card, .deal-card');

    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;

            const centerX = rect.width / 2;
            const centerY = rect.height / 2;

            const rotateX = (y - centerY) / 20;
            const rotateY = (centerX - x) / 20;

            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translateY(-5px)`;
        });

        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0) translateY(0)';
        });
    });
}

// ========================================
// Smooth Page Load
// ========================================
function initSmoothLoad() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease';

    window.addEventListener('load', () => {
        document.body.style.opacity = '1';
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
    initScrollReveal();
    initEnhancedHovers();

    // Initial scroll check
    handleScroll();

    // Initialize Supabase if available
    if (window.SupabaseService) {
        window.SupabaseService.init();
    }

    // Add loaded class for animations
    document.body.classList.add('loaded');

    console.log('C2C Journeys - Website Loaded Successfully!');
}

// Run when DOM is ready
document.addEventListener('DOMContentLoaded', init);
