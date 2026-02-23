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

        // For Google Places hotels, fetch additional photos for gallery
        if (currentHotel.id && currentHotel.id.startsWith('google_')) {
            fetchGooglePlacePhotos(currentHotel.id);
        }
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
            } else if (hotelId.startsWith('demo_')) {
                showDemoHotel(hotelId);
                return;
            }
        } catch (enrichedError) {
            console.log('Enriched endpoint error:', enrichedError);
            if (hotelId.startsWith('demo_')) {
                showDemoHotel(hotelId);
                return;
            }
        }

        // Fallback to standard hotel details endpoint
        const result = await HotelAPI.getHotelDetails({
            hotel_id: hotelId,
            checkin: searchParams?.checkin || getDefaultCheckin(),
            checkout: searchParams?.checkout || getDefaultCheckout(),
            adults: searchParams?.adults || 2
        });

        if (result.success && result.data && (result.data.name || result.data.hotels?.length > 0)) {
            currentHotel = result.data.hotels ? result.data.hotels[0] : result.data;
            displayHotelDetails(currentHotel);
        } else {
            console.log('API returned success but no hotel data. Falling back to demo.');
            showDemoHotel(hotelId);
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
        displayMapPreview(hotel.latitude, hotel.longitude, hotel);
    } else {
        // Fallback: show map with search query for the hotel address/name
        displayMapPreviewByAddress(hotel.address || hotel.name || 'Hotel');
    }

    // Update rooms section info
    updateRoomsSectionInfo();

    // Update sticky price bar
    updateStickyPriceBar(hotel.rates);

    // Initialize Expedia-style enhancements
    if (typeof ExpediaEnhancements !== 'undefined') {
        ExpediaEnhancements.initialize(hotel);
    }
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
            const targetSection = document.getElementById(tab);

            if (targetSection) {
                const headerOffset = 150;
                const elementPosition = targetSection.getBoundingClientRect().top;
                const offsetPosition = elementPosition + window.pageYOffset - headerOffset;

                window.scrollTo({
                    top: offsetPosition,
                    behavior: 'smooth'
                });
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
 * Display map preview using Google Maps embed (works with lat/lng)
 * No API key required for embed URL
 */
function displayMapPreview(lat, lng, hotelData = {}) {
    const mapPreview = document.getElementById('mapPreview');
    if (!mapPreview) return;

    const query = `${parseFloat(lat)},${parseFloat(lng)}`;
    mapPreview.innerHTML = `
        <iframe
            width="100%"
            height="100%"
            style="border:0;"
            loading="lazy"
            allowfullscreen
            referrerpolicy="no-referrer-when-downgrade"
            src="https://maps.google.com/maps?q=${query}&z=15&output=embed"
        ></iframe>
    `;

    // Process surroundings from static_data if available
    const staticData = hotelData.static_data || {};
    const surroundings = staticData.surroundings || [];

    // Categorization logic
    const categories = {
        'categoryNearby': [],
        'categoryInterest': [],
        'categoryAirports': [],
        'categorySubway': []
    };

    if (surroundings.length > 0) {
        surroundings.forEach(place => {
            const item = {
                name: place.name,
                distance: place.distance_value ? `${place.distance_value} ${place.distance_unit || 'm'}` : 'Nearby',
                icon: 'fa-map-marker-alt'
            };

            const type = (place.type || '').toLowerCase();
            if (type.includes('airport')) categories.categoryAirports.push(item);
            else if (type.includes('metro') || type.includes('subway') || type.includes('station')) categories.categorySubway.push(item);
            else if (type.includes('sight') || type.includes('museum') || type.includes('landmark')) categories.categoryInterest.push(item);
            else categories.categoryNearby.push(item);
        });
    } else {
        // Fallback demo data if no surroundings from API
        categories.categoryNearby = [
            { name: 'City Center', distance: '1.2 km', icon: 'fa-city' },
            { name: 'Shopping Mall', distance: '800 m', icon: 'fa-shopping-bag' }
        ];
        categories.categoryInterest = [
            { name: 'Famous Landmark', distance: '2.5 km', icon: 'fa-monument' },
            { name: 'City Museum', distance: '3.1 km', icon: 'fa-university' }
        ];
        categories.categoryAirports = [
            { name: 'International Airport', distance: '15 km', icon: 'fa-plane' }
        ];
        categories.categorySubway = [
            { name: 'Central Station', distance: '1.1 km', icon: 'fa-subway' }
        ];
    }

    // Populate the UI
    for (const [id, items] of Object.entries(categories)) {
        const container = document.getElementById(id);
        const listEl = container?.querySelector('.surroundings-list');
        if (listEl) {
            if (items.length > 0) {
                container.style.display = 'block';
                listEl.innerHTML = items.slice(0, 5).map(item => `
                    <div class="surroundings-item">
                        <div class="place-info">
                            <i class="fas ${item.icon}"></i>
                            <span>${item.name}</span>
                        </div>
                        <span class="place-distance">${item.distance}</span>
                    </div>
                `).join('');
            } else {
                container.style.display = 'none';
            }
        }
    }
}

/**
 * Display map preview by address/name search (fallback when no lat/lng)
 * Uses Google Maps embed search — no API key, no CORS issues
 */
function displayMapPreviewByAddress(address) {
    const mapPreview = document.getElementById('mapPreview');
    if (!mapPreview) return;

    const encodedQuery = encodeURIComponent(address);
    mapPreview.innerHTML = `
        <iframe
            width="100%"
            height="100%"
            style="border:0;"
            loading="lazy"
            allowfullscreen
            referrerpolicy="no-referrer-when-downgrade"
            src="https://maps.google.com/maps?q=${encodedQuery}&output=embed"
        ></iframe>
    `;
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
 * Fetch additional photos for Google Places hotels
 * Updates the gallery with real photos from Google Places API
 */
async function fetchGooglePlacePhotos(hotelId) {
    try {
        // Extract place_id from hotel ID (remove 'google_' prefix)
        const placeId = hotelId.replace('google_', '');

        if (!placeId) {
            console.log('No place ID found for Google Places hotel');
            return;
        }

        console.log(`📸 Fetching Google Places photos for: ${placeId}`);

        const result = await HotelAPI.getGooglePlacePhotos(placeId);

        if (result.success && result.data?.photo_urls?.length > 0) {
            // Update the hotelImages array with new photos
            hotelImages = result.data.photo_urls;

            // Update currentHotel images
            if (currentHotel) {
                currentHotel.images = hotelImages;
            }

            // Refresh the photo gallery display
            displayPhotoGallery(hotelImages);

            console.log(`✅ Loaded ${hotelImages.length} photos from Google Places`);
        } else {
            console.log('No additional photos from Google Places');
        }
    } catch (error) {
        console.log('Could not fetch Google Places photos:', error);
        // Keep existing images, no need to show error
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
        early_late: [
            { icon: 'fa-clock', label: 'Early Check-in', value: 'Subject to availability — Contact hotel directly' },
            { icon: 'fa-clock', label: 'Late Check-out', value: 'Subject to availability — Contact hotel directly' }
        ],
        children: [
            { icon: 'fa-child', label: 'Children', value: 'Children of all ages welcome' }
        ],
        pets: [
            { icon: 'fa-paw', label: 'Pets', value: 'Pet policy varies by property — some hotels allow pets with a fee, others do not' }
        ],
        payments: [
            { icon: 'fa-credit-card', label: 'Payment', value: 'Credit/Debit cards accepted' }
        ],
        internet: [
            { icon: 'fa-wifi', label: 'WiFi', value: 'Free WiFi available' }
        ],
        parking: [
            { icon: 'fa-parking', label: 'Parking', value: 'Subject to availability' }
        ],
        mandatory_fees: [],
        optional_fees: [],
        special: []
    };

    displayHotelPolicies(policies);
}

/**
 * Display formatted hotel policies (Expedia Style)
 * Maps ALL backend policy categories to their HTML card elements.
 */
function displayHotelPolicies(policies) {
    // 1. Check-in/Check-out with Progress Bars
    const checkinTime = policies.check_in_time || '14:00';
    const checkoutTime = policies.check_out_time || '11:00';

    const checkinEl = document.getElementById('checkinValue');
    const checkoutEl = document.getElementById('checkoutValue');
    const checkinProgress = document.getElementById('checkinProgress');
    const checkoutProgress = document.getElementById('checkoutProgress');

    if (checkinEl) checkinEl.textContent = `After ${checkinTime}`;
    if (checkoutEl) checkoutEl.textContent = `Until ${checkoutTime}`;

    // Calculate progress (00:00 to 24:00)
    const timeToPercent = (timeStr) => {
        if (!timeStr) return 50;
        const [hours, minutes] = timeStr.split(':').map(Number);
        return ((hours + (minutes || 0) / 60) / 24) * 100;
    };

    if (checkinProgress) checkinProgress.style.width = `${timeToPercent(checkinTime)}%`;
    if (checkoutProgress) checkoutProgress.style.width = `${timeToPercent(checkoutTime)}%`;

    // 2. Paid on the Spot (Pets, Extra Beds, Parking)
    const petsPolicy = policies.pets || [];
    const extraBedsPolicy = policies.extra_beds || policies.children || [];
    const parkingPolicy = policies.parking || [];

    const petsSection = document.getElementById('paidPets');
    const extraBedsSection = document.getElementById('paidExtraBed');
    const parkingSection = document.getElementById('paidParking');
    const paidSection = document.getElementById('paidOnSpot');

    let hasAnyPaid = false;

    if (petsSection) {
        if (petsPolicy.length > 0) {
            petsSection.style.display = 'flex';
            petsSection.querySelector('.paid-item-details').innerHTML = petsPolicy.map(p => `
                <div class="paid-detail-row"><span class="paid-text">${p.value || p}</span></div>
            `).join('');
            hasAnyPaid = true;
        } else {
            petsSection.style.display = 'none';
        }
    }

    if (extraBedsSection) {
        if (extraBedsPolicy.length > 0) {
            extraBedsSection.style.display = 'flex';
            extraBedsSection.querySelector('.paid-item-details').innerHTML = extraBedsPolicy.map(p => `
                <div class="paid-detail-row"><span class="paid-text">${p.value || p}</span></div>
            `).join('');
            hasAnyPaid = true;
        } else {
            extraBedsSection.style.display = 'none';
        }
    }

    if (parkingSection) {
        if (parkingPolicy.length > 0) {
            parkingSection.style.display = 'flex';
            parkingSection.querySelector('.paid-item-details').innerHTML = parkingPolicy.map(p => `
                <div class="paid-detail-row"><span class="paid-text">${p.value || p}</span></div>
            `).join('');
            hasAnyPaid = true;
        } else {
            parkingSection.style.display = 'none';
        }
    }

    if (paidSection) {
        paidSection.style.display = hasAnyPaid ? 'block' : 'none';
    }

    // 3. Additional Information (Mandatory fees, Smoking, Age, Special instructions)
    const additionalInfoContainer = document.getElementById('additionalInfoContent');
    if (additionalInfoContainer) {
        const otherSections = [
            { title: 'Mandatory Fees', data: policies.mandatory_fees },
            { title: 'Optional Charges', data: policies.optional_fees },
            { title: 'Special Instructions', data: policies.special },
            { title: 'Internet', data: policies.internet },
            { title: 'Smoking Policy', data: policies.smoking },
            { title: 'Age Restriction', data: policies.age_restriction },
            { title: 'Other Policies', data: policies.other }
        ];

        let additionalHtml = '';
        otherSections.forEach(section => {
            if (section.data && section.data.length > 0) {
                additionalHtml += `
                    <div class="info-block" style="margin-bottom: 16px;">
                        <strong style="display: block; margin-bottom: 4px; color: #111827;">${section.title}</strong>
                        <ul style="padding-left: 20px; color: #4b5563;">
                            ${section.data.map(item => `<li>${item.value || item}</li>`).join('')}
                        </ul>
                    </div>
                `;
            }
        });

        if (additionalHtml) {
            additionalInfoContainer.innerHTML = additionalHtml;
        } else {
            document.getElementById('additionalInfoSection').style.display = 'none';
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
 * Display room rates (Expedia / RateHawk Style)
 *
 * Strategy:
 *  - If we received MULTIPLE real rates from the API → show each one directly
 *    with its authentic cancellation policy from the ETG response.
 *  - If we only have ONE rate (demo / Google hotel fallback) → expand it into
 *    several realistic room-type variants, each with industry-standard
 *    cancellation policies (free-cancel on most, non-refundable on cheapest).
 */
function displayRates(rates) {
    const container = document.getElementById('ratesList');
    if (!container) return;

    container.innerHTML = '';

    if (!rates || rates.length === 0) {
        container.innerHTML = '<p class="no-rates" style="text-align: center; padding: 40px; color: #6b7280;">No rooms available for selected dates.</p>';
        return;
    }

    // Sort by price ascending
    rates.sort((a, b) => (a.price || 0) - (b.price || 0));

    // ── CASE A: multiple real ETG rates ────────────────────────────────────
    // Each rate already has its own API-sourced cancellation_info — render directly.
    if (rates.length > 1) {
        const ratesToShow = rates.slice(0, 20);
        const badges = ['Cheapest Option', 'Best Seller', 'Great Value', 'Popular', 'Upgrade your stay', 'Limited Availability'];
        ratesToShow.forEach((rate, index) => {
            const badge = index === 0 ? 'Cheapest Option' : badges[index % badges.length];
            const card = createRateCard(rate, index, badge);
            container.appendChild(card);
        });
        updateMainCancellationPolicy(rates);
        return;
    }

    // ── CASE B: single/demo rate → expand into realistic tiers ────────────
    const baseRate = rates[0];
    const basePrice = baseRate.price || 5000;

    // Free-cancellation deadline: 72 hours before check-in (industry standard)
    const freeCancelDate = new Date();
    if (searchParams?.checkin) {
        freeCancelDate.setTime(new Date(searchParams.checkin + 'T14:00:00').getTime() - 72 * 60 * 60 * 1000);
    } else {
        freeCancelDate.setDate(freeCancelDate.getDate() + 3);
    }
    const freeCancelStr = freeCancelDate.toLocaleDateString('en-US', { weekday: 'short', month: 'short', day: 'numeric', year: 'numeric' }) + ', ' + freeCancelDate.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }) + ' (UTC+0)';

    function makeFreeCancelInfo(deadline) {
        return {
            is_free_cancellation: true,
            free_cancellation_formatted: { datetime: deadline },
            description: `Free cancellation until ${deadline}. After this time, the full charge applies.`,
            policies: [
                { type: 'free', penalty_amount: '0' },
                { type: 'full_penalty', start_formatted: deadline, penalty_amount: String(basePrice * (searchParams ? Math.max(1, Math.round((new Date(searchParams.checkout) - new Date(searchParams.checkin)) / 86400000)) : 1)) }
            ]
        };
    }

    function makeNonRefundInfo() {
        return {
            is_free_cancellation: false,
            free_cancellation_formatted: null,
            description: 'This rate is non-refundable. No refund will be provided for cancellations or no-shows.',
            policies: [{ type: 'full_penalty', start_formatted: 'At time of booking', penalty_amount: '100%' }]
        };
    }

    // Room tier definitions — mirrors what real hotels publish
    const roomTiers = [
        {
            name: 'Standard Room',
            badge: 'Non-refundable deal',
            priceMultiplier: 1.0,
            mealPlan: 'nomeal',
            mealDisplay: 'Room Only (No Meals)',
            cancellable: false,   // ← cheapest non-refundable option (like Booking.com)
            bedType: '1 Queen Bed',
            size: 250,
            sleeps: 2,
            viewType: null
        },
        {
            name: 'Standard Room',
            badge: 'Free cancellation',
            priceMultiplier: 1.08,
            mealPlan: 'nomeal',
            mealDisplay: 'Room Only (No Meals)',
            cancellable: true,    // ← slightly pricier, fully refundable
            bedType: '1 Queen Bed',
            size: 250,
            sleeps: 2,
            viewType: null
        },
        {
            name: 'Deluxe Room',
            badge: 'Popular · Free cancellation',
            priceMultiplier: 1.3,
            mealPlan: 'breakfast',
            mealDisplay: 'Breakfast Included',
            cancellable: true,
            bedType: '1 King Bed',
            size: 320,
            sleeps: 2,
            viewType: 'City view'
        },
        {
            name: 'Superior Room',
            badge: 'Best seller · Free cancellation',
            priceMultiplier: 1.5,
            mealPlan: 'breakfast',
            mealDisplay: 'Breakfast Included',
            cancellable: true,
            bedType: '2 Double Beds',
            size: 360,
            sleeps: 3,
            viewType: 'Garden view'
        },
        {
            name: 'Junior Suite',
            badge: 'Spacious · Free cancellation',
            priceMultiplier: 1.85,
            mealPlan: 'half-board',
            mealDisplay: 'Half Board (Breakfast + Dinner)',
            cancellable: true,
            bedType: '1 King Bed',
            size: 480,
            sleeps: 3,
            viewType: 'Premium view'
        },
        {
            name: 'Executive Suite',
            badge: 'Luxury · All inclusive',
            priceMultiplier: 2.5,
            mealPlan: 'all-inclusive',
            mealDisplay: 'All Inclusive',
            cancellable: true,
            bedType: '1 King Bed + Living Area',
            size: 650,
            sleeps: 4,
            viewType: 'Panoramic view'
        }
    ];

    const roomImages = {
        'Standard Room': ['https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600'],
        'Deluxe Room': ['https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600'],
        'Superior Room': ['https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600'],
        'Junior Suite': ['https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600'],
        'Executive Suite': ['https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=600']
    };

    roomTiers.forEach((tier, i) => {
        const tierPrice = Math.round(basePrice * tier.priceMultiplier);
        const cancelInfo = tier.cancellable ? makeFreeCancelInfo(freeCancelStr) : makeNonRefundInfo();

        const modifiedRate = {
            ...baseRate,
            room_name: tier.name,
            price: tierPrice,
            original_price: Math.round(tierPrice * 1.25),
            meal: tier.mealPlan,
            meal_plan: tier.mealPlan,
            meal_info: {
                value: tier.mealPlan,
                display_name: tier.mealDisplay,
                has_breakfast: tier.mealPlan !== 'nomeal',
                no_child_meal: false,
                is_fixed_count: false
            },
            cancellation_info: cancelInfo,
            room_static: {
                matched: true,
                images: roomImages[tier.name] || roomImages['Standard Room']
            },
            _roomTypeConfig: {
                ...tier,
                features: ['hasWifi', 'hasAC',
                    tier.priceMultiplier >= 1.3 ? 'hasMiniFridge' : null,
                    tier.viewType ? 'hasView' : null
                ].filter(Boolean)
            }
        };

        const card = createRateCard(modifiedRate, i, tier.badge);
        container.appendChild(card);
    });

    // Update the Policies tab cancellation summary using the (virtual) refundable rates
    updateMainCancellationPolicy(roomTiers.filter(t => t.cancellable).map(t => ({
        cancellation_info: makeFreeCancelInfo(freeCancelStr)
    })));
}

/**
 * Update the main cancellation policy summary in the Policies tab
 */
function updateMainCancellationPolicy(rates) {
    const titleEl = document.getElementById('propertyRefundTitle');
    const subtitleEl = document.getElementById('propertyRefundSubtitle');
    const descEl = document.getElementById('propertyRefundDescription');

    if (!titleEl || !rates || rates.length === 0) return;

    const freeRates = rates.filter(r => r.cancellation_info?.is_free_cancellation);

    if (freeRates.length > 0) {
        const deadline = freeRates[0].cancellation_info.free_cancellation_formatted;
        const dateStr = deadline?.datetime || deadline || '';

        titleEl.textContent = dateStr ? `Fully refundable before ${dateStr}` : 'Free cancellation available';
        subtitleEl.textContent = 'Cancellations or changes made after this time are subject to a fee.';
        if (descEl) descEl.innerHTML = freeRates[0].cancellation_info.description || 'Free cancellation available on most room types. Non-refundable discounted rates also available.';

        const statusBox = titleEl.closest('.policy-status');
        if (statusBox) {
            statusBox.className = 'policy-status free';
            statusBox.style.background = '#f0fdf4';
            statusBox.style.border = '1px solid #bbf7d0';
            const icon = statusBox.querySelector('i');
            if (icon) { icon.className = 'fas fa-check-circle'; icon.style.color = '#059669'; }
        }
    } else {
        titleEl.textContent = 'Non-refundable';
        if (subtitleEl) subtitleEl.textContent = 'This booking is non-refundable.';
        if (descEl) descEl.textContent = 'The property does not offer refunds for cancellations or changes.';

        const statusBox = titleEl.closest('.policy-status');
        if (statusBox) {
            statusBox.className = 'policy-status non-refundable';
            statusBox.style.background = '#fef2f2';
            statusBox.style.border = '1px solid #fecaca';
            const icon = statusBox.querySelector('i');
            if (icon) { icon.className = 'fas fa-exclamation-circle'; icon.style.color = '#dc2626'; }
        }
    }
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
function createRateCard(rate, index, customBadge = null) {
    const card = document.createElement('div');
    card.className = 'rate-card';
    card.dataset.rateIndex = index;
    card.dataset.basePrice = rate.price; // used by updateExtras when toggling add-ons

    const price = rate.price;
    const priceFormatted = HotelUtils.formatPrice(price);
    const originalPrice = rate.original_price || Math.round(price * 1.15);
    const originalPriceFormatted = HotelUtils.formatPrice(originalPrice);
    const discount = originalPrice - price;
    const discountFormatted = HotelUtils.formatPrice(discount);

    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = HotelUtils.formatPrice(price * nights);
    const originalTotal = HotelUtils.formatPrice(originalPrice * nights);

    // Use custom badge if provided, otherwise use defaults
    const popularityBadges = ['Popular among travelers', 'Upgrade your stay', 'Great value', 'Best seller'];
    const popularityBadge = customBadge || (index < popularityBadges.length ? popularityBadges[index] : '');
    const badgeClass = index === 0 ? 'popular' : (index === 1 ? 'upgrade' : 'value');

    // Store rate data on card for showRoomDetails to read
    try { card.dataset.rateJson = JSON.stringify(rate); } catch (e) { }

    // Room static data
    const roomStatic = rate.room_static || {};
    const roomImages = roomStatic.images || [];
    const roomName = rate.room_name || roomStatic.room_name || 'Standard Room';

    // Get room type config if available
    const roomTypeConfig = rate._roomTypeConfig || {};

    // Room features - use config if available, otherwise use defaults
    const roomSize = roomTypeConfig.size || roomStatic.room_size || rate.room_size || Math.floor(Math.random() * 200 + 150);
    const sleepsCount = roomTypeConfig.sleeps || roomStatic.max_occupancy || rate.max_occupancy || (searchParams?.adults || 2);
    const bedType = roomTypeConfig.bedType || roomStatic.bed_type || rate.bed_type || getBedType(roomName);

    // Amenities for feature list - use config features if available
    const configFeatures = roomTypeConfig.features || [];
    const hasParking = configFeatures.includes('hasParking') || roomStatic.amenities?.includes('parking') || rate.features?.includes('Parking') || Math.random() > 0.3;
    const hasWifi = configFeatures.includes('hasWifi') || roomStatic.amenities?.includes('wifi') || rate.features?.includes('Free WiFi') || true;
    const hasAC = configFeatures.includes('hasAC') || roomStatic.amenities?.includes('air_conditioning') || Math.random() > 0.4;
    const hasMiniFridge = configFeatures.includes('hasMiniFridge') || roomStatic.amenities?.includes('minibar') || Math.random() > 0.5;
    const hasView = configFeatures.includes('hasView') || roomStatic.amenities?.includes('view') || roomName.toLowerCase().includes('view');

    // Room image HTML with carousel
    let roomImageHtml = '';
    const imageCount = roomImages.length || Math.floor(Math.random() * 10 + 5);
    const mainImage = roomImages[0] || `https://images.unsplash.com/photo-${1566073771259 + index}-6a8506099945?w=600`;

    roomImageHtml = `
        <div class="room-image-carousel" data-index="0" data-images='${JSON.stringify(roomImages.slice(0, 5))}'>
            ${popularityBadge ? `<div class="room-popularity-badge ${badgeClass}">${popularityBadge}</div>` : ''}
            <button class="carousel-nav prev" onclick="navigateRoomImage(this, -1)"><i class="fas fa-chevron-left"></i></button>
            <div class="room-carousel-image" style="background-image: url('${mainImage}');"></div>
            <button class="carousel-nav next" onclick="navigateRoomImage(this, 1)"><i class="fas fa-chevron-right"></i></button>
            <span class="room-image-count"><i class="fas fa-camera"></i> ${imageCount}</span>
        </div>
    `;

    // Features grid - use room type config view if available
    const viewType = roomTypeConfig.viewType || getViewType(roomName);

    // Meal info display — use meal_data.value via meal_info (never deprecated `meal` field)
    const mealInfo = rate.meal_info || {};
    const mealCode = mealInfo.value || rate.meal_plan || rate.meal || 'nomeal';
    const isMealIncluded = mealCode !== 'nomeal' && mealCode !== 'room-only';
    const hasBreakfastIncluded = mealCode.toLowerCase().includes('breakfast') ||
        mealCode.toLowerCase().includes('board') ||
        mealCode.toLowerCase().includes('all-inclusive');

    // Derive number of children from search session for no_child_meal warning
    const searchData = SearchSession.getSearchParams() || {};
    const roomGuests = (searchData.rooms || [{}])[0] || {};
    const numChildren = (roomGuests.children || []).length;

    // Build meal badge + child warning + fixed-count note via shared utility
    const mealBadgeHtml = HotelUtils.getMealInfoHtml(rate, numChildren);


    let featuresHtml = `
        ${mealBadgeHtml}
        <div class="room-features-grid">
            ${hasView && viewType ? `<span class="room-feature view"><i class="fas fa-mountain"></i> ${viewType}</span>` : ''}
            ${hasParking ? `<span class="room-feature parking"><i class="fas fa-parking"></i> Free self parking</span>` : ''}
            <span class="room-feature size"><i class="fas fa-ruler-combined"></i> ${roomSize} sq ft</span>
            <span class="room-feature sleeps"><i class="fas fa-users"></i> Sleeps ${sleepsCount}</span>
            <span class="room-feature bed"><i class="fas fa-bed"></i> ${bedType}</span>
            <span class="room-feature paylater"><i class="fas fa-check"></i> Reserve now, pay later</span>
            ${hasWifi ? `<span class="room-feature wifi"><i class="fas fa-wifi"></i> Free WiFi</span>` : ''}
        </div>
    `;

    // Featured amenity box (show one highlighted amenity)
    let featuredAmenityHtml = '';
    if (hasAC) {
        featuredAmenityHtml = `
            <div class="featured-amenity-box">
                <i class="fas fa-snowflake"></i>
                <span>Air conditioning</span>
            </div>
        `;
    } else if (hasMiniFridge) {
        featuredAmenityHtml = `
            <div class="featured-amenity-box">
                <i class="fas fa-door-closed"></i>
                <span>Mini-fridge</span>
            </div>
        `;
    }

    // ── Cancellation Policy Section (clean header only) ────────────────────
    const cancellationInfo = rate.cancellation_info || {};

    let refundableHtml = `
        <div class="cancellation-policy-section">
            <div class="cp-header">
                <span class="cp-title">Cancellation policy</span>
                <a class="cp-more-details" onclick="showCancellationModal(${index})">More details on all policy options <i class="fas fa-info-circle"></i></a>
            </div>
        </div>
    `;

    // Extras section (Breakfast add-on) - uses mealInfo and hasBreakfastIncluded declared above
    const breakfastPrice = Math.floor(price * 0.05) + 10; // ~5% of room price + base
    const breakfastPriceFormatted = HotelUtils.formatPrice(breakfastPrice);

    let extrasHtml = '';
    if (!hasBreakfastIncluded) {
        extrasHtml = `
            <div class="extras-section">
                <div class="extras-header">
                    <span class="extras-title">Extras</span>
                    <span class="extras-price-label">per night</span>
                </div>
                <label class="extra-option selected">
                    <input type="radio" name="extras_${index}" value="none" checked onchange="updateExtras(${index}, 'none', 0)">
                    <span class="extra-radio"></span>
                    <span class="extra-name">No extras</span>
                    <span class="extra-price">+ ₹0</span>
                </label>
                <label class="extra-option">
                    <input type="radio" name="extras_${index}" value="breakfast" onchange="updateExtras(${index}, 'breakfast', ${breakfastPrice})">
                    <span class="extra-radio"></span>
                    <span class="extra-name">Breakfast</span>
                    <span class="extra-price">+ ${breakfastPriceFormatted}</span>
                </label>
            </div>
        `;
    } else {
        extrasHtml = `
            <div class="included-meal-badge">
                <i class="fas fa-utensils"></i> ${mealInfo.display_name || 'Breakfast included'}
            </div>
        `;
    }

    // Urgency notice (randomly show for some rooms)
    const showUrgency = Math.random() > 0.6;
    const roomsLeft = Math.floor(Math.random() * 4) + 1;
    const urgencyHtml = showUrgency ? `<span class="urgency-notice">We have ${roomsLeft} left</span>` : '';

    // Tax info display - simplify to "Includes all taxes and fees" as per user requirement
    let taxNoteHtml = '<small class="taxes-note" style="color:#059669"><i class="fas fa-check-circle"></i> Includes all taxes and fees</small>';

    const taxInfo = rate.tax_info || {};
    const nonIncludedTaxes = taxInfo.non_included_taxes || [];

    // Even if there are non-included taxes, we want to reassure the user 
    // or indicate they are already accounted for in the grand total display.
    if (nonIncludedTaxes.length > 0) {
        taxNoteHtml = `
            <div style="margin-top:6px;padding:8px 10px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
                <div style="font-size:0.78rem;font-weight:600;color:#166534;margin-bottom:2px;">
                    <i class="fas fa-check-circle"></i> All-inclusive pricing
                </div>
                <div style="font-size:0.72rem;color:#15803d;">Includes all taxes and fees. No additional amount will be charged at the property.</div>
            </div>
        `;
    }

    // Build the card HTML
    card.innerHTML = `
        ${roomImageHtml}
        <div class="rate-card-content">
            <div class="rate-main-info">
                <h3 class="rate-room-name">${roomName}</h3>
                
                ${featuresHtml}
                
                ${featuredAmenityHtml}
                
                ${refundableHtml}
                
                <a class="more-details-link" onclick="showRoomDetails(${index})">More details <i class="fas fa-chevron-right"></i></a>
                
                ${extrasHtml}
            </div>

            <div class="rate-price-action">
                <div class="discount-row">
                    ${urgencyHtml}
                    <span class="discount-badge">${discountFormatted} off</span>
                </div>
                
                <div class="price-display">
                    <div class="nightly-price">${priceFormatted} <small>nightly</small></div>
                    <div class="total-price-row">
                        <span class="strikethrough-price">${originalTotal}</span>
                        <span class="total-price">${totalPrice} <small>total</small></span>
                    </div>
                    ${taxNoteHtml}
                </div>

                <button class="reserve-btn" data-rate-index="${index}">
                    Reserve
                </button>
                <small class="no-charge-note">You will not be charged yet</small>
            </div>
        </div>
    `;

    card.querySelector('.reserve-btn').addEventListener('click', () => {
        selectRate(rate, index);
    });

    return card;
}

// Helper function to get bed type from room name
function getBedType(roomName) {
    const name = roomName.toLowerCase();
    if (name.includes('king')) return '1 King Bed';
    if (name.includes('queen')) return '1 Queen Bed';
    if (name.includes('twin')) return '2 Twin Beds';
    if (name.includes('double')) return '2 Double Beds';
    if (name.includes('family') || name.includes('quadruple')) return '2 King Beds';
    if (name.includes('suite')) return '1 King Bed';
    return '1 King Bed';
}

// Helper function to get view type
function getViewType(roomName) {
    const name = roomName.toLowerCase();
    if (name.includes('garden')) return 'Garden view';
    if (name.includes('ocean') || name.includes('sea')) return 'Ocean view';
    if (name.includes('city')) return 'City view';
    if (name.includes('pool')) return 'Pool view';
    if (name.includes('mountain')) return 'Mountain view';
    return 'Room view';
}

// Navigate room image carousel
function navigateRoomImage(btn, direction) {
    const carousel = btn.closest('.room-image-carousel');
    const imageEl = carousel.querySelector('.room-carousel-image');
    const images = JSON.parse(carousel.dataset.images || '[]');

    if (images.length <= 1) return;

    let currentIndex = parseInt(carousel.dataset.index || 0);
    currentIndex = (currentIndex + direction + images.length) % images.length;
    carousel.dataset.index = currentIndex;

    imageEl.style.backgroundImage = `url('${images[currentIndex]}')`;
}

// Update extras selection and visually update card prices
function updateExtras(rateIndex, extraType, extraPrice) {
    const card = document.querySelector(`.rate-card[data-rate-index="${rateIndex}"]`);
    if (!card) return;

    // Update selected state
    card.querySelectorAll('.extra-option').forEach(opt => opt.classList.remove('selected'));
    const selectedInput = card.querySelector(`input[value="${extraType}"]`);
    if (selectedInput) selectedInput.closest('.extra-option').classList.add('selected');

    // Store extra selection for booking
    if (!window.rateExtras) window.rateExtras = {};
    window.rateExtras[rateIndex] = { type: extraType, price: extraPrice };

    // Update the card's displayed prices to include the extra
    const baseNightly = parseFloat(card.dataset.basePrice || 0);
    if (!baseNightly) return;  // base price not set yet — card will read it on reserve

    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const newNightly = baseNightly + extraPrice;
    const newTotal = newNightly * nights;

    const nightlyEl = card.querySelector('.nightly-price');
    const totalEl = card.querySelector('.total-price');
    if (nightlyEl) nightlyEl.innerHTML = `${HotelUtils.formatPrice(newNightly)} <small>nightly</small>`;
    if (totalEl) totalEl.innerHTML = `${HotelUtils.formatPrice(newTotal)} <small>total</small>`;
}

// Show room details modal / overlay panel
function showRoomDetails(rateIndex) {
    // Retrieve rate from the card's stored data attribute
    const card = document.querySelector(`.rate-card[data-rate-index="${rateIndex}"]`);
    if (!card) return;

    // We reconstruct the rate from data tags on the card
    // (the full rate object is encoded as JSON in a data attribute by createRateCard)
    let rate;
    try {
        rate = JSON.parse(card.dataset.rateJson || '{}');
    } catch (e) {
        rate = {};
    }

    const cancelInfo = rate.cancellation_info || {};
    const isFreeCancellation = cancelInfo.is_free_cancellation;
    const deadline = cancelInfo.free_cancellation_formatted?.datetime || cancelInfo.free_cancellation_formatted || '';
    const mealDisplay = rate.meal_info?.display_name || 'Room Only';
    const roomName = rate.room_name || 'Room';

    // Build policy HTML
    let policyHtml;
    if (isFreeCancellation) {
        policyHtml = `
            <div style="display:flex;align-items:flex-start;gap:12px;padding:16px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;margin-bottom:16px;">
                <i class="fas fa-check-circle" style="color:#059669;font-size:1.4rem;margin-top:2px;"></i>
                <div>
                    <strong style="color:#065f46;font-size:1rem;">Free Cancellation</strong>
                    <p style="margin:4px 0 0;color:#047857;font-size:0.9rem;">
                        Cancel for free before <b>${deadline}</b>.<br>
                        After this deadline, the full room charge applies.
                    </p>
                </div>
            </div>`;
    } else {
        policyHtml = `
            <div style="display:flex;align-items:flex-start;gap:12px;padding:16px;background:#fef2f2;border:1px solid #fecaca;border-radius:10px;margin-bottom:16px;">
                <i class="fas fa-exclamation-circle" style="color:#dc2626;font-size:1.4rem;margin-top:2px;"></i>
                <div>
                    <strong style="color:#7f1d1d;font-size:1rem;">Non-refundable rate</strong>
                    <p style="margin:4px 0 0;color:#991b1b;font-size:0.9rem;">
                        ${cancelInfo.description || 'This rate cannot be cancelled or refunded once booked. No-shows will be charged the full amount.'}
                    </p>
                </div>
            </div>`;
    }

    // Build cancellation schedule if available
    let scheduleHtml = '';
    const policies = cancelInfo.policies || [];
    if (policies.length > 0) {
        scheduleHtml = `
            <div style="margin-bottom:16px;">
                <h4 style="font-size:0.9rem;color:#374151;margin-bottom:10px;display:flex;align-items:center;gap:8px;">
                    <i class="fas fa-calendar-alt" style="color:#6366f1;"></i> Cancellation Schedule
                </h4>
                <table style="width:100%;border-collapse:collapse;font-size:0.85rem;">
                    <thead>
                        <tr style="background:#f9fafb;">
                            <th style="text-align:left;padding:8px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Period</th>
                            <th style="text-align:right;padding:8px;border-bottom:1px solid #e5e7eb;color:#6b7280;">Penalty</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${policies.map(p => {
            const isFree = p.type === 'free' || p.penalty_amount === '0' || p.penalty_amount === 0;
            const startStr = p.start_formatted || 'Now';
            const penaltyStr = isFree ? '<span style="color:#059669">No charge</span>' : `<span style="color:#dc2626">${p.penalty_amount}</span>`;
            return `<tr>
                                <td style="padding:8px;border-bottom:1px solid #f3f4f6;">${isFree ? 'Until ' + (p.end_formatted || deadline) : 'From ' + startStr}</td>
                                <td style="padding:8px;border-bottom:1px solid #f3f4f6;text-align:right;">${penaltyStr}</td>
                            </tr>`;
        }).join('')}
                    </tbody>
                </table>
            </div>`;
    }

    // Inject overlay into page if not already present
    let overlay = document.getElementById('rateDetailsOverlay');
    if (!overlay) {
        overlay = document.createElement('div');
        overlay.id = 'rateDetailsOverlay';
        overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:9999;display:flex;align-items:center;justify-content:center;padding:20px;';
        overlay.addEventListener('click', e => { if (e.target === overlay) overlay.remove(); });
        document.body.appendChild(overlay);
    } else {
        overlay.style.display = 'flex';
    }

    overlay.innerHTML = `
        <div style="background:#fff;border-radius:16px;max-width:520px;width:100%;max-height:85vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);">
            <!-- Header -->
            <div style="display:flex;justify-content:space-between;align-items:center;padding:20px 24px;border-bottom:1px solid #e5e7eb;position:sticky;top:0;background:#fff;border-radius:16px 16px 0 0;">
                <div>
                    <h3 style="margin:0;font-size:1.1rem;color:#111827;">${roomName}</h3>
                    <p style="margin:4px 0 0;font-size:0.85rem;color:#6b7280;"><i class="fas fa-utensils" style="margin-right:5px;"></i>${mealDisplay}</p>
                </div>
                <button onclick="document.getElementById('rateDetailsOverlay').remove()"
                    style="background:none;border:none;font-size:1.4rem;cursor:pointer;color:#9ca3af;line-height:1;padding:4px 8px;">&times;</button>
            </div>

            <!-- Body -->
            <div style="padding:24px;">
                <h4 style="font-size:1rem;color:#111827;margin-bottom:12px;"><i class="fas fa-undo" style="margin-right:8px;color:#6366f1;"></i>Cancellation Policy</h4>
                ${policyHtml}
                ${scheduleHtml}

                <div style="padding:14px;background:#fffbeb;border:1px solid #fde68a;border-radius:10px;margin-bottom:16px;font-size:0.85rem;color:#92400e;">
                    <i class="fas fa-info-circle" style="margin-right:6px;"></i>
                    <strong>Important:</strong> Cancellation times are based on the property's local time zone. We recommend cancelling well before the deadline to avoid charges.
                </div>

                <div style="padding:14px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:10px;font-size:0.85rem;color:#0369a1;">
                    <i class="fas fa-shield-alt" style="margin-right:6px;"></i>
                    <strong>Price Guarantee:</strong> The price you see includes all taxes and service fees. No hidden charges.
                </div>
            </div>

            <!-- Footer -->
            <div style="padding:16px 24px;border-top:1px solid #e5e7eb;display:flex;justify-content:space-between;align-items:center;">
                <div>
                    <div style="font-size:1.3rem;font-weight:700;color:#111827;">${HotelUtils.formatPrice(rate.price)}</div>
                    <div style="font-size:0.8rem;color:#6b7280;">per night · all inclusive</div>
                </div>
                <button onclick="document.getElementById('rateDetailsOverlay').remove(); selectRate(${JSON.stringify({}).replace ? 'window.__rateForModal' : 'null'}, ${rateIndex});"
                    style="padding:12px 24px;background:linear-gradient(135deg,#2563eb,#1d4ed8);color:#fff;border:none;border-radius:10px;font-weight:600;cursor:pointer;font-size:0.95rem;">
                    Select This Room
                </button>
            </div>
        </div>`;

    // Store rate for the "Select This Room" button in the modal footer
    window.__rateForModal = rate;
    // Patch the select button now that we know the rate
    overlay.querySelector('button[onclick*="selectRate"]').onclick = () => {
        overlay.remove();
        selectRate(rate, rateIndex);
    };
}


/**
 * Show Cancellation Policies Modal (Booking.com style)
 * Opens a modal with tabs for Non-refundable and Fully refundable options,
 * each with a visual timeline and detailed policy description.
 */
function showCancellationModal(rateIndex) {
    // Get rate data from the card
    const card = document.querySelector(`.rate-card[data-rate-index="${rateIndex}"]`);
    let rate = {};
    try { rate = JSON.parse(card?.dataset?.rateJson || '{}'); } catch (e) { }

    const cancellationInfo = rate.cancellation_info || {};
    const deadline = cancellationInfo.free_cancellation_formatted;
    const dateStr = deadline ? (deadline.datetime || deadline) : '';

    // Parse free cancel date for display
    let freeCancelShortDate = '';
    let freeCancelFullDate = '';
    let checkinShortDate = '';

    if (dateStr) {
        try {
            const d = new Date(dateStr.replace(/\(UTC.*\)/, '').trim());
            if (!isNaN(d.getTime())) {
                freeCancelShortDate = d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                freeCancelFullDate = d.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
            } else {
                const match = dateStr.match(/(\d{1,2}\s\w{3}\s\d{4})/);
                if (match) {
                    const d2 = new Date(match[1]);
                    if (!isNaN(d2.getTime())) {
                        freeCancelShortDate = d2.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
                        freeCancelFullDate = d2.toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
                    }
                }
            }
        } catch (e) { }
        if (!freeCancelShortDate) {
            freeCancelShortDate = dateStr.split(',')[0] || dateStr;
            freeCancelFullDate = dateStr;
        }
    }

    if (searchParams?.checkin) {
        try {
            const ci = new Date(searchParams.checkin);
            checkinShortDate = ci.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
        } catch (e) { }
    }

    // Remove any existing modal
    const existing = document.getElementById('cancellationPolicyModal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'cancellationPolicyModal';
    modal.className = 'cp-modal-overlay';
    modal.innerHTML = `
        <div class="cp-modal">
            <div class="cp-modal-header">
                <button class="cp-modal-close" onclick="closeCancellationModal()">
                    <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
                </button>
                <span class="cp-modal-title">Cancellation policies</span>
            </div>

            <div class="cp-modal-body">
                <h2 class="cp-modal-heading">Cancellation policies</h2>

                <!-- Tabs -->
                <div class="cp-tabs">
                    <button class="cp-tab active" data-tab="nonrefund" onclick="switchCancellationTab(this, 'nonrefund')">Non-refundable</button>
                    <button class="cp-tab" data-tab="refundable" onclick="switchCancellationTab(this, 'refundable')">Fully refundable</button>
                </div>

                <!-- Non-refundable Tab Content -->
                <div class="cp-tab-content active" id="cpTabNonrefund">
                    <div class="cp-timeline-box">
                        <div class="cp-timeline-label">No refund</div>
                        <div class="cp-timeline-track">
                            <div class="cp-timeline-dot filled"></div>
                            <div class="cp-timeline-line red"></div>
                            <div class="cp-timeline-dot"></div>
                        </div>
                        <div class="cp-timeline-dates">
                            <span>Today</span>
                            <span>Check-in</span>
                        </div>
                    </div>

                    <div class="cp-policy-detail">
                        <div class="cp-policy-until">
                            <span class="cp-until-label">Until</span>
                            <span class="cp-until-date">${checkinShortDate || 'Check-in'}</span>
                        </div>
                        <div class="cp-policy-info">
                            <h4>No refund</h4>
                            <p>If you change or cancel your booking you will not get a refund or credit to use for a future stay.</p>
                        </div>
                    </div>
                </div>

                <!-- Fully refundable Tab Content -->
                <div class="cp-tab-content" id="cpTabRefundable">
                    <div class="cp-timeline-box">
                        <div class="cp-timeline-label-split">
                            <span class="cp-tl-green">Full refund</span>
                            <span class="cp-tl-red">No refund</span>
                        </div>
                        <div class="cp-timeline-track">
                            <div class="cp-timeline-dot filled green"></div>
                            <div class="cp-timeline-line green" style="flex:1;"></div>
                            <div class="cp-timeline-dot filled red-dot"></div>
                            <div class="cp-timeline-line red" style="flex:0.5;"></div>
                            <div class="cp-timeline-dot"></div>
                        </div>
                        <div class="cp-timeline-dates three">
                            <span>Today</span>
                            <span>${freeCancelShortDate || 'Deadline'}</span>
                            <span>Check-in</span>
                        </div>
                    </div>

                    <div class="cp-policy-detail">
                        <div class="cp-policy-until">
                            <span class="cp-until-label">Before</span>
                            <span class="cp-until-date">${freeCancelShortDate || 'Deadline'}</span>
                        </div>
                        <div class="cp-policy-info">
                            <h4>Full refund</h4>
                            <p>You will get a full refund if you cancel before ${freeCancelFullDate || 'the deadline'}.</p>
                        </div>
                    </div>

                    <div class="cp-policy-detail">
                        <div class="cp-policy-until">
                            <span class="cp-until-label">After</span>
                            <span class="cp-until-date">${freeCancelShortDate || 'Deadline'}</span>
                        </div>
                        <div class="cp-policy-info">
                            <h4>No refund</h4>
                            <p>If you cancel after ${freeCancelFullDate || 'the deadline'}, you will not receive a refund.</p>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    // Close on backdrop click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) closeCancellationModal();
    });

    // Animate in
    requestAnimationFrame(() => modal.classList.add('visible'));
}

function closeCancellationModal() {
    const modal = document.getElementById('cancellationPolicyModal');
    if (modal) {
        modal.classList.remove('visible');
        setTimeout(() => modal.remove(), 300);
    }
}

function switchCancellationTab(btn, tab) {
    // Update tabs
    btn.closest('.cp-tabs').querySelectorAll('.cp-tab').forEach(t => t.classList.remove('active'));
    btn.classList.add('active');

    // Update content
    const modal = btn.closest('.cp-modal-body');
    modal.querySelectorAll('.cp-tab-content').forEach(c => c.classList.remove('active'));
    if (tab === 'nonrefund') {
        modal.querySelector('#cpTabNonrefund').classList.add('active');
    } else {
        modal.querySelector('#cpTabRefundable').classList.add('active');
    }
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
    const selectedCard = document.querySelector(`.rate-card[data-rate-index="${index}"]`);
    if (selectedCard) selectedCard.classList.add('selected');

    // Pick up any extras the user selected (e.g. breakfast add-on)
    const extras = (window.rateExtras && window.rateExtras[index]) || { type: 'none', price: 0 };

    // Calculate totals including extras
    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const baseNightlyPrice = rate.price;
    const extraNightlyPrice = extras.price || 0;
    const nightlyWithExtras = baseNightlyPrice + extraNightlyPrice;
    const totalPrice = nightlyWithExtras * nights;

    // Build the rate object that checkout pages will read
    const rateForCheckout = {
        ...rate,
        // Overwrite price fields to include the extras
        price: nightlyWithExtras,
        base_nightly_price: baseNightlyPrice,
        extra_price: extraNightlyPrice,
        extra_type: extras.type,
        total_price: totalPrice,
        nights: nights,
        // Meal plan may change if breakfast extra was added
        meal_plan: extras.type === 'breakfast' ? 'breakfast' : rate.meal_plan,
        meal_info: extras.type === 'breakfast'
            ? { ...rate.meal_info, value: 'breakfast', display_name: 'Breakfast Included', has_breakfast: true }
            : rate.meal_info,
    };

    // Save to session
    SearchSession.saveSelectedRate(rateForCheckout);
    SearchSession.saveBookingData({
        hotel: currentHotel,
        rate: rateForCheckout,
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
