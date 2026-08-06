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
        if (currentHotel.id && currentHotel.id.startsWith('mock_')) {
            const demoData = generateDemoHotelDetails(currentHotel.id);
            if (!currentHotel.rates || currentHotel.rates.length === 0) {
                currentHotel.rates = demoData.rates;
            }
            if (!currentHotel.images || currentHotel.images.length <= 1) {
                currentHotel.images = [currentHotel.images[0], ...demoData.images.slice(1)];
            }
        }
        displayHotelDetails(currentHotel);

        // For Google Places hotels, fetch additional photos for gallery is completely disabled
        // if (currentHotel.id && currentHotel.id.startsWith('google_')) {
        //     fetchGooglePlacePhotos(currentHotel.id);
        // }
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
                currency: searchParams?.currency || localStorage.getItem('ctc_currency') || 'USD'
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
                currency: 'USD',
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
                currency: 'USD',
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
                currency: 'USD',
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
    let rawImages = hotel.images || (hotel.image ? [hotel.image] : []);
    hotelImages = rawImages.length > 0 
        ? rawImages.map(img => typeof img === 'string' ? img.replace('{size}', '1024x768') : img)
        : ['https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'];

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
    document.getElementById('reviewCount').textContent = `Based on ${hotel.review_count || 0} reviews`;

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

    // Map preview & Attractions
    if (hotel.latitude && hotel.longitude) {
        displayMapPreview(hotel.latitude, hotel.longitude, hotel);
    } else {
        displayMapPreviewByAddress(hotel.address || hotel.name || 'Hotel', hotel);
    }

    // Async static info fetch to enrich surroundings if missing
    if ((!hotel.surroundings || hotel.surroundings.length === 0) && (hotel.id || hotel.hid) && !String(hotel.id || hotel.hid).startsWith('demo_')) {
        const hId = hotel.id || hotel.hid;
        HotelAPI.getHotelInfo(hId).then(res => {
            if (res?.success && res.data) {
                const fetched = res.data;
                hotel.surroundings = fetched.surroundings || fetched.static_data?.surroundings || hotel.surroundings || [];
                hotel.description_struct = fetched.description_struct || fetched.static_data?.description_struct || hotel.description_struct || [];
                if (fetched.latitude && fetched.longitude && (!hotel.latitude || !hotel.longitude)) {
                    hotel.latitude = fetched.latitude;
                    hotel.longitude = fetched.longitude;
                }
                if (hotel.latitude && hotel.longitude) {
                    displayMapPreview(hotel.latitude, hotel.longitude, hotel);
                } else {
                    displayMapPreviewByAddress(hotel.address || hotel.name || 'Hotel', hotel);
                }
            }
        }).catch(err => console.log('Static info fetch for attractions notice:', err));
    }

    // Update rooms section info
    updateRoomsSectionInfo();

    // Update sticky price bar
    updateStickyPriceBar(hotel.rates);

    // Initialize Expedia-style enhancements
    if (typeof ExpediaEnhancements !== 'undefined') {
        ExpediaEnhancements.initialize(hotel);
    }

    // Track recently viewed hotel
    try {
        const RV_KEY = 'ctc_recently_viewed';
        const MAX_VIEWED = 15; // Store 15 to ensure we can display 6 valid ones after filtering
        const viewed = JSON.parse(localStorage.getItem(RV_KEY) || '[]');
        const hotelEntry = {
            id: hotel.id || hotel.hid,
            name: hotel.name,
            image: hotelImages[0] || '',
            star_rating: hotel.star_rating || 0,
            price: hotel.rates && hotel.rates[0] ? hotel.rates[0].price : null,
            address: hotel.address || '',
            timestamp: Date.now()
        };
        // Remove if already exists
        const filtered = viewed.filter(v => v.id !== hotelEntry.id);
        filtered.unshift(hotelEntry);
        localStorage.setItem(RV_KEY, JSON.stringify(filtered.slice(0, MAX_VIEWED)));
    } catch (e) {
        console.log('Could not save recently viewed:', e);
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

    function scrollToRooms() {
        const roomsSection = document.getElementById('rooms') || document.getElementById('roomsSection');
        if (roomsSection) {
            const headerOffset = 140;
            const elementPosition = roomsSection.getBoundingClientRect().top;
            const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
            window.scrollTo({
                top: offsetPosition,
                behavior: 'smooth'
            });
        }
    }

    // Reserve button
    const reserveBtn = document.getElementById('quickReserveBtn');
    if (reserveBtn) {
        reserveBtn.addEventListener('click', scrollToRooms);
    }

    // Sticky reserve button
    const stickyReserveBtn = document.getElementById('stickyReserveBtn');
    if (stickyReserveBtn) {
        stickyReserveBtn.addEventListener('click', scrollToRooms);
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

    // Check for Spa to conditionally show the Featured Spa section
    const spaSection = document.getElementById('featuredSpaAmenity');
    if (spaSection) {
        // Handle both simple array of strings and complex objects
        const hasSpa = amenities.some(a => {
            const spaRegex = /\bspa\b/i;
            if (typeof a === 'string') return spaRegex.test(a);
            if (a && a.id) return spaRegex.test(a.id) || a.id.toLowerCase() === 'health_spa';
            if (a && a.name) return spaRegex.test(a.name);
            return false;
        });
        
        if (hasSpa) {
            spaSection.style.display = 'block';
        } else {
            spaSection.style.display = 'none';
        }
    }

    grid.innerHTML = '';
    amenities.slice(0, 8).forEach(a => {
        const data = amenityData[a] || { icon: 'fa-check', label: a };
        const item = document.createElement('div');
        item.className = 'amenity-item';
        item.innerHTML = `<i class="fas ${data.icon}"></i> <span>${data.label}</span>`;
        grid.appendChild(item);
    });
}

function getAttractionsForHotel(hotelData = {}, lat = null, lng = null, address = '') {
    const staticData = hotelData.static_data || {};
    const rawSurroundings = staticData.surroundings || hotelData.surroundings || [];
    
    const categories = {
        'categoryNearby': [],
        'categoryInterest': [],
        'categoryAirports': [],
        'categorySubway': []
    };

    function formatDistanceText(distVal, distUnit = 'km') {
        if (!distVal) return 'Nearby';
        let num = parseFloat(distVal);
        if (isNaN(num)) return distVal;
        if (distUnit.toLowerCase() === 'm') num = num / 1000;
        
        if (num <= 1.2) {
            const walkMins = Math.max(2, Math.round(num * 12));
            return `${walkMins} min walk`;
        } else if (num <= 30) {
            const driveMins = Math.max(3, Math.round(num * 2));
            return `${driveMins} min drive`;
        } else {
            const miles = (num * 0.621371).toFixed(1);
            return `${miles} mi / ${num.toFixed(1)} km`;
        }
    }

    // 1. Process explicit surroundings from API
    if (Array.isArray(rawSurroundings) && rawSurroundings.length > 0) {
        rawSurroundings.forEach(place => {
            const name = place.name || place.title || 'Landmark';
            const dist = formatDistanceText(place.distance_value || place.distance, place.distance_unit || 'km');
            const type = (place.type || '').toLowerCase();
            const item = { name, distance: dist, icon: 'fa-map-marker-alt' };

            if (type.includes('airport')) {
                item.icon = 'fa-plane';
                categories.categoryAirports.push(item);
            } else if (type.includes('metro') || type.includes('subway') || type.includes('station') || type.includes('rail')) {
                item.icon = 'fa-subway';
                categories.categorySubway.push(item);
            } else if (type.includes('sight') || type.includes('museum') || type.includes('monument') || type.includes('landmark')) {
                item.icon = 'fa-landmark';
                categories.categoryInterest.push(item);
            } else {
                item.icon = 'fa-walking';
                categories.categoryNearby.push(item);
            }
        });
    }

    // 2. Parse from description_struct if available
    const descStruct = staticData.description_struct || hotelData.description_struct || [];
    if (Array.isArray(descStruct)) {
        descStruct.forEach(block => {
            const title = (block.title || '').toLowerCase();
            if (title.includes('location') || title.includes('nearby') || title.includes('attractions')) {
                (block.paragraphs || []).forEach(p => {
                    if (p.includes('nearby:') || p.includes('Nearby:')) {
                        const parts = p.split(/nearby:|\:/i);
                        if (parts[1]) {
                            parts[1].split(',').forEach(spotName => {
                                const clean = spotName.trim().replace(/\.$/, '');
                                if (clean.length > 2 && clean.length < 50) {
                                    categories.categoryNearby.push({
                                        name: clean,
                                        distance: 'Nearby',
                                        icon: 'fa-walking'
                                    });
                                }
                            });
                        }
                    }
                });
            }
        });
    }

    // 3. Fallback Landmark Engine based on Coordinates & Destination
    const fullText = `${hotelData.name || ''} ${address || ''} ${hotelData.city || ''} ${hotelData.address || ''}`.toLowerCase();
    const curLat = parseFloat(lat || hotelData.latitude);
    const curLng = parseFloat(lng || hotelData.longitude);

    function getDistanceKm(lat1, lon1, lat2, lon2) {
        const R = 6371;
        const dLat = (lat2 - lat1) * Math.PI / 180;
        const dLon = (lon2 - lon1) * Math.PI / 180;
        const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
                  Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
                  Math.sin(dLon/2) * Math.sin(dLon/2);
        return R * (2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a)));
    }

    const cityLandmarks = {
        'bengaluru': [
            { name: 'UB City Mall & Brigade Road', lat: 12.9716, lng: 77.5946, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Commercial Street Shopping', lat: 12.9822, lng: 77.6083, cat: 'categoryNearby', icon: 'fa-walking' },
            { name: 'Cubbon Park & Vidhana Soudha', lat: 12.9763, lng: 77.5929, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Bengaluru Palace', lat: 12.9988, lng: 77.5921, cat: 'categoryInterest', icon: 'fa-archway' },
            { name: 'Kempegowda International Airport (BLR)', lat: 13.1986, lng: 77.7066, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Indiranagar / MG Road Metro Station', lat: 12.9784, lng: 77.6408, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'bangalore': [
            { name: 'UB City Mall & Brigade Road', lat: 12.9716, lng: 77.5946, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Commercial Street Shopping', lat: 12.9822, lng: 77.6083, cat: 'categoryNearby', icon: 'fa-walking' },
            { name: 'Cubbon Park & Vidhana Soudha', lat: 12.9763, lng: 77.5929, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Bengaluru Palace', lat: 12.9988, lng: 77.5921, cat: 'categoryInterest', icon: 'fa-archway' },
            { name: 'Kempegowda International Airport (BLR)', lat: 13.1986, lng: 77.7066, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Indiranagar / MG Road Metro Station', lat: 12.9784, lng: 77.6408, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'mumbai': [
            { name: 'Gateway of India & Taj Palace', lat: 18.9220, lng: 72.8347, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Marine Drive Promenade', lat: 18.9438, lng: 72.8234, cat: 'categoryNearby', icon: 'fa-walking' },
            { name: 'Colaba Causeway Market', lat: 18.9222, lng: 72.8315, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Chhatrapati Shivaji Maharaj Terminus (CSMT)', lat: 18.9400, lng: 72.8353, cat: 'categorySubway', icon: 'fa-subway' },
            { name: 'Chhatrapati Shivaji Intl Airport (BOM)', lat: 19.0896, lng: 72.8656, cat: 'categoryAirports', icon: 'fa-plane' }
        ],
        'delhi': [
            { name: 'Connaught Place Shopping Belt', lat: 28.6315, lng: 77.2167, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'India Gate & Central Vista', lat: 28.6129, lng: 77.2295, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Qutub Minar Complex', lat: 28.5245, lng: 77.1855, cat: 'categoryInterest', icon: 'fa-archway' },
            { name: 'Indira Gandhi International Airport (DEL)', lat: 28.5562, lng: 77.1000, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Rajiv Chowk Metro Station', lat: 28.6328, lng: 77.2197, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'goa': [
            { name: 'Calangute & Baga Beach', lat: 15.5494, lng: 73.7535, cat: 'categoryNearby', icon: 'fa-umbrella-beach' },
            { name: 'Panaji City Promenade', lat: 15.4989, lng: 73.8278, cat: 'categoryNearby', icon: 'fa-walking' },
            { name: 'Basilica of Bom Jesus (Old Goa)', lat: 15.5009, lng: 73.9116, cat: 'categoryInterest', icon: 'fa-church' },
            { name: 'Goa Dabolim Airport (GOI)', lat: 15.3808, lng: 73.8314, cat: 'categoryAirports', icon: 'fa-plane' }
        ],
        'jaipur': [
            { name: 'Hawa Mahal (Palace of Winds)', lat: 26.9239, lng: 75.8267, cat: 'categoryInterest', icon: 'fa-monument' },
            { name: 'City Palace & Jantar Mantar', lat: 26.9258, lng: 75.8237, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Johari Bazaar Shopping', lat: 26.9197, lng: 75.8274, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Jaipur International Airport (JAI)', lat: 26.8242, lng: 75.8122, cat: 'categoryAirports', icon: 'fa-plane' }
        ],
        'agra': [
            { name: 'Taj Mahal', lat: 27.1751, lng: 78.0421, cat: 'categoryInterest', icon: 'fa-gopuram' },
            { name: 'Agra Fort', lat: 27.1795, lng: 78.0211, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Sadar Bazaar Shopping', lat: 27.1610, lng: 78.0100, cat: 'categoryNearby', icon: 'fa-shopping-bag' }
        ],
        'los angeles': [
            { name: 'Beverly Center', lat: 34.0752, lng: -118.3773, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'The Farmers Market & The Grove', lat: 34.0722, lng: -118.3581, cat: 'categoryNearby', icon: 'fa-walking' },
            { name: 'LACMA (Museum of Art)', lat: 34.0639, lng: -118.3592, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Sunset Strip', lat: 34.0909, lng: -118.3847, cat: 'categoryInterest', icon: 'fa-glass-cheers' },
            { name: 'Hollywood Walk of Fame', lat: 34.1016, lng: -118.3268, cat: 'categoryInterest', icon: 'fa-star' },
            { name: 'Los Angeles Intl. Airport (LAX)', lat: 33.9416, lng: -118.4085, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Hollywood Burbank Airport (BUR)', lat: 34.2007, lng: -118.3587, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Wilshire / Western Metro Station', lat: 34.0617, lng: -118.3086, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'new york': [
            { name: 'Times Square', lat: 40.7580, lng: -73.9855, cat: 'categoryNearby', icon: 'fa-city' },
            { name: 'Central Park', lat: 40.7829, lng: -73.9654, cat: 'categoryNearby', icon: 'fa-tree' },
            { name: 'Rockefeller Center', lat: 40.7587, lng: -73.9787, cat: 'categoryInterest', icon: 'fa-building' },
            { name: 'Empire State Building', lat: 40.7484, lng: -73.9857, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'John F. Kennedy Intl Airport (JFK)', lat: 40.6413, lng: -73.7781, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'LaGuardia Airport (LGA)', lat: 40.7769, lng: -73.8740, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: '42 St - Port Authority Bus Terminal', lat: 40.7570, lng: -73.9897, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'paris': [
            { name: 'Eiffel Tower', lat: 48.8584, lng: 2.2945, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Louvre Museum', lat: 48.8606, lng: 2.3376, cat: 'categoryInterest', icon: 'fa-palette' },
            { name: 'Champs-Élysées', lat: 48.8698, lng: 2.3075, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Arc de Triomphe', lat: 48.8738, lng: 2.2950, cat: 'categoryInterest', icon: 'fa-monument' },
            { name: 'Paris Charles de Gaulle Airport (CDG)', lat: 49.0097, lng: 2.5479, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Paris Orly Airport (ORY)', lat: 48.7262, lng: 2.3652, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Franklin D. Roosevelt Metro Station', lat: 48.8692, lng: 2.3099, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'london': [
            { name: 'Big Ben & Parliament', lat: 51.5007, lng: -0.1246, cat: 'categoryInterest', icon: 'fa-clock' },
            { name: 'London Eye', lat: 51.5033, lng: -0.1195, cat: 'categoryInterest', icon: 'fa-landmark' },
            { name: 'Hyde Park', lat: 51.5073, lng: -0.1657, cat: 'categoryNearby', icon: 'fa-tree' },
            { name: 'British Museum', lat: 51.5194, lng: -0.1270, cat: 'categoryInterest', icon: 'fa-university' },
            { name: 'London Heathrow Airport (LHR)', lat: 51.4700, lng: -0.4543, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Victoria Underground Station', lat: 51.4965, lng: -0.1447, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'dubai': [
            { name: 'Burj Khalifa', lat: 25.1972, lng: 55.2744, cat: 'categoryInterest', icon: 'fa-building' },
            { name: 'The Dubai Mall', lat: 25.1985, lng: 55.2796, cat: 'categoryNearby', icon: 'fa-shopping-cart' },
            { name: 'Dubai Fountain', lat: 25.1959, lng: 55.2764, cat: 'categoryNearby', icon: 'fa-water' },
            { name: 'Dubai International Airport (DXB)', lat: 25.2532, lng: 55.3657, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Burjuman Metro Station', lat: 25.2536, lng: 55.3023, cat: 'categorySubway', icon: 'fa-subway' }
        ],
        'las vegas': [
            { name: 'Bellagio Fountains', lat: 36.1126, lng: -115.1767, cat: 'categoryNearby', icon: 'fa-water' },
            { name: 'High Roller Observation Wheel', lat: 36.1176, lng: -115.1681, cat: 'categoryInterest', icon: 'fa-bullseye' },
            { name: 'Grand Canal Shoppes', lat: 36.1212, lng: -115.1697, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Harry Reid International Airport (LAS)', lat: 36.0840, lng: -115.1537, cat: 'categoryAirports', icon: 'fa-plane' }
        ],
        'singapore': [
            { name: 'Marina Bay Sands', lat: 1.2834, lng: 103.8607, cat: 'categoryInterest', icon: 'fa-hotel' },
            { name: 'Gardens by the Bay', lat: 1.2816, lng: 103.8636, cat: 'categoryNearby', icon: 'fa-tree' },
            { name: 'Orchard Road Shopping Belt', lat: 1.3048, lng: 103.8318, cat: 'categoryNearby', icon: 'fa-shopping-bag' },
            { name: 'Singapore Changi Airport (SIN)', lat: 1.3644, lng: 103.9915, cat: 'categoryAirports', icon: 'fa-plane' },
            { name: 'Bayfront MRT Station', lat: 1.2818, lng: 103.8591, cat: 'categorySubway', icon: 'fa-subway' }
        ]
    };

    let matchedSpots = [];
    for (const [cityName, spots] of Object.entries(cityLandmarks)) {
        if (fullText.includes(cityName)) {
            matchedSpots = spots;
            break;
        }
    }

    if (matchedSpots.length > 0 && !isNaN(curLat) && !isNaN(curLng) && curLat !== 0) {
        matchedSpots.forEach(spot => {
            const distKm = getDistanceKm(curLat, curLng, spot.lat, spot.lng);
            const formattedDist = formatDistanceText(distKm, 'km');
            categories[spot.cat].push({
                name: spot.name,
                distance: formattedDist,
                icon: spot.icon
            });
        });
    }

    // Universal fallback if fewer than 3 total attractions exist
    const totalFound = Object.values(categories).reduce((acc, arr) => acc + arr.length, 0);
    if (totalFound < 3) {
        const extractCityName = (hData, addrStr) => {
            if (hData.city && hData.city.length > 2 && hData.city.toLowerCase() !== 'unknown location') return hData.city;
            if (hData.region_name && hData.region_name.length > 2 && hData.region_name.toLowerCase() !== 'unknown location') return hData.region_name;
            const full = `${hData.name || ''} ${addrStr || ''}`.toLowerCase();
            const known = ['bengaluru', 'bangalore', 'mumbai', 'delhi', 'goa', 'jaipur', 'agra', 'hyderabad', 'chennai', 'kolkata', 'pune', 'los angeles', 'new york', 'paris', 'london', 'dubai', 'las vegas', 'singapore'];
            for (const k of known) {
                if (full.includes(k)) return k.charAt(0).toUpperCase() + k.slice(1);
            }
            if (addrStr && addrStr.includes(',')) {
                const parts = addrStr.split(',').map(s => s.trim()).filter(Boolean);
                for (let i = parts.length - 1; i >= 0; i--) {
                    const p = parts[i];
                    if (!/^\d+$/.test(p) && p.length > 2 && !/india|usa|uk|france|uae|germany|spain|italy|japan|australia/i.test(p)) {
                        return p;
                    }
                }
            }
            return 'City Center';
        };

        const cityDisp = extractCityName(hotelData, address);

        categories.categoryNearby.push({
            name: `${cityDisp} Shopping Promenade`,
            distance: '1.2 km / 15 min walk',
            icon: 'fa-shopping-bag'
        });
        categories.categoryNearby.push({
            name: `${cityDisp} Central Park & Gardens`,
            distance: '0.8 km / 10 min walk',
            icon: 'fa-walking'
        });
        categories.categoryInterest.push({
            name: `${cityDisp} Historic District & Museums`,
            distance: '2.5 km / 6 min drive',
            icon: 'fa-landmark'
        });
        categories.categoryAirports.push({
            name: `${cityDisp} International Airport`,
            distance: '18 km / 25 min drive',
            icon: 'fa-plane'
        });
        categories.categorySubway.push({
            name: `${cityDisp} Central Metro Station`,
            distance: '0.9 km / 11 min walk',
            icon: 'fa-subway'
        });
    }

    return categories;
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

    // Process attractions for hotel
    const categories = getAttractionsForHotel(hotelData, lat, lng, hotelData.address || '');

    const surroundingsContainer = document.getElementById('surroundingsContainer');
    if (surroundingsContainer) {
        surroundingsContainer.style.display = 'grid';
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
 */
function displayMapPreviewByAddress(address, hotelData = {}) {
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

    // Process attractions
    const categories = getAttractionsForHotel(hotelData, null, null, address);
    const surroundingsContainer = document.getElementById('surroundingsContainer');
    if (surroundingsContainer) {
        surroundingsContainer.style.display = 'grid';
    }

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
 * Fetch additional photos for Google Places hotels is completely disabled.
 */
async function fetchGooglePlacePhotos(hotelId) {
    console.log('Google Places photo fetching is completely disabled. Relying only on RateHawk/ETG.');
}

function formatTimeAmPm(timeStr) {
    if (!timeStr) return '';
    if (timeStr.includes('AM') || timeStr.includes('PM') || timeStr.includes('noon') || timeStr.includes('midnight')) {
        return timeStr;
    }
    const parts = timeStr.trim().split(':');
    if (parts.length >= 2) {
        let h = parseInt(parts[0], 10);
        let m = parseInt(parts[1], 10);
        if (isNaN(h)) return timeStr;
        if (h === 12 && m === 0) return '12:00 PM (noon)';
        if (h === 0 && m === 0) return '12:00 AM (midnight)';
        const period = h < 12 ? 'AM' : 'PM';
        let h12 = h % 12;
        if (h12 === 0) h12 = 12;
        return m === 0 ? `${h12}:00 ${period}` : `${h12}:${m < 10 ? '0' + m : m} ${period}`;
    }
    return timeStr;
}

/**
 * Display default policies
 */
function displayDefaultPolicies() {
    const policies = {
        check_in_time: '15:00',
        check_out_time: '11:00',
        check_in_time_formatted: '3:00 PM',
        check_out_time_formatted: '11:00 AM',
        check_in_out: [
            { icon: 'fa-sign-in-alt', label: 'Check-in', value: 'Check-in start time: 3:00 PM; Check-in end time: anytime' },
            { icon: 'fa-sign-out-alt', label: 'Check-out', value: 'Check-out before 11:00 AM' }
        ],
        early_late: [
            { icon: 'fa-clock', label: 'Early Check-in', value: 'Standard check-in starts at 3:00 PM. Early check-in before 3:00 PM is subject to room availability on arrival.' },
            { icon: 'fa-clock', label: 'Late Check-out', value: 'Standard check-out is before 11:00 AM. Late check-out beyond 11:00 AM is subject to availability upon request.' }
        ],
        children: [
            { icon: 'fa-child', label: 'Children', value: 'Children of all ages welcome' }
        ],
        pets: [
            { icon: 'fa-paw', label: 'Pets', value: 'Pet policy varies by property — check property details or request at check-in' }
        ],
        payments: [
            { icon: 'fa-credit-card', label: 'Payment', value: 'Credit/Debit cards accepted' }
        ],
        internet: [
            { icon: 'fa-wifi', label: 'WiFi', value: 'Free WiFi available' }
        ],
        parking: [
            { icon: 'fa-parking', label: 'Parking', value: 'Parking available on site' }
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
    const ciFmt = policies.check_in_time_formatted || formatTimeAmPm(policies.check_in_time) || '3:00 PM';
    const coFmt = policies.check_out_time_formatted || formatTimeAmPm(policies.check_out_time) || '11:00 AM';
    const rawCi = policies.check_in_time || '15:00';
    const rawCo = policies.check_out_time || '11:00';

    const checkinEl = document.getElementById('checkinValue');
    const checkoutEl = document.getElementById('checkoutValue');
    const checkinProgress = document.getElementById('checkinProgress');
    const checkoutProgress = document.getElementById('checkoutProgress');

    if (checkinEl) checkinEl.textContent = `After ${ciFmt}`;
    if (checkoutEl) checkoutEl.textContent = `Until ${coFmt}`;

    // Calculate progress (00:00 to 24:00)
    const timeToPercent = (timeStr) => {
        if (!timeStr) return 50;
        const [hours, minutes] = timeStr.split(':').map(Number);
        return ((hours + (minutes || 0) / 60) / 24) * 100;
    };

    if (checkinProgress) checkinProgress.style.width = `${timeToPercent(rawCi)}%`;
    if (checkoutProgress) checkoutProgress.style.width = `${timeToPercent(rawCo)}%`;

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
                <div class="paid-detail-row">
                    <span class="paid-label">${p.label || 'Details'}:</span>
                    <span class="paid-value">${p.value || p}</span>
                </div>
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
                <div class="paid-detail-row">
                    <span class="paid-label">${p.label || 'Details'}:</span>
                    <span class="paid-value">${p.value || p}</span>
                </div>
            `).join('');
            hasAnyPaid = true;
        } else {
            extraBedsSection.style.display = 'none';
        }
    }

    if (parkingSection) {
        if (parkingPolicy.length > 0) {
            parkingSection.style.display = 'flex';
            parkingSection.querySelector('.paid-item-details').innerHTML = parkingPolicy.map(p => {
                let val = p.value || p;
                if (val.toLowerCase().includes('subject to availability')) {
                    val = 'Parking available';
                }
                return `
                <div class="paid-detail-row">
                    <span class="paid-label">${p.label || 'Details'}:</span>
                    <span class="paid-value">${val}</span>
                </div>
            `;
            }).join('');
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
            { title: 'Important Information', data: policies.other },
            { title: 'Meals & Dining', data: policies.meals },
            { title: 'Internet & Connectivity', data: policies.internet },
            { title: 'Smoking Policy', data: policies.smoking },
            { title: 'Age Restriction', data: policies.age_restriction },
            { title: 'Shuttle & Transfers', data: policies.shuttle },
            { title: 'Visa & Documents', data: policies.visa },
            { title: 'Check-in Policy', data: policies.early_late },
            { title: 'Payment Methods', data: policies.payments }
        ];

        let additionalHtml = '';
        otherSections.forEach(section => {
            if (section.data && section.data.length > 0) {
                additionalHtml += `
                    <div class="info-block" style="margin-bottom: 16px;">
                        <strong style="display: block; margin-bottom: 4px; color: #111827;">${section.title}</strong>
                        <ul style="padding-left: 20px; color: #4b5563; list-style-type: disc;">
                            ${section.data.map(item => `
                                <li style="margin-bottom: 8px;">
                                    ${item.label && item.label !== section.title ? `<strong>${item.label}:</strong> ` : ''}
                                    ${item.value || item}
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                `;
            }
        });

        if (additionalHtml) {
            additionalInfoContainer.innerHTML = additionalHtml;
            document.getElementById('additionalInfoSection').style.display = 'block';
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
    const rateCurrency = rates[0]?.currency || currentHotel?.currency || 'USD';
    const stickyPrice = document.getElementById('stickyPrice');
    if (stickyPrice) {
        stickyPrice.textContent = HotelUtils.formatPrice(lowestPrice, rateCurrency);
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

    // ── Render Real ETG Rates Natively ────────────────────────────────────
    // Deduplicate rates by room name so we don't show the exact same suite multiple times
    const uniqueRates = [];
    const seenRooms = new Set();
    
    for (const rate of rates) {
        const roomName = (rate.room_name || 'Standard Room').toLowerCase().trim();
        if (!seenRooms.has(roomName)) {
            seenRooms.add(roomName);
            uniqueRates.push(rate);
        }
    }

    const ratesToShow = uniqueRates.slice(0, 12); // Show up to 12 unique room types
    const badges = ['Cheapest Option', 'Best Seller', 'Great Value', 'Popular', 'Upgrade your stay', 'Limited Availability'];
    
    ratesToShow.forEach((rate, index) => {
        const badge = index === 0 ? 'Cheapest Option' : badges[index % badges.length];
        const card = createRateCard(rate, index, badge);
        container.appendChild(card);
    });
    
    updateMainCancellationPolicy(rates);
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
    card.dataset.rateCurrency = rate.currency || currentHotel?.currency || 'USD'; // currency for price formatting

    const price = rate.price;
    const rateCurrency = rate.currency || currentHotel?.currency || 'USD';
    const priceFormatted = HotelUtils.formatPrice(price, rateCurrency);
    const originalPrice = rate.original_price || Math.round(price * 1.15);
    const originalPriceFormatted = HotelUtils.formatPrice(originalPrice, rateCurrency);
    const discount = originalPrice - price;
    const discountFormatted = HotelUtils.formatPrice(discount, rateCurrency);

    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = HotelUtils.formatPrice(price * nights, rateCurrency);
    const originalTotal = HotelUtils.formatPrice(originalPrice * nights, rateCurrency);

    // Use custom badge if provided, otherwise use defaults
    const popularityBadges = ['Popular among travelers', 'Upgrade your stay', 'Great value', 'Best seller'];
    const popularityBadge = customBadge || (index < popularityBadges.length ? popularityBadges[index] : '');
    const badgeClass = index === 0 ? 'popular' : (index === 1 ? 'upgrade' : 'value');


    // Room static data
    const roomStatic = rate.room_static || {};
    let roomImagesRaw = roomStatic.images || [];
    let roomImages = roomImagesRaw.map(img => typeof img === 'string' ? img.replace('{size}', '1024x768') : img);

    // Fallback to distinct overall hotel photos from ETG API if room images are empty
    const roomName = rate.room_name || roomStatic.room_name || 'Standard Room';
    
    // Hash the room name so the same room type always gets the same fallback photos
    let nameHash = 0;
    const normalizedName = roomName.toLowerCase();
    for (let i = 0; i < normalizedName.length; i++) {
        nameHash = ((nameHash << 5) - nameHash) + normalizedName.charCodeAt(i);
        nameHash = nameHash & nameHash;
    }
    
    if (roomImages.length === 0 || roomStatic.matched === false || roomStatic.image_source === 'hotel_fallback') {
        // Fallback to the hotel's actual images first, then to generic images
        if (window.hotelImages && window.hotelImages.length > 0) {
            // Use up to 5 images from the hotel's general photos
            roomImages = window.hotelImages.slice(0, 5);
        } else {
            const genericRoomImages = [
                'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?w=600',
                'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600',
                'https://images.unsplash.com/photo-1618773928121-c32242e63f39?w=600',
                'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600',
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600'
            ];
            const offset = Math.abs(nameHash) % genericRoomImages.length;
            roomImages = [...genericRoomImages.slice(offset), ...genericRoomImages.slice(0, offset)].slice(0, 5);
        }
        
        // Also update the underlying rate object so the modal sees the exact same fallback images
        if (!rate.room_static) rate.room_static = {};
        rate.room_static.images = roomImages;
    }
    
    // Hard cap at 5 images for the room gallery
    if (roomImages.length > 5) {
        roomImages = roomImages.slice(0, 5);
        if (rate.room_static) rate.room_static.images = roomImages;
    }

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
    const imageCount = roomImages.length || (hotelImages ? hotelImages.length : 1);
    const mainImage = roomImages[0] || (hotelImages && hotelImages[0]) || '';

    roomImageHtml = `
        <div class="room-image-carousel" data-index="0" data-images='${JSON.stringify(roomImages.slice(0, 8))}'>
            ${popularityBadge ? `<div class="room-popularity-badge ${badgeClass}">${popularityBadge}</div>` : ''}
            <button class="carousel-nav prev" onclick="navigateRoomImage(this, -1)"><i class="fas fa-chevron-left"></i></button>
            <div class="room-carousel-image" style="background-image: url('${mainImage}');"></div>
            <button class="carousel-nav next" onclick="navigateRoomImage(this, 1)"><i class="fas fa-chevron-right"></i></button>
            <span class="room-image-count"><i class="fas fa-camera"></i> ${imageCount}</span>
        </div>
    `;

    // Store rate data on card for showRoomDetails to read (after modifications)
    try { card.dataset.rateJson = JSON.stringify(rate); } catch (e) { }

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

    // ── Cancellation Policy Section ────────────────────
    const cancellationInfo = rate.cancellation_info || {};

    let refundableHtml = '';
    
    if (cancellationInfo.is_free_cancellation && cancellationInfo.free_cancellation_formatted) {
        const deadline = cancellationInfo.free_cancellation_formatted.datetime || cancellationInfo.free_cancellation_formatted.raw;
        refundableHtml = `
            <div class="rate-refundable-status free-cancellation" style="display:flex;align-items:flex-start;gap:8px;margin-top:12px;padding:10px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;">
                <i class="fas fa-check-circle" style="color:#059669;font-size:1.1rem;margin-top:2px;"></i>
                <div class="status-content">
                    <strong style="display:block;color:#065f46;font-size:0.9rem;">Free cancellation</strong>
                    <span style="display:block;color:#047857;font-size:0.8rem;margin-top:2px;">Before ${deadline}</span>
                    <a href="#" style="display:block;color:#059669;font-size:0.75rem;margin-top:4px;text-decoration:none;font-weight:600;" onclick="showCancellationModal(${index}); return false;">View all policy details <i class="fas fa-chevron-right"></i></a>
                </div>
            </div>
        `;
    } else {
        refundableHtml = `
            <div class="rate-refundable-status non-refundable" style="display:flex;align-items:flex-start;gap:8px;margin-top:12px;padding:10px;background:#fef2f2;border:1px solid #fecaca;border-radius:8px;">
                <i class="fas fa-times-circle" style="color:#dc2626;font-size:1.1rem;margin-top:2px;"></i>
                <div class="status-content">
                    <strong style="display:block;color:#991b1b;font-size:0.9rem;">Non-refundable rate</strong>
                    <a href="#" style="display:block;color:#dc2626;font-size:0.75rem;margin-top:4px;text-decoration:none;font-weight:600;" onclick="showCancellationModal(${index}); return false;">View all policy details <i class="fas fa-chevron-right"></i></a>
                </div>
            </div>
        `;
    }

    // Extras section has been fully removed. The meal badge is already displayed at the top via mealBadgeHtml.
    let extrasHtml = '';

    // Urgency notice (randomly show for some rooms)
    const showUrgency = Math.random() > 0.6;
    const roomsLeft = Math.floor(Math.random() * 4) + 1;
    const urgencyHtml = showUrgency ? `<span class="urgency-notice">We have ${roomsLeft} left</span>` : '';

    // Tax info display - ETG-compliant: distinguish included vs non-included taxes
    let taxNoteHtml = '<small class="taxes-note" style="color:#059669"><i class="fas fa-check-circle"></i> Includes taxes & fees</small>';

    const taxInfo = rate.tax_info || {};
    const nonIncludedTaxes = taxInfo.non_included_taxes || [];

    // If there are non-included taxes, show them clearly (ETG certification requirement)
    if (nonIncludedTaxes.length > 0) {
        const taxItems = nonIncludedTaxes.map(tax => {
            const amount = parseFloat(tax.amount || 0);
            const currency = tax.currency_code || 'USD';
            const displayName = tax.display_name || tax.name || 'Property Fee';
            return `<div style="display:flex;justify-content:space-between;font-size:0.72rem;padding:2px 0"><span>${displayName}</span><span>${currency} ${amount.toFixed(2)}</span></div>`;
        }).join('');

        taxNoteHtml = `
            <div style="margin-top:6px;padding:8px 10px;background:#fffbeb;border:1px solid #fde68a;border-radius:8px;">
                <div style="font-size:0.78rem;font-weight:600;color:#92400e;margin-bottom:4px;">
                    <i class="fas fa-info-circle"></i> Additional fees payable at property:
                </div>
                ${taxItems}
                <div style="font-size:0.72rem;color:#b45309;margin-top:4px;">These fees are not included in the price shown and must be paid at check-in.</div>
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

    const carouselEl = card.querySelector('.room-image-carousel');
    if (carouselEl) {
        carouselEl.style.cursor = 'pointer';
        carouselEl.addEventListener('click', (e) => {
            if (e.target.closest('.carousel-nav')) return;
            showRoomDetails(index);
        });
    }

    const roomNameEl = card.querySelector('.rate-room-name');
    if (roomNameEl) {
        roomNameEl.style.cursor = 'pointer';
        roomNameEl.title = 'Click to view room photos and details';
        roomNameEl.addEventListener('click', () => {
            showRoomDetails(index);
        });
    }

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

// updateExtras function removed per ETG auditor request

let currentRoomModalImages = [];
let currentRoomModalImageIndex = 0;

function navigateExpediaRoomModalImage(direction) {
    if (!currentRoomModalImages || currentRoomModalImages.length <= 1) return;
    currentRoomModalImageIndex = (currentRoomModalImageIndex + direction + currentRoomModalImages.length) % currentRoomModalImages.length;

    const imgEl = document.getElementById('expediaRoomModalImg');
    const counterEl = document.getElementById('expediaRoomImgCounter');

    if (imgEl) imgEl.src = currentRoomModalImages[currentRoomModalImageIndex];
    if (counterEl) counterEl.textContent = `${currentRoomModalImageIndex + 1} / ${currentRoomModalImages.length}`;
}

// Show Expedia Room Information Modal (matching Expedia layout)
function showRoomDetails(rateIndex) {
    const card = document.querySelector(`.rate-card[data-rate-index="${rateIndex}"]`);
    if (!card) return;

    let rate = {};
    try {
        rate = JSON.parse(card.dataset.rateJson || '{}');
    } catch (e) {
        rate = {};
    }

    const roomName = rate.room_name || 'Room';
    const roomStatic = rate.room_static || {};
    let roomImages = roomStatic.images || [];

    if (!roomImages || roomImages.length === 0) {
        if (hotelImages && hotelImages.length > 0) {
            roomImages = hotelImages;
        } else {
            roomImages = ['https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'];
        }
    }
    
    if (roomImages.length > 5) {
        roomImages = roomImages.slice(0, 5);
    }

    currentRoomModalImages = roomImages;
    currentRoomModalImageIndex = 0;

    const cancelInfo = rate.cancellation_info || {};
    const isFreeCancellation = cancelInfo.is_free_cancellation;
    const deadline = cancelInfo.free_cancellation_formatted?.datetime || cancelInfo.free_cancellation_formatted || '';
    const mealDisplay = rate.meal_info?.display_name || 'Room Only (No Meals)';
    const priceFormatted = HotelUtils.formatPrice(rate.price, rate.currency || currentHotel?.currency || 'USD');

    const roomTypeConfig = rate._roomTypeConfig || {};
    const roomSize = roomTypeConfig.size || roomStatic.room_size || rate.room_size || 320;
    const sleepsCount = roomTypeConfig.sleeps || roomStatic.max_occupancy || rate.max_occupancy || 2;
    const bedType = roomTypeConfig.bedType || roomStatic.bed_type || rate.bed_type || getBedType(roomName);

    // Remove existing modal if open
    const existing = document.getElementById('expediaRoomInfoModal');
    if (existing) existing.remove();

    const modal = document.createElement('div');
    modal.id = 'expediaRoomInfoModal';
    modal.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.65);z-index:99999;display:flex;align-items:center;justify-content:center;padding:16px;backdrop-filter:blur(4px);';

    modal.addEventListener('click', (e) => {
        if (e.target === modal) modal.remove();
    });

    modal.innerHTML = `
        <div style="background:#ffffff;border-radius:20px;max-width:640px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 24px 64px rgba(0,0,0,0.35);position:relative;animation:expediaModalPop 0.2s ease-out;">
            <!-- Header -->
            <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 20px;border-bottom:1px solid #e2e8f0;position:sticky;top:0;background:#ffffff;z-index:10;border-radius:20px 20px 0 0;">
                <div style="display:flex;align-items:center;gap:12px;">
                    <button onclick="document.getElementById('expediaRoomInfoModal').remove()" style="width:36px;height:36px;border-radius:50%;border:1px solid #e2e8f0;background:#f8fafc;display:flex;align-items:center;justify-content:center;cursor:pointer;color:#334155;transition:all 0.2s;">
                        <i class="fas fa-times" style="font-size:1.1rem;"></i>
                    </button>
                    <span style="font-weight:700;font-size:1.1rem;color:#0f172a;">Room information</span>
                </div>
            </div>

            <div style="padding:20px;">
                <!-- Main Image Carousel (Expedia Style) -->
                <div style="position:relative;width:100%;height:320px;border-radius:16px;overflow:hidden;background:#0f172a;margin-bottom:20px;box-shadow:0 8px 24px rgba(0,0,0,0.12);">
                    <img id="expediaRoomModalImg" src="${roomImages[0]}" alt="${roomName}" style="width:100%;height:100%;object-fit:cover;transition:opacity 0.2s ease-in-out;" />
                    
                    ${roomImages.length > 1 ? `
                        <button onclick="navigateExpediaRoomModalImage(-1)" style="position:absolute;left:12px;top:50%;transform:translateY(-50%);width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.92);border:none;box-shadow:0 4px 12px rgba(0,0,0,0.2);cursor:pointer;display:flex;align-items:center;justify-content:center;color:#0f172a;">
                            <i class="fas fa-chevron-left" style="font-size:1.1rem;"></i>
                        </button>
                        <button onclick="navigateExpediaRoomModalImage(1)" style="position:absolute;right:12px;top:50%;transform:translateY(-50%);width:40px;height:40px;border-radius:50%;background:rgba(255,255,255,0.92);border:none;box-shadow:0 4px 12px rgba(0,0,0,0.2);cursor:pointer;display:flex;align-items:center;justify-content:center;color:#0f172a;">
                            <i class="fas fa-chevron-right" style="font-size:1.1rem;"></i>
                        </button>
                        <div id="expediaRoomImgCounter" style="position:absolute;bottom:12px;right:12px;background:rgba(0,0,0,0.75);color:#ffffff;padding:4px 12px;border-radius:20px;font-size:0.8rem;font-weight:600;backdrop-filter:blur(4px);">
                            1 / ${roomImages.length}
                        </div>
                    ` : ''}
                </div>

                <!-- Room Title -->
                <h2 style="font-size:1.35rem;font-weight:700;color:#0f172a;margin:0 0 16px;line-height:1.3;">${roomName}</h2>

                <!-- Expedia Amenities Grid Box -->
                <div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:16px;padding:20px;margin-bottom:20px;">
                    <div style="display:grid;grid-template-columns:repeat(2, 1fr);gap:16px;">
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-snowflake" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>Air conditioning</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-door-open" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>Connecting rooms available</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-baby" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>Free cribs / infant beds</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-bed" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>${bedType}</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-blinds" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>Blackout drapes / curtains</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-wind" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>Hair dryer</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-ruler-combined" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>${roomSize} sq ft</span>
                        </div>
                        <div style="display:flex;align-items:center;gap:12px;color:#334155;font-size:0.9rem;">
                            <i class="fas fa-users" style="font-size:1.2rem;color:#2563eb;width:24px;text-align:center;"></i>
                            <span>Sleeps ${sleepsCount}</span>
                        </div>
                    </div>
                </div>

                <!-- Policies & Inclusions -->
                <div style="display:flex;flex-direction:column;gap:10px;margin-bottom:20px;">
                    <div style="display:flex;align-items:center;gap:10px;color:#059669;font-weight:600;font-size:0.95rem;">
                        <i class="fas fa-utensils"></i>
                        <span>${mealDisplay}</span>
                    </div>
                    ${isFreeCancellation ? `
                        <div style="display:flex;align-items:center;gap:10px;color:#059669;font-weight:600;font-size:0.95rem;">
                            <i class="fas fa-check-circle"></i>
                            <span>Free cancellation before ${deadline}</span>
                        </div>
                    ` : `
                        <div style="display:flex;align-items:center;gap:10px;color:#dc2626;font-weight:600;font-size:0.95rem;">
                            <i class="fas fa-times-circle"></i>
                            <span>Non-refundable rate</span>
                        </div>
                    `}
                    <div style="display:flex;align-items:center;gap:10px;color:#2563eb;font-weight:600;font-size:0.95rem;">
                        <i class="fas fa-calendar-check"></i>
                        <span>Reserve now, pay later</span>
                    </div>
                </div>
            </div>

            <!-- Footer Action Bar -->
            <div style="display:flex;align-items:center;justify-content:space-between;padding:16px 24px;border-top:1px solid #e2e8f0;background:#ffffff;border-radius:0 0 20px 20px;">
                <div>
                    <div style="font-size:1.4rem;font-weight:700;color:#0f172a;">${priceFormatted}</div>
                    <div style="font-size:0.8rem;color:#64748b;">per night · incl. taxes & fees</div>
                </div>
                <button id="expediaModalReserveBtn" style="padding:14px 32px;background:#2563eb;color:#ffffff;border:none;border-radius:12px;font-weight:700;font-size:1rem;cursor:pointer;box-shadow:0 4px 14px rgba(37,99,235,0.35);transition:all 0.2s;">
                    Reserve
                </button>
            </div>
        </div>
    `;

    document.body.appendChild(modal);

    document.getElementById('expediaModalReserveBtn').onclick = () => {
        modal.remove();
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

    // Calculate totals
    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const baseNightlyPrice = rate.price;
    const totalPrice = baseNightlyPrice * nights;

    // Build the rate object that checkout pages will read
    const rateForCheckout = {
        ...rate,
        price: baseNightlyPrice,
        total_price: totalPrice,
        nights: nights
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
        // Appended timestamp to force browser to ignore cached HTML
        window.location.href = 'guest-details.html?v=' + Date.now();
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
