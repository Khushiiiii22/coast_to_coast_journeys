/**
 * C2C Journeys - Hotel Details Page (Expedia Style)
 * Handles hotel details display, photo gallery, and room selection
 */

document.addEventListener('DOMContentLoaded', function () {
    initHotelDetails();
});

// Global state
let selectedRate = null;
let currentHotel = null;
let searchParams = null;
let currentPhotoIndex = 0;
let hotelImages = [];

/**
 * Initialize hotel details page
 */
async function initHotelDetails() {
    // Get hotel from session
    currentHotel = SearchSession.getSelectedHotel();
    searchParams = SearchSession.getSearchParams();

    if (!currentHotel) {
        // Try to get from URL parameter
        const urlParams = new URLSearchParams(window.location.search);
        const hotelId = urlParams.get('id');

        if (!hotelId) {
            showNotification('No hotel selected', 'error');
            setTimeout(() => window.location.href = 'hotel-results.html', 2000);
            return;
        }

        // If we have demo hotel data in search results
        const searchResults = SearchSession.getSearchResults();
        if (searchResults?.data?.hotels) {
            currentHotel = searchResults.data.hotels.find(h => h.id === hotelId);
        }
    }

    if (!searchParams) {
        showNotification('Search parameters not found', 'warning');
    }

    // Display hotel data
    if (currentHotel) {
        displayHotelDetails(currentHotel);
    } else {
        // Fetch from API
        await fetchHotelDetails();
    }

    setupEventListeners();
    setupTabNavigation();
    setupPhotoGallery();
}

/**
 * Fetch hotel details from API
 */
async function fetchHotelDetails() {
    const urlParams = new URLSearchParams(window.location.search);
    const hotelId = urlParams.get('id');

    if (!hotelId) {
        showError('Hotel ID not found');
        return;
    }

    try {
        // Check API health
        try {
            await HotelAPI.healthCheck();
        } catch (e) {
            // Use demo data
            showDemoHotel(hotelId);
            return;
        }

        // Try enriched endpoint first
        try {
            const enrichedResult = await HotelAPI.getEnrichedHotelDetails({
                hotel_id: hotelId,
                checkin: searchParams?.checkin || getDefaultCheckin(),
                checkout: searchParams?.checkout || getDefaultCheckout(),
                adults: searchParams?.adults || 2,
                children_ages: searchParams?.children_ages || [],
                currency: searchParams?.currency || localStorage.getItem('ctc_currency') || 'INR'
            });

            if (enrichedResult.success && enrichedResult.data?.hotels?.length > 0) {
                currentHotel = enrichedResult.data.hotels[0];
                currentHotel.room_groups_matched = enrichedResult.data.room_groups_count || 0;
                displayHotelDetails(currentHotel);
                console.log(`✅ Loaded hotel with ${enrichedResult.data.room_groups_count} room groups matched`);
                return;
            }
        } catch (enrichedError) {
            console.log('Enriched endpoint error:', enrichedError);
        }

        // Fallback to standard hotel details endpoint
        const result = await HotelAPI.getHotelDetails({
            hotel_id: hotelId,
            checkin: searchParams?.checkin || getDefaultCheckin(),
            checkout: searchParams?.checkout || getDefaultCheckout(),
            adults: searchParams?.adults || 2
        });

        if (result.success) {
            currentHotel = result.data;
            displayHotelDetails(currentHotel);
        } else {
            showError(result.error || 'Failed to load hotel details');
        }
    } catch (error) {
        console.error('Error fetching hotel:', error);
        showDemoHotel(hotelId);
    }
}

/**
 * Show demo hotel data
 */
function showDemoHotel(hotelId) {
    currentHotel = generateDemoHotelDetails(hotelId);
    displayHotelDetails(currentHotel);
    showNotification('Showing demo data. Connect backend for real results.', 'info');
}

/**
 * Generate demo hotel details
 */
function generateDemoHotelDetails(hotelId) {
    const names = ['The Grand Palace', 'Ocean View Resort', 'Mountain Retreat', 'City Center Hotel'];
    const name = names[Math.floor(Math.random() * names.length)];
    const destination = searchParams?.destination || 'Paris';

    return {
        id: hotelId,
        name: name,
        property_type: 'Hotel',
        star_rating: Math.floor(Math.random() * 2) + 4,
        guest_rating: (Math.random() * 1 + 4).toFixed(1),
        review_count: Math.floor(Math.random() * 500) + 100,
        address: `123 Hotel Street, ${destination}`,
        description: `Experience luxury and comfort at ${name}. Our hotel offers world-class amenities, exceptional service, and a prime location. Whether you're traveling for business or leisure, we ensure an unforgettable stay with our modern facilities and warm hospitality.`,
        images: [
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
            'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800',
            'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
            'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800',
            'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=800',
            'https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=800'
        ],
        latitude: 48.8566 + (Math.random() - 0.5) * 0.1,
        longitude: 2.3522 + (Math.random() - 0.5) * 0.1,
        amenities: ['wifi', 'pool', 'parking', 'spa', 'restaurant', 'gym', 'bar', 'room_service'],
        rates: [
            {
                book_hash: `demo_hash_1_${Date.now()}`,
                room_name: 'Deluxe Room',
                room_description: 'Spacious room with city view, king bed, and modern amenities.',
                meal_plan: 'breakfast',
                meal_info: { display_name: 'Breakfast included', no_child_meal: false },
                price: Math.floor(Math.random() * 5000) + 8000,
                original_price: Math.floor(Math.random() * 3000) + 12000,
                currency: 'INR',
                cancellation: 'free',
                cancellation_info: {
                    is_free_cancellation: true,
                    free_cancellation_formatted: { datetime: 'Feb 10, 2026 at 11:59 PM' },
                    policies: [
                        { type: 'free', end_formatted: 'Feb 10, 2026' },
                        { type: 'full_penalty', start_formatted: 'Feb 11, 2026', penalty_amount: 8000 }
                    ]
                },
                features: ['King Bed', 'City View', '45 sqm', 'Free WiFi'],
                room_static: {
                    matched: true,
                    images: ['https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600']
                }
            },
            {
                book_hash: `demo_hash_2_${Date.now()}`,
                room_name: 'Premium Suite',
                room_description: 'Luxurious suite with separate living area and premium amenities.',
                meal_plan: 'halfboard',
                meal_info: { display_name: 'Breakfast + Dinner included', no_child_meal: false },
                price: Math.floor(Math.random() * 8000) + 15000,
                original_price: Math.floor(Math.random() * 5000) + 20000,
                currency: 'INR',
                cancellation: 'free',
                cancellation_info: {
                    is_free_cancellation: true,
                    free_cancellation_formatted: { datetime: 'Feb 9, 2026 at 11:59 PM' },
                    policies: [
                        { type: 'free', end_formatted: 'Feb 9, 2026' },
                        { type: 'partial_penalty', start_formatted: 'Feb 10, 2026', penalty_amount: 7500 },
                        { type: 'full_penalty', start_formatted: 'Feb 11, 2026', penalty_amount: 15000 }
                    ]
                },
                features: ['King Bed', 'Sea View', '65 sqm', 'Lounge Access', 'Butler Service'],
                room_static: {
                    matched: true,
                    images: ['https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600']
                }
            },
            {
                book_hash: `demo_hash_3_${Date.now()}`,
                room_name: 'Standard Room',
                room_description: 'Comfortable room with all essential amenities for a pleasant stay.',
                meal_plan: 'nomeal',
                meal_info: { display_name: 'Room only (no meals)', no_child_meal: true },
                price: Math.floor(Math.random() * 3000) + 5000,
                currency: 'INR',
                cancellation: 'non-refundable',
                features: ['Queen Bed', 'Garden View', '30 sqm', 'Free WiFi'],
                room_static: {
                    matched: true,
                    images: ['https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=600']
                }
            }
        ]
    };
}

/**
 * Display hotel details (Expedia Style)
 */
function displayHotelDetails(hotel) {
    hideLoading();
    document.getElementById('hotelContent').classList.remove('hidden');

    // Update page title
    document.title = `${hotel.name} | Coast To Coast Journeys`;

    // Store images for gallery
    hotelImages = hotel.images || [hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'];

    // Photo Gallery Grid (Expedia Style)
    displayPhotoGallery(hotelImages);

    // Property badges
    const propertyType = hotel.property_type || 'Hotel';
    document.getElementById('propertyType').textContent = propertyType;

    // VIP badge (show for high-rated hotels)
    const vipBadge = document.getElementById('vipBadge');
    if (hotel.star_rating >= 4 || hotel.guest_rating >= 4.5) {
        vipBadge.style.display = 'inline-flex';
    } else {
        vipBadge.style.display = 'none';
    }

    // Hotel name and stars
    document.getElementById('hotelName').textContent = hotel.name;
    document.getElementById('hotelStars').innerHTML = HotelUtils.generateStars(hotel.star_rating || 4);

    // Rating section
    const rating = parseFloat(hotel.guest_rating || 4).toFixed(1);
    document.getElementById('hotelRating').textContent = rating;
    document.getElementById('ratingLabel').textContent = getRatingLabel(rating);
    document.getElementById('reviewCount').textContent = `See all ${hotel.review_count || 0} reviews`;

    // Description
    document.getElementById('hotelDescription').textContent = hotel.description || 'Experience exceptional hospitality at this wonderful property.';

    // Address
    document.getElementById('hotelAddress').querySelector('span').textContent = hotel.address || 'Location available at booking';

    // Amenities
    displayAmenities(hotel.amenities || []);

    // Fetch and display hotel policies
    fetchHotelPolicies(hotel.id || hotel.hid);

    // Rates
    displayRates(hotel.rates || []);

    // Map preview
    if (hotel.latitude && hotel.longitude) {
        displayMapPreview(hotel.latitude, hotel.longitude);
    }

    // Update rooms section info
    updateRoomsSectionInfo();

    // Update sticky price bar
    updateStickyPriceBar(hotel.rates);
}

/**
 * Display photo gallery grid (Expedia Style)
 */
function displayPhotoGallery(images) {
    const mainImage = document.getElementById('galleryMainImage');
    const sideImages = [
        document.getElementById('sideImage1'),
        document.getElementById('sideImage2'),
        document.getElementById('sideImage3'),
        document.getElementById('sideImage4')
    ];

    // Main image
    if (images[0]) {
        mainImage.style.backgroundImage = `url('${images[0]}')`;
    }

    // Side images
    for (let i = 0; i < 4; i++) {
        if (images[i + 1] && sideImages[i]) {
            sideImages[i].style.backgroundImage = `url('${images[i + 1]}')`;
        }
    }

    // Update photo count
    const photoCount = document.getElementById('photoCount');
    if (photoCount) {
        photoCount.textContent = images.length > 5 ? `${images.length}+` : images.length;
    }

    // Make gallery clickable
    const gallerySection = document.getElementById('photoGallery');
    if (gallerySection) {
        gallerySection.addEventListener('click', () => openPhotoModal(0));
    }
}

/**
 * Setup photo gallery modal
 */
function setupPhotoGallery() {
    const modal = document.getElementById('photoModal');
    const closeBtn = document.getElementById('closePhotoModal');
    const prevBtn = document.getElementById('photoPrev');
    const nextBtn = document.getElementById('photoNext');

    if (closeBtn) {
        closeBtn.addEventListener('click', closePhotoModal);
    }

    if (prevBtn) {
        prevBtn.addEventListener('click', () => navigatePhoto(-1));
    }

    if (nextBtn) {
        nextBtn.addEventListener('click', () => navigatePhoto(1));
    }

    // Close on backdrop click
    if (modal) {
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                closePhotoModal();
            }
        });
    }

    // Keyboard navigation
    document.addEventListener('keydown', (e) => {
        if (!modal || modal.classList.contains('hidden')) return;
        if (e.key === 'Escape') closePhotoModal();
        if (e.key === 'ArrowLeft') navigatePhoto(-1);
        if (e.key === 'ArrowRight') navigatePhoto(1);
    });
}

/**
 * Open photo modal
 */
function openPhotoModal(index = 0) {
    currentPhotoIndex = index;
    const modal = document.getElementById('photoModal');
    const mainImage = document.getElementById('modalMainImage');
    const thumbnailsContainer = document.getElementById('modalThumbnails');

    if (!modal || !mainImage) return;

    // Show main image
    mainImage.src = hotelImages[currentPhotoIndex];

    // Create thumbnails
    thumbnailsContainer.innerHTML = hotelImages.map((img, i) => `
        <div class="modal-thumb ${i === currentPhotoIndex ? 'active' : ''}" 
             style="background-image: url('${img}')" 
             data-index="${i}"></div>
    `).join('');

    // Thumbnail click handlers
    thumbnailsContainer.querySelectorAll('.modal-thumb').forEach(thumb => {
        thumb.addEventListener('click', () => {
            currentPhotoIndex = parseInt(thumb.dataset.index);
            updateModalImage();
        });
    });

    // Update counter
    updatePhotoCounter();

    // Show modal
    modal.classList.remove('hidden');
    document.body.style.overflow = 'hidden';
}

/**
 * Close photo modal
 */
function closePhotoModal() {
    const modal = document.getElementById('photoModal');
    if (modal) {
        modal.classList.add('hidden');
        document.body.style.overflow = '';
    }
}

/**
 * Navigate photos
 */
function navigatePhoto(direction) {
    currentPhotoIndex = (currentPhotoIndex + direction + hotelImages.length) % hotelImages.length;
    updateModalImage();
}

/**
 * Update modal image
 */
function updateModalImage() {
    const mainImage = document.getElementById('modalMainImage');
    if (mainImage) {
        mainImage.src = hotelImages[currentPhotoIndex];
    }

    // Update active thumbnail
    document.querySelectorAll('.modal-thumb').forEach((thumb, i) => {
        thumb.classList.toggle('active', i === currentPhotoIndex);
    });

    updatePhotoCounter();
}

/**
 * Update photo counter
 */
function updatePhotoCounter() {
    const currentNum = document.getElementById('currentPhotoNum');
    const totalNum = document.getElementById('totalPhotoNum');
    if (currentNum) currentNum.textContent = currentPhotoIndex + 1;
    if (totalNum) totalNum.textContent = hotelImages.length;
}

/**
 * Setup tab navigation
 */
function setupTabNavigation() {
    const tabButtons = document.querySelectorAll('.tab-btn');

    tabButtons.forEach(btn => {
        btn.addEventListener('click', () => {
            const tab = btn.dataset.tab;

            // Update active tab
            tabButtons.forEach(b => b.classList.remove('active'));
            btn.classList.add('active');

            // Scroll to section
            let targetSection;
            switch (tab) {
                case 'overview':
                    targetSection = document.getElementById('overviewSection');
                    break;
                case 'about':
                    targetSection = document.getElementById('aboutSection');
                    break;
                case 'rooms':
                    targetSection = document.getElementById('roomsSection');
                    break;
                case 'policies':
                    targetSection = document.getElementById('policiesSection');
                    break;
            }

            if (targetSection) {
                targetSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    // Reserve button
    const reserveBtn = document.getElementById('quickReserveBtn');
    if (reserveBtn) {
        reserveBtn.addEventListener('click', () => {
            document.getElementById('roomsSection')?.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // Sticky reserve button
    const stickyReserveBtn = document.getElementById('stickyReserveBtn');
    if (stickyReserveBtn) {
        stickyReserveBtn.addEventListener('click', () => {
            document.getElementById('roomsSection')?.scrollIntoView({ behavior: 'smooth' });
        });
    }
}

/**
 * Display amenities grid (Expedia Style)
 */
function displayAmenities(amenities) {
    const grid = document.getElementById('amenitiesGrid');
    const amenityData = {
        wifi: { icon: 'fa-wifi', label: 'Free WiFi' },
        pool: { icon: 'fa-swimming-pool', label: 'Pool' },
        parking: { icon: 'fa-parking', label: 'Free Parking' },
        spa: { icon: 'fa-spa', label: 'Spa' },
        restaurant: { icon: 'fa-utensils', label: 'Restaurant' },
        gym: { icon: 'fa-dumbbell', label: 'Fitness Center' },
        bar: { icon: 'fa-glass-martini-alt', label: 'Bar' },
        room_service: { icon: 'fa-concierge-bell', label: 'Room Service' },
        ac: { icon: 'fa-snowflake', label: 'Air conditioning' },
        laundry: { icon: 'fa-tshirt', label: 'Laundry' }
    };

    if (!grid) return;

    grid.innerHTML = '';
    amenities.slice(0, 8).forEach(a => {
        const data = amenityData[a] || { icon: 'fa-check', label: a };
        const item = document.createElement('div');
        item.className = 'amenity-item';
        item.innerHTML = `<i class="fas ${data.icon}"></i> <span>${data.label}</span>`;
        grid.appendChild(item);
    });
}

/**
 * Display map preview (Expedia Style)
 */
function displayMapPreview(lat, lng) {
    const mapPreview = document.getElementById('mapPreview');
    if (!mapPreview) return;

    mapPreview.innerHTML = `
        <iframe 
            width="100%" 
            height="100%" 
            frameborder="0" 
            scrolling="no" 
            marginheight="0" 
            marginwidth="0" 
            src="https://www.openstreetmap.org/export/embed.html?bbox=${parseFloat(lng) - 0.01},${parseFloat(lat) - 0.01},${parseFloat(lng) + 0.01},${parseFloat(lat) + 0.01}&layer=mapnik&marker=${lat},${lng}"
        ></iframe>
    `;

    // Add nearby places (demo data)
    const nearbyPlaces = document.getElementById('nearbyPlaces');
    if (nearbyPlaces) {
        nearbyPlaces.innerHTML = `
            <div class="nearby-place">
                <span class="place-name">City Center</span>
                <span class="place-distance">1.2 km</span>
            </div>
            <div class="nearby-place">
                <span class="place-name">Train Station</span>
                <span class="place-distance">2.5 km</span>
            </div>
            <div class="nearby-place">
                <span class="place-name">Airport</span>
                <span class="place-distance">15 km</span>
            </div>
        `;
    }
}

/**
 * Fetch hotel policies from RateHawk static data
 */
async function fetchHotelPolicies(hotelId) {
    const loadingEl = document.getElementById('policiesLoading');
    const errorEl = document.getElementById('policiesError');

    if (!hotelId || hotelId.startsWith('google_') || hotelId.startsWith('demo_') || hotelId.startsWith('test_')) {
        loadingEl?.classList.add('hidden');
        // Show default policies for demo
        displayDefaultPolicies();
        return;
    }

    try {
        const result = await HotelAPI.getHotelPolicies(hotelId);

        if (result.success && result.data) {
            loadingEl?.classList.add('hidden');
            displayHotelPolicies(result.data.formatted_policies);
        } else {
            loadingEl?.classList.add('hidden');
            displayDefaultPolicies();
        }
    } catch (error) {
        console.log('Could not fetch hotel policies:', error);
        loadingEl?.classList.add('hidden');
        displayDefaultPolicies();
    }
}

/**
 * Display default policies
 */
function displayDefaultPolicies() {
    const policies = {
        check_in_out: [
            { icon: 'fa-sign-in-alt', label: 'Check-in', value: 'From 3:00 PM' },
            { icon: 'fa-sign-out-alt', label: 'Check-out', value: 'Until 11:00 AM' }
        ],
        children: [
            { icon: 'fa-child', label: 'Children', value: 'Children of all ages welcome' }
        ],
        pets: [
            { icon: 'fa-paw', label: 'Pets', value: 'Contact property for pet policy' }
        ],
        payments: [
            { icon: 'fa-credit-card', label: 'Payment', value: 'Credit/Debit cards accepted' }
        ],
        internet: [
            { icon: 'fa-wifi', label: 'WiFi', value: 'Free WiFi available' }
        ],
        parking: [
            { icon: 'fa-parking', label: 'Parking', value: 'Subject to availability' }
        ]
    };

    displayHotelPolicies(policies);
}

/**
 * Display formatted hotel policies (Expedia Style)
 */
function displayHotelPolicies(policies) {
    const sections = {
        'check_in_out': 'policyCheckInOut',
        'children': 'policyChildren',
        'extra_beds': 'policyExtraBeds',
        'pets': 'policyPets',
        'internet': 'policyInternet',
        'parking': 'policyParking',
        'payments': 'policyPayments',
        'meals': 'policyMeals',
        'other': 'policyOther'
    };

    for (const [key, elementId] of Object.entries(sections)) {
        const sectionEl = document.getElementById(elementId);
        const itemsEl = sectionEl?.querySelector('.policy-items');
        const policyItems = policies[key] || [];

        if (policyItems.length > 0 && itemsEl) {
            sectionEl.style.display = 'flex';
            itemsEl.innerHTML = policyItems.map(item => `
                <div class="policy-item">
                    <i class="fas fa-check-circle"></i>
                    <span>${item.label ? `${item.label}: ${item.value}` : item.value || item}</span>
                </div>
            `).join('');
        } else if (sectionEl) {
            sectionEl.style.display = 'none';
        }
    }
}

/**
 * Update rooms section info
 */
function updateRoomsSectionInfo() {
    if (searchParams) {
        const nights = HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout);
        document.getElementById('roomsNightsInfo').textContent = `${nights} night${nights > 1 ? 's' : ''}`;

        const adults = parseInt(searchParams.adults || 2);
        const children = searchParams.children_ages ? searchParams.children_ages.length : 0;
        const total = adults + children;
        document.getElementById('roomsGuestsInfo').textContent = `${total} guest${total > 1 ? 's' : ''}`;
    }
}

/**
 * Update sticky price bar
 */
function updateStickyPriceBar(rates) {
    if (!rates || rates.length === 0) return;

    const lowestPrice = Math.min(...rates.map(r => r.price));
    const stickyPrice = document.getElementById('stickyPrice');
    if (stickyPrice) {
        stickyPrice.textContent = HotelUtils.formatPrice(lowestPrice);
    }
}

/**
 * Display room rates (Expedia Style)
 */
function displayRates(rates) {
    const container = document.getElementById('ratesList');
    if (!container) return;

    container.innerHTML = '';

    if (rates.length === 0) {
        container.innerHTML = '<p class="no-rates" style="text-align: center; padding: 40px; color: #6b7280;">No rooms available for selected dates.</p>';
        return;
    }

    rates.forEach((rate, index) => {
        const card = createRateCard(rate, index);
        container.appendChild(card);
    });
}

/**
 * Build tax display HTML for rate card
 * Shows non-included taxes that must be paid at check-in (RateHawk requirement)
 */
function buildTaxDisplayHtml(rate) {
    const taxInfo = rate.tax_info || {};
    const nonIncludedTaxes = taxInfo.non_included_taxes || [];

    if (nonIncludedTaxes.length > 0) {
        // There are taxes to be paid at check-in
        const taxItems = nonIncludedTaxes.map(tax => {
            const amount = parseFloat(tax.amount || 0);
            const currency = tax.currency_code || 'USD';
            const displayName = tax.display_name || tax.name || 'Tax';
            return `<div class="tax-item"><span>${displayName}</span><span>${currency} ${amount.toFixed(2)}</span></div>`;
        }).join('');

        return `
            <div style="font-size: 0.75rem; color: #6b7280;">Includes taxes & fees</div>
            <div class="non-included-taxes-notice">
                <div class="taxes-header">
                    <i class="fas fa-info-circle"></i>
                    <span>Additional fees payable at property:</span>
                </div>
                <div class="taxes-list">
                    ${taxItems}
                </div>
                <div class="taxes-note">These taxes are not included in the price and must be paid at check-in.</div>
            </div>
        `;
    } else {
        return '<div style="font-size: 0.75rem; color: #6b7280;">Includes taxes & fees</div>';
    }
}

/**
 * Create rate card element (Expedia Style)
 */
function createRateCard(rate, index) {
    const card = document.createElement('div');
    card.className = 'rate-card';
    card.dataset.rateIndex = index;

    const price = HotelUtils.formatPrice(rate.price);
    const originalPrice = rate.original_price ? HotelUtils.formatPrice(rate.original_price) : null;

    // Meal Plan
    const mealInfo = rate.meal_info || {};
    let mealPlanHtml = '';
    let noChildMealWarning = '';

    if (mealInfo.display_name) {
        mealPlanHtml = `<p class="rate-meal-plan"><i class="fas fa-utensils"></i> ${mealInfo.display_name}</p>`;
        // Add warning if meal is not included for children
        if (mealInfo.no_child_meal) {
            noChildMealWarning = `
                <div class="no-child-meal-warning">
                    <i class="fas fa-exclamation-triangle"></i>
                    <span>Note: Meals are NOT included for children in this rate</span>
                </div>
            `;
        }
    } else {
        const mealText = HotelUtils.getMealPlanText(rate.meal_plan || rate.meal);
        mealPlanHtml = `<p class="rate-meal-plan"><i class="fas fa-utensils"></i> ${mealText}</p>`;
    }

    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = HotelUtils.formatPrice(rate.price * nights);

    // Cancellation badge
    const cancellationInfo = rate.cancellation_info || {};
    let cancellationBadge = '';
    let cancellationDetailsHtml = '';

    if (cancellationInfo.is_free_cancellation && cancellationInfo.free_cancellation_formatted) {
        const deadline = cancellationInfo.free_cancellation_formatted;
        cancellationBadge = `
            <span class="cancellation-badge free">
                <i class="fas fa-check-circle"></i> Free Cancellation
            </span>
        `;
        cancellationDetailsHtml = `
            <div class="cancellation-deadline">
                <i class="fas fa-clock"></i>
                <span>Cancel free until <strong>${deadline.datetime}</strong> <small style="color:#64748b;">(UTC+0)</small></span>
            </div>
        `;

        // Policy timeline
        const policies = cancellationInfo.policies || [];
        if (policies.length > 0) {
            const policyItems = policies.map(policy => {
                let icon, label, dateRange, penaltyText, tierClass;
                if (policy.type === 'free') {
                    icon = 'fa-check-circle';
                    label = 'Free cancellation';
                    tierClass = 'tier-free';
                    dateRange = policy.end_formatted ? `Until ${policy.end_formatted}` : '';
                    penaltyText = '';
                } else if (policy.type === 'partial_penalty') {
                    icon = 'fa-exclamation-circle';
                    label = 'Partial penalty';
                    tierClass = 'tier-partial';
                    dateRange = policy.start_formatted ? `From ${policy.start_formatted}` : '';
                    const amount = parseFloat(policy.penalty_amount || 0).toFixed(0);
                    penaltyText = `Penalty: ₹${amount}`;
                } else if (policy.type === 'full_penalty') {
                    icon = 'fa-times-circle';
                    label = 'Non-refundable';
                    tierClass = 'tier-full';
                    dateRange = policy.start_formatted ? `From ${policy.start_formatted}` : '';
                    const amount = parseFloat(policy.penalty_amount || 0).toFixed(0);
                    penaltyText = `Penalty: ₹${amount}`;
                } else {
                    return '';
                }

                return `
                    <div class="policy-tier ${tierClass}">
                        <div class="tier-icon"><i class="fas ${icon}"></i></div>
                        <div class="tier-content">
                            <span class="tier-label">${label}</span>
                            <span class="tier-date">${dateRange}</span>
                            ${penaltyText ? `<span class="tier-penalty">${penaltyText}</span>` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            cancellationDetailsHtml += `
                <div class="cancellation-policy-details">
                    <button class="policy-toggle" onclick="this.parentElement.classList.toggle('expanded')">
                        <i class="fas fa-chevron-down"></i> View cancellation policy
                    </button>
                    <div class="policy-timeline">
                        <div class="timeline-header"><i class="fas fa-calendar-alt"></i> Cancellation Timeline</div>
                        ${policyItems}
                    </div>
                </div>
            `;
        }
    } else if (rate.cancellation === 'free') {
        cancellationBadge = '<span class="cancellation-badge free"><i class="fas fa-check-circle"></i> Free Cancellation</span>';
    } else {
        cancellationBadge = '<span class="cancellation-badge non-refund"><i class="fas fa-ban"></i> Non-refundable</span>';
        cancellationDetailsHtml = `
            <div class="non-refundable-notice">
                <i class="fas fa-exclamation-triangle"></i>
                <span>This rate is non-refundable. Cancellation will incur full charges.</span>
            </div>
        `;
    }

    // Room images
    const roomStatic = rate.room_static || {};
    const roomImages = roomStatic.images || [];
    let roomImageHtml = '';
    if (roomImages.length > 0) {
        roomImageHtml = `
            <div class="room-image-gallery">
                <div class="room-main-image" style="background-image: url('${roomImages[0]}');">
                    ${roomImages.length > 1 ? `<span class="image-count"><i class="fas fa-images"></i> ${roomImages.length}</span>` : ''}
                </div>
            </div>
        `;
    }

    // Room amenities
    const roomAmenities = roomStatic.amenities || rate.features || [];
    let roomAmenitiesHtml = '';
    if (roomAmenities.length > 0) {
        const amenityIcons = {
            'wifi': 'fa-wifi', 'King Bed': 'fa-bed', 'Queen Bed': 'fa-bed',
            'City View': 'fa-city', 'Sea View': 'fa-water', 'Free WiFi': 'fa-wifi',
            'air_conditioning': 'fa-snowflake', 'tv': 'fa-tv', 'minibar': 'fa-wine-bottle'
        };

        const displayAmenities = roomAmenities.slice(0, 5).map(amenity => {
            const label = typeof amenity === 'string' ? amenity : (amenity.label || amenity.name || '');
            const icon = amenityIcons[label] || 'fa-check';
            return `<span class="room-amenity"><i class="fas ${icon}"></i> ${label}</span>`;
        }).join('');

        roomAmenitiesHtml = `
            <div class="room-amenities-list">
                ${displayAmenities}
                ${roomAmenities.length > 5 ? `<span class="more-amenities">+${roomAmenities.length - 5} more</span>` : ''}
            </div>
        `;
    }

    card.innerHTML = `
        ${roomImageHtml}
        <div class="rate-card-content">
            <div class="rate-main-info">
                <h3 class="rate-room-name">${rate.room_name || roomStatic.room_name || 'Room'}</h3>
                
                <div class="rate-badges">
                    ${cancellationBadge}
                    ${mealPlanHtml}
                </div>
                
                ${noChildMealWarning}

                ${roomAmenitiesHtml}
                
                <div class="rate-policies">
                    ${cancellationDetailsHtml}
                </div>
            </div>

            <div class="rate-price-action">
                <div class="price-display">
                    ${originalPrice ? `<div class="original-price">${originalPrice} /night</div>` : ''}
                    <div class="rate-per-night">${price} <small>/night</small></div>
                    <div class="rate-total">${totalPrice} <small>total</small></div>
                    ${buildTaxDisplayHtml(rate)}
                </div>

                <button class="book-rate-btn" data-rate-index="${index}">
                    Reserve <i class="fas fa-arrow-right"></i>
                </button>
            </div>
        </div>
    `;

    card.querySelector('.book-rate-btn').addEventListener('click', () => {
        selectRate(rate, index);
    });

    return card;
}

/**
 * Select a rate and proceed to booking
 */
function selectRate(rate, index) {
    selectedRate = rate;

    // Update UI
    document.querySelectorAll('.rate-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.rate-card[data-rate-index="${index}"]`).classList.add('selected');

    // Calculate total
    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = rate.price * nights;

    // Save selected rate
    SearchSession.saveSelectedRate({
        ...rate,
        total_price: totalPrice,
        nights: nights
    });

    // Save booking data for checkout page
    SearchSession.saveBookingData({
        hotel: currentHotel,
        rate: {
            ...rate,
            total_price: totalPrice,
            nights: nights
        },
        search_params: searchParams
    });

    showNotification(`${rate.room_name} selected! Redirecting to checkout...`, 'success');

    // Redirect to checkout page
    setTimeout(() => {
        window.location.href = 'guest-details.html';
    }, 800);
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Share button
    const shareBtn = document.getElementById('shareBtn');
    if (shareBtn) {
        shareBtn.addEventListener('click', () => {
            if (navigator.share) {
                navigator.share({
                    title: currentHotel?.name || 'Hotel',
                    url: window.location.href
                });
            } else {
                navigator.clipboard.writeText(window.location.href);
                showNotification('Link copied to clipboard!', 'success');
            }
        });
    }

    // Save button
    const saveBtn = document.getElementById('saveBtn');
    if (saveBtn) {
        saveBtn.addEventListener('click', () => {
            saveBtn.innerHTML = '<i class="fas fa-heart"></i> Saved';
            saveBtn.style.color = '#ef4444';
            showNotification('Added to your wishlist!', 'success');
        });
    }
}

// Helper functions
function getRatingLabel(rating) {
    const r = parseFloat(rating);
    if (r >= 4.5) return 'Excellent';
    if (r >= 4) return 'Very Good';
    if (r >= 3.5) return 'Good';
    if (r >= 3) return 'Average';
    return 'Fair';
}

function getDefaultCheckin() {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    return tomorrow.toISOString().split('T')[0];
}

function getDefaultCheckout() {
    const nextWeek = new Date();
    nextWeek.setDate(nextWeek.getDate() + 8);
    return nextWeek.toISOString().split('T')[0];
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function showError(message) {
    hideLoading();
    document.getElementById('hotelContent').innerHTML = `
        <div class="error-state" style="text-align: center; padding: 80px 20px;">
            <i class="fas fa-exclamation-circle" style="font-size: 4rem; color: #ef4444; margin-bottom: 20px;"></i>
            <h3 style="font-size: 1.5rem; color: #111827; margin-bottom: 10px;">Error Loading Hotel</h3>
            <p style="color: #6b7280; margin-bottom: 24px;">${message}</p>
            <a href="hotel-results.html" class="btn btn-primary" style="background: #1e40af; color: white; padding: 12px 24px; border-radius: 8px; text-decoration: none;">Back to Results</a>
        </div>
    `;
    document.getElementById('hotelContent').classList.remove('hidden');
}

function showNotification(message, type = 'info') {
    const existing = document.querySelector('.notification');
    if (existing) existing.remove();

    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;

    const icons = {
        success: 'fa-check-circle',
        error: 'fa-times-circle',
        warning: 'fa-exclamation-triangle',
        info: 'fa-info-circle'
    };

    const colors = {
        success: 'linear-gradient(135deg, #10b981, #047857)',
        error: 'linear-gradient(135deg, #ef4444, #dc2626)',
        warning: 'linear-gradient(135deg, #f59e0b, #d97706)',
        info: 'linear-gradient(135deg, #3b82f6, #2563eb)'
    };

    notification.innerHTML = `
        <div class="notification-content">
            <i class="fas ${icons[type]}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${colors[type]};
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

    notification.querySelector('.notification-close').addEventListener('click', () => {
        notification.remove();
    });

    setTimeout(() => notification.remove(), 5000);
}
