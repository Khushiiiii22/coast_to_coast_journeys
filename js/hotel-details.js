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
 * Display map preview by address search (fallback when no lat/lng)
 */
function displayMapPreviewByAddress(address) {
    const mapPreview = document.getElementById('mapPreview');
    if (!mapPreview) return;

    // Show a loading state first
    mapPreview.innerHTML = `
        <div style="display:flex;align-items:center;justify-content:center;height:100%;background:#e5e7eb;border-radius:8px;">
            <span style="color:#6b7280;">Loading map...</span>
        </div>
    `;

    // Geocode the address using Nominatim (free, no API key needed)
    const encodedAddress = encodeURIComponent(address);
    fetch(`https://nominatim.openstreetmap.org/search?q=${encodedAddress}&format=json&limit=1`)
        .then(res => res.json())
        .then(data => {
            if (data && data.length > 0) {
                const lat = parseFloat(data[0].lat);
                const lng = parseFloat(data[0].lon);
                displayMapPreview(lat, lng);
            } else {
                // Show a generic map placeholder
                mapPreview.innerHTML = `
                    <div style="display:flex;align-items:center;justify-content:center;height:100%;background:#e5e7eb;border-radius:8px;flex-direction:column;gap:8px;">
                        <i class="fas fa-map-marker-alt" style="font-size:2rem;color:#9ca3af;"></i>
                        <span style="color:#6b7280;font-size:0.9rem;">Map not available</span>
                    </div>
                `;
            }
        })
        .catch(() => {
            mapPreview.innerHTML = `
                <div style="display:flex;align-items:center;justify-content:center;height:100%;background:#e5e7eb;border-radius:8px;flex-direction:column;gap:8px;">
                    <i class="fas fa-map-marker-alt" style="font-size:2rem;color:#9ca3af;"></i>
                    <span style="color:#6b7280;font-size:0.9rem;">Map not available</span>
                </div>
            `;
        });
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
        ],
        mandatory_fees: [
            { icon: 'fa-dollar-sign', label: 'Resort/Facility Fee', value: 'Contact property for mandatory fee details' }
        ],
        optional_fees: [
            { icon: 'fa-money-bill-wave', label: 'Optional Charges', value: 'Additional services available at extra cost upon request' }
        ],
        special: [
            { icon: 'fa-info-circle', label: 'Special Instructions', value: 'Please contact the property for special check-in instructions' }
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
        'early_late': 'policyEarlyLate',
        'children': 'policyChildren',
        'extra_beds': 'policyExtraBeds',
        'pets': 'policyPets',
        'internet': 'policyInternet',
        'parking': 'policyParking',
        'payments': 'policyPayments',
        'meals': 'policyMeals',
        'mandatory_fees': 'policyMandatoryFees',
        'optional_fees': 'policyOptionalFees',
        'special': 'policySpecial',
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

    // Room type templates for Expedia-style variety
    const roomTypes = [
        {
            name: 'Standard Room',
            badge: 'Great value',
            priceMultiplier: 1.0,
            features: ['hasWifi', 'hasAC'],
            size: 250,
            sleeps: 2,
            bedType: '1 Queen Bed',
            viewType: null
        },
        {
            name: 'Deluxe Room',
            badge: 'Popular among travelers',
            priceMultiplier: 1.25,
            features: ['hasWifi', 'hasAC', 'hasMiniFridge', 'hasView'],
            size: 320,
            sleeps: 2,
            bedType: '1 King Bed',
            viewType: 'City view'
        },
        {
            name: 'Prime Room',
            badge: 'Best seller',
            priceMultiplier: 1.45,
            features: ['hasWifi', 'hasAC', 'hasMiniFridge', 'hasView', 'hasParking'],
            size: 380,
            sleeps: 3,
            bedType: '1 King Bed or 2 Queen Beds',
            viewType: 'Garden view'
        },
        {
            name: 'Executive Suite',
            badge: 'Upgrade your stay',
            priceMultiplier: 1.75,
            features: ['hasWifi', 'hasAC', 'hasMiniFridge', 'hasView', 'hasParking'],
            size: 480,
            sleeps: 4,
            bedType: '1 King Bed + Sofa Bed',
            viewType: 'Premium city view'
        },
        {
            name: 'Junior Suite',
            badge: 'Spacious comfort',
            priceMultiplier: 1.55,
            features: ['hasWifi', 'hasAC', 'hasMiniFridge', 'hasView', 'hasParking'],
            size: 420,
            sleeps: 3,
            bedType: '1 King Bed',
            viewType: 'Partial ocean view'
        },
        {
            name: 'Presidential Suite',
            badge: 'Ultimate luxury',
            priceMultiplier: 2.5,
            features: ['hasWifi', 'hasAC', 'hasMiniFridge', 'hasView', 'hasParking'],
            size: 650,
            sleeps: 6,
            bedType: '2 King Beds + Living Area',
            viewType: 'Panoramic view'
        }
    ];

    // If we have actual rates, create multiple room type variations
    const baseRate = rates[0];
    const roomsToShow = Math.min(roomTypes.length, 6);

    for (let i = 0; i < roomsToShow; i++) {
        const roomType = roomTypes[i];

        // Create a modified rate object with room type characteristics
        const modifiedRate = {
            ...baseRate,
            room_name: roomType.name,
            price: Math.round(baseRate.price * roomType.priceMultiplier),
            _roomTypeConfig: roomType
        };

        const card = createRateCard(modifiedRate, i, roomType.badge);
        container.appendChild(card);
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

    // Meal info display
    const mealInfo = rate.meal_info || {};
    const mealDisplay = mealInfo.display_name || '';
    const hasBreakfastIncluded = mealInfo.has_breakfast || rate.meal === 'breakfast' || rate.meal_plan === 'breakfast';
    const mealCode = mealInfo.code || 'nomeal';
    const isMealIncluded = mealCode !== 'nomeal' && mealCode !== 'room-only';

    // Meal badge HTML
    let mealBadgeHtml = '';
    if (isMealIncluded && mealDisplay) {
        mealBadgeHtml = `
            <div style="display:flex;align-items:center;gap:6px;padding:6px 12px;background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-radius:8px;border:1px solid #a7f3d0;margin-bottom:8px;">
                <i class="fas fa-utensils" style="color:#059669;font-size:0.8rem;"></i>
                <span style="color:#065f46;font-size:0.82rem;font-weight:600;">${mealDisplay}</span>
            </div>
        `;
    } else if (hasBreakfastIncluded) {
        mealBadgeHtml = `
            <div style="display:flex;align-items:center;gap:6px;padding:6px 12px;background:linear-gradient(135deg,#ecfdf5,#d1fae5);border-radius:8px;border:1px solid #a7f3d0;margin-bottom:8px;">
                <i class="fas fa-coffee" style="color:#059669;font-size:0.8rem;"></i>
                <span style="color:#065f46;font-size:0.82rem;font-weight:600;">Breakfast Included</span>
            </div>
        `;
    } else {
        mealBadgeHtml = `
            <div style="display:flex;align-items:center;gap:6px;padding:6px 12px;background:#f8fafc;border-radius:8px;border:1px solid #e2e8f0;margin-bottom:8px;">
                <i class="fas fa-utensils" style="color:#94a3b8;font-size:0.8rem;"></i>
                <span style="color:#64748b;font-size:0.82rem;">Room Only (No Meals)</span>
            </div>
        `;
    }

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

    // Cancellation info
    const cancellationInfo = rate.cancellation_info || {};
    let refundableHtml = '';
    let policyDetailsHtml = '';

    // Generate detailed policy tooltips/text
    if (cancellationInfo.policies && cancellationInfo.policies.length > 0) {
        const policyList = cancellationInfo.policies.map(p => {
            if (p.type === 'free') return null;
            const amount = parseFloat(p.penalty_amount);
            const amountFormatted = HotelUtils.formatPrice(amount, p.currency || rate.currency);

            if (p.type === 'full_penalty') {
                return `<li>From ${p.start_formatted || 'booking'}: 100% penalty (${amountFormatted})</li>`;
            } else {
                return `<li>From ${p.start_formatted}: Penalty ${amountFormatted}</li>`;
            }
        }).filter(Boolean).join('');

        if (policyList) {
            policyDetailsHtml = `<ul class="cancellation-details-list">${policyList}</ul>`;
        }
    }

    if (cancellationInfo.is_free_cancellation && cancellationInfo.free_cancellation_formatted) {
        const deadline = cancellationInfo.free_cancellation_formatted;
        // Use either the object (new format) or string (old format)
        const dateStr = deadline.datetime || deadline;

        refundableHtml = `
            <div class="refundable-notice group">
                <span class="refundable-text"><i class="fas fa-info-circle"></i> Fully refundable</span>
                <small>Before ${dateStr}</small>
                
                <div class="cancellation-tooltip">
                    <strong>Cancellation Policy:</strong>
                    ${policyDetailsHtml || 'Free cancellation before deadline.'}
                </div>
            </div>
        `;
    } else if (rate.cancellation === 'free') {
        refundableHtml = `
            <div class="refundable-notice">
                <span class="refundable-text"><i class="fas fa-info-circle"></i> Fully refundable</span>
            </div>
        `;
    } else {
        refundableHtml = `
            <div class="non-refundable-notice group">
                <span class="non-refund-text"><i class="fas fa-ban"></i> Non-refundable</span>
                <div class="cancellation-tooltip">
                    <strong>Cancellation Policy:</strong>
                    ${policyDetailsHtml || 'No refund upon cancellation.'}
                </div>
            </div>
        `;
    }

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

    // Tax info display - use REAL tax data from rate
    let taxNoteHtml = '<small class="taxes-note"><i class="fas fa-check"></i> Total with taxes and fees</small>';

    const taxInfo = rate.tax_info || {};
    const nonIncludedTaxes = taxInfo.non_included_taxes || [];
    const includedTaxes = taxInfo.included_taxes || [];

    if (nonIncludedTaxes.length > 0) {
        // Calculate total non-included tax amount
        let totalNonIncluded = 0;
        const taxDetailsHtml = nonIncludedTaxes.map(tax => {
            const amount = parseFloat(tax.amount || 0);
            totalNonIncluded += amount;
            const displayName = tax.display_name || tax.name || 'Tax';
            const currency = tax.currency_code || 'INR';
            return `<div style="display:flex;justify-content:space-between;font-size:0.72rem;color:#92400e;"><span>${displayName}</span><span>${currency} ${amount.toFixed(2)}</span></div>`;
        }).join('');

        taxNoteHtml = `
            <div style="margin-top:6px;padding:8px 10px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;">
                <div style="font-size:0.78rem;font-weight:600;color:#92400e;margin-bottom:4px;">
                    <i class="fas fa-info-circle"></i> Additional fees payable at property:
                </div>
                ${taxDetailsHtml}
                <div style="font-size:0.7rem;color:#b45309;margin-top:4px;font-style:italic;">These taxes are not included and must be paid at check-in.</div>
            </div>
        `;
    } else if (includedTaxes.length > 0) {
        let totalIncluded = 0;
        includedTaxes.forEach(tax => { totalIncluded += parseFloat(tax.amount || 0); });
        if (totalIncluded > 0) {
            taxNoteHtml = `<small class="taxes-note" style="color:#059669"><i class="fas fa-check-circle"></i> Includes ₹${totalIncluded.toLocaleString('en-IN')} taxes & fees</small>`;
        }
    } else if (rate.tax_info && rate.tax_info.total > 0) {
        const taxAmount = HotelUtils.formatPrice(rate.tax_info.total);
        if (rate.tax_info.included) {
            taxNoteHtml = `<small class="taxes-note"><i class="fas fa-check"></i> Includes ${taxAmount} taxes & fees</small>`;
        } else {
            taxNoteHtml = `<small class="taxes-note" style="color:#d97706"><i class="fas fa-info-circle"></i> + ${taxAmount} taxes & fees due at property</small>`;
        }
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

// Update extras selection
function updateExtras(rateIndex, extraType, extraPrice) {
    const card = document.querySelector(`.rate-card[data-rate-index="${rateIndex}"]`);
    card.querySelectorAll('.extra-option').forEach(opt => opt.classList.remove('selected'));
    card.querySelector(`input[value="${extraType}"]`).closest('.extra-option').classList.add('selected');

    // Store extra selection for booking
    if (!window.rateExtras) window.rateExtras = {};
    window.rateExtras[rateIndex] = { type: extraType, price: extraPrice };
}

// Show room details modal
function showRoomDetails(rateIndex) {
    // Can implement modal with full room details
    console.log('Show details for room', rateIndex);
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
