/**
 * C2C Journeys - Hotel Results Page (Expedia-Style)
 * Handles hotel search results display and interactions
 */

document.addEventListener('DOMContentLoaded', function () {
    initHotelResults();
});

// Global state
let allHotels = [];
let filteredHotels = [];
let currentPage = 1;
const hotelsPerPage = 12;
let map = null;
let markers = [];

/**
 * Initialize hotel results page
 */
async function initHotelResults() {
    // Check URL params first and save to session
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('destination')) {
        const params = {
            destination: urlParams.get('destination'),
            checkin: urlParams.get('checkin'),
            checkout: urlParams.get('checkout'),
            rooms: parseRoomsParam(urlParams.get('rooms')),
            adults: parseInt(urlParams.get('adults')) || 2,
            children_ages: [],
            residency: urlParams.get('residency') || 'in'
        };

        if (Array.isArray(params.rooms)) {
            params.adults = params.rooms.reduce((sum, r) => sum + (r.adults || 0), 0);
        }
        SearchSession.saveSearchParams(params);
        SearchSession.remove(SearchSession.KEYS.SEARCH_RESULTS);
    }

    // Get search params from session
    const searchParams = SearchSession.getSearchParams();

    if (!searchParams) {
        showNotification('Please search for hotels first', 'warning');
        setTimeout(() => {
            window.location.href = 'index.html#hotels';
        }, 2000);
        return;
    }

    // Update search bar
    updateSearchBar(searchParams);

    // Setup event listeners
    setupEventListeners();

    // Initialize Currency Selector
    initCurrency();

    // Generate price histogram
    generatePriceHistogram();

    // Check for cached results first
    const cachedResults = SearchSession.getSearchResults();
    if (cachedResults && cachedResults.hotels) {
        displayResults(cachedResults);
    } else {
        await performSearch(searchParams);
    }
}

/**
 * Update the Expedia-style search bar
 */
function updateSearchBar(params) {
    const destinationEl = document.getElementById('searchDestination');
    const datesEl = document.getElementById('searchDates');
    const travelersEl = document.getElementById('searchTravelers');

    if (destinationEl) {
        destinationEl.textContent = params.destination || 'Select destination';
    }

    if (datesEl && params.checkin && params.checkout) {
        const checkinDate = new Date(params.checkin);
        const checkoutDate = new Date(params.checkout);
        const options = { weekday: 'short', month: 'short', day: 'numeric' };
        datesEl.textContent = `${checkinDate.toLocaleDateString('en-US', options)} - ${checkoutDate.toLocaleDateString('en-US', options)}`;
    }

    if (travelersEl) {
        let roomCount = Array.isArray(params.rooms) ? params.rooms.length : (params.rooms || 1);
        let adultCount = Array.isArray(params.rooms)
            ? params.rooms.reduce((sum, r) => sum + (r.adults || 0), 0)
            : (params.adults || 2);
        travelersEl.textContent = `${adultCount} traveler${adultCount > 1 ? 's' : ''}, ${roomCount} room${roomCount > 1 ? 's' : ''}`;
    }
}

function parseRoomsParam(param) {
    if (!param) return 1;
    try {
        const parsed = JSON.parse(param);
        if (Array.isArray(parsed)) return parsed;
        return parseInt(param) || 1;
    } catch (e) {
        return parseInt(param) || 1;
    }
}

/**
 * Generate price histogram bars
 */
function generatePriceHistogram() {
    const histogram = document.getElementById('priceHistogram');
    if (!histogram) return;

    const heights = [20, 35, 60, 80, 100, 85, 65, 45, 30, 20, 15, 10];
    histogram.innerHTML = heights.map((h, i) =>
        `<div class="bar ${i < 8 ? 'active' : ''}" style="height: ${h}%"></div>`
    ).join('');
}

/**
 * Perform hotel search
 */
async function performSearch(params) {
    showLoading();

    try {
        try {
            await HotelAPI.healthCheck();
        } catch (e) {
            console.log('Backend server not reachable, using demo data');
            showDemoResults(params);
            return;
        }

        const result = await HotelAPI.searchByDestination(params);

        if (result.success && result.data?.hotels?.length > 0) {
            SearchSession.saveSearchResults(result);
            displayResults(result);

            const hotelCount = result.hotels_count || result.data.hotels.length;
            const isRateHawk = result.source === 'ratehawk';

            console.log(`✅ Found ${hotelCount} hotels via ${result.source}`);

            if (isRateHawk) {
                showNotification(`${hotelCount} verified hotels loaded from global partners.`, 'success');
            }
        } else {
            console.log('No hotels found from API, showing demo');
            showDemoResults(params);
        }
    } catch (error) {
        console.error('Search error:', error);
        showDemoResults(params);
    }
}

/**
 * Display search results
 */
function displayResults(result) {
    hideLoading();

    const hotels = result.data?.hotels || result.hotels || [];

    if (hotels.length === 0) {
        showNoResults();
        return;
    }

    allHotels = hotels;
    filteredHotels = [...hotels];

    document.getElementById('resultsCount').textContent = hotels.length;

    applyFiltersAndSort();
    showHotelsList();

    // Initialize map preview
    initMapPreview(hotels);
}

/**
 * Show demo results when API is not available
 */
function showDemoResults(params) {
    const demoHotels = generateDemoHotels(params.destination, 15);

    const result = {
        success: true,
        data: { hotels: demoHotels },
        demo: true
    };

    SearchSession.saveSearchResults(result);
    displayResults(result);
}

/**
 * Generate demo hotel data
 */
function generateDemoHotels(destination, count) {
    const hotelData = [
        { name: 'The Grand Palace Hotel', tagline: 'Luxury in the heart of the city', stars: 5 },
        { name: 'Ocean View Resort & Spa', tagline: 'Beachfront paradise awaits', stars: 5 },
        { name: 'City Center Suites', tagline: 'Modern comfort, prime location', stars: 4 },
        { name: 'Heritage Boutique Inn', tagline: 'Historic charm meets modern luxury', stars: 4 },
        { name: 'Mountain Retreat Lodge', tagline: 'Escape to nature in style', stars: 4 },
        { name: 'Business Plaza Hotel', tagline: 'Perfect for the modern traveler', stars: 4 },
        { name: 'Sunset Beach Resort', tagline: 'Where every sunset is magical', stars: 5 },
        { name: 'Urban Loft Hotel', tagline: 'Trendy stays in the city', stars: 3 },
        { name: 'Garden View Inn', tagline: 'Tranquil oasis in the city', stars: 3 },
        { name: 'Royal Crown Hotel', tagline: 'Experience royal treatment', stars: 5 },
        { name: 'Comfort Stay Plus', tagline: 'Value without compromise', stars: 3 },
        { name: 'Lakeside Resort', tagline: 'Serenity by the water', stars: 4 },
        { name: 'Downtown Luxury Suites', tagline: 'Upscale urban living', stars: 5 },
        { name: 'Family Fun Resort', tagline: 'Adventures for all ages', stars: 4 },
        { name: 'Executive Business Hotel', tagline: 'Where business meets comfort', stars: 4 }
    ];

    const images = [
        'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
        'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=800',
        'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=800',
        'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800',
        'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
        'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800'
    ];

    const amenitiesList = [
        ['wifi', 'pool', 'spa', 'restaurant', 'gym'],
        ['wifi', 'parking', 'restaurant', 'ac'],
        ['wifi', 'pool', 'gym', 'parking'],
        ['wifi', 'spa', 'restaurant'],
        ['wifi', 'pool', 'parking', 'restaurant', 'gym', 'spa']
    ];

    const hotels = [];
    for (let i = 0; i < count; i++) {
        const hotelInfo = hotelData[i % hotelData.length];
        const basePrice = Math.floor(Math.random() * 15000) + 3000;
        const originalPrice = basePrice + Math.floor(Math.random() * 5000) + 2000;

        hotels.push({
            id: `demo_hotel_${i + 1}`,
            name: hotelInfo.name,
            tagline: hotelInfo.tagline,
            star_rating: hotelInfo.stars,
            guest_rating: (Math.random() * 1.5 + 3.5).toFixed(1),
            review_count: Math.floor(Math.random() * 2000) + 100,
            address: `${destination}`,
            distance: `${(Math.random() * 5 + 0.5).toFixed(1)} km from center`,
            images: images.slice(0, Math.floor(Math.random() * 3) + 3).sort(() => Math.random() - 0.5),
            image: images[i % images.length],
            price: basePrice,
            original_price: originalPrice,
            currency: 'INR',
            amenities: amenitiesList[i % amenitiesList.length],
            meal_plan: ['nomeal', 'breakfast', 'halfboard'][Math.floor(Math.random() * 3)],
            is_refundable: Math.random() > 0.3,
            limited_availability: Math.random() > 0.7,
            vip_access: i < 3,
            latitude: 28.6139 + (Math.random() - 0.5) * 0.1,
            longitude: 77.2090 + (Math.random() - 0.5) * 0.1,
            rates: [{
                book_hash: `demo_hash_${i}_${Date.now()}`,
                room_name: 'Deluxe Room',
                price: basePrice
            }]
        });
    }

    return hotels;
}

/**
 * Render hotels list (Expedia-style horizontal cards)
 */
function renderHotels(hotels, append = false) {
    const list = document.getElementById('hotelsList');

    if (!append) {
        list.innerHTML = '';
    }

    hotels.forEach(hotel => {
        const card = createHotelCardHorizontal(hotel);
        list.appendChild(card);
    });

    // Initialize all carousels
    initCarousels();
}

/**
 * Create Expedia-style horizontal hotel card
 */
function createHotelCardHorizontal(hotel) {
    const card = document.createElement('div');
    card.className = 'hotel-card-horizontal';
    card.dataset.hotelId = hotel.id;

    const images = hotel.images || [hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'];
    const price = HotelUtils.formatPrice(hotel.price || hotel.rates?.[0]?.price || 0, hotel.currency);
    const originalPrice = hotel.original_price ? HotelUtils.formatPrice(hotel.original_price, hotel.currency) : null;
    const nights = getSearchNights();
    const totalPrice = HotelUtils.formatPrice((hotel.price || 0) * nights, hotel.currency);
    const rating = parseFloat(hotel.guest_rating) || 4.0;
    const ratingClass = rating >= 4.5 ? 'excellent' : rating >= 4 ? 'very-good' : 'good';
    const ratingText = rating >= 4.5 ? 'Excellent' : rating >= 4 ? 'Very Good' : 'Good';

    // Amenities icons
    const amenityIcons = {
        wifi: '<i class="fas fa-wifi"></i> Free WiFi',
        pool: '<i class="fas fa-swimming-pool"></i> Pool',
        spa: '<i class="fas fa-spa"></i> Spa',
        parking: '<i class="fas fa-parking"></i> Parking',
        restaurant: '<i class="fas fa-utensils"></i> Restaurant',
        gym: '<i class="fas fa-dumbbell"></i> Gym',
        ac: '<i class="fas fa-snowflake"></i> A/C'
    };

    const amenitiesHtml = (hotel.amenities || []).slice(0, 4).map(a =>
        `<span class="amenity-tag">${amenityIcons[a] || a}</span>`
    ).join('');

    // Image carousel HTML
    const carouselImagesHtml = images.map((img, idx) =>
        `<div class="carousel-image ${idx === 0 ? 'active' : ''}" style="background-image: url('${img}')" data-index="${idx}"></div>`
    ).join('');

    const carouselDotsHtml = images.length > 1 ? images.map((_, idx) =>
        `<span class="carousel-dot ${idx === 0 ? 'active' : ''}" data-index="${idx}"></span>`
    ).join('') : '';

    // Badges
    let badgesHtml = '';
    if (hotel.vip_access) {
        badgesHtml += '<span class="hotel-badge vip">VIP Access</span>';
    }
    if (hotel.discount || (hotel.original_price && hotel.price < hotel.original_price)) {
        const discount = Math.round((1 - hotel.price / hotel.original_price) * 100);
        if (discount > 5) {
            badgesHtml += `<span class="hotel-badge deal">${discount}% OFF</span>`;
        }
    }

    card.innerHTML = `
        <div class="hotel-card-image-section">
            <div class="hotel-image-carousel" data-hotel-id="${hotel.id}">
                ${carouselImagesHtml}
                ${images.length > 1 ? `
                    <button class="carousel-nav prev"><i class="fas fa-chevron-left"></i></button>
                    <button class="carousel-nav next"><i class="fas fa-chevron-right"></i></button>
                    <div class="carousel-dots">${carouselDotsHtml}</div>
                ` : ''}
            </div>
            <button class="wishlist-btn" data-hotel-id="${hotel.id}">
                <i class="far fa-heart"></i>
            </button>
            ${badgesHtml ? `<div class="hotel-badges">${badgesHtml}</div>` : ''}
        </div>
        <div class="hotel-card-content-section">
            <div class="hotel-card-header">
                <div class="hotel-card-title">
                    <h3>${hotel.name}</h3>
                    <p class="hotel-location"><i class="fas fa-map-marker-alt"></i> ${hotel.address || 'Location available'}</p>
                    ${hotel.distance ? `<p class="hotel-distance">${hotel.distance}</p>` : ''}
                </div>
            </div>
            <div class="hotel-amenities-row">
                ${amenitiesHtml}
            </div>
            <div class="hotel-description-text">
                ${hotel.tagline ? `<p class="hotel-tagline">${hotel.tagline}</p>` : ''}
                <p class="hotel-desc-short">${hotel.description || 'Experience exceptional comfort and world-class hospitality at this stunning property. Perfect for both leisure and business travelers.'}</p>
            </div>
            <div class="hotel-card-footer">
                <div class="hotel-rating-section">
                    <span class="rating-score-badge ${ratingClass}">${rating}</span>
                    <div class="rating-details">
                        <span class="rating-text">${ratingText}</span>
                        <span class="review-count">${hotel.review_count || 0} reviews</span>
                    </div>
                </div>
                <div class="hotel-pricing-section">
                    ${hotel.limited_availability ? '<div class="limited-availability"><i class="fas fa-bolt"></i> Only a few left!</div>' : ''}
                    <div class="price-display">
                        <span class="price-per-night"><span class="amount">${price}</span> nightly</span>
                        ${originalPrice ? `<span class="price-original">${originalPrice}</span>` : ''}
                        <span class="price-total">${totalPrice} <span class="total-label">total</span></span>
                        <span class="price-includes"><i class="fas fa-check"></i> Total with taxes and fees</span>
                    </div>
                    ${hotel.is_refundable ? '<span class="refundable-badge"><i class="fas fa-check-circle"></i> Fully refundable</span>' : ''}
                </div>
            </div>
        </div>
    `;

    // Add click event to card (except carousel controls and wishlist)
    card.addEventListener('click', (e) => {
        if (!e.target.closest('.carousel-nav') && !e.target.closest('.wishlist-btn') && !e.target.closest('.carousel-dot')) {
            viewHotelDetails(hotel);
        }
    });

    // Wishlist toggle
    card.querySelector('.wishlist-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleWishlist(e.currentTarget, hotel);
    });

    return card;
}

/**
 * Initialize image carousels
 */
function initCarousels() {
    document.querySelectorAll('.hotel-image-carousel').forEach(carousel => {
        const images = carousel.querySelectorAll('.carousel-image');
        const dots = carousel.querySelectorAll('.carousel-dot');
        const prevBtn = carousel.querySelector('.carousel-nav.prev');
        const nextBtn = carousel.querySelector('.carousel-nav.next');
        let currentIndex = 0;

        const showImage = (index) => {
            images.forEach((img, i) => {
                img.classList.toggle('active', i === index);
            });
            dots.forEach((dot, i) => {
                dot.classList.toggle('active', i === index);
            });
            currentIndex = index;
        };

        if (prevBtn) {
            prevBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const newIndex = (currentIndex - 1 + images.length) % images.length;
                showImage(newIndex);
            });
        }

        if (nextBtn) {
            nextBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const newIndex = (currentIndex + 1) % images.length;
                showImage(newIndex);
            });
        }

        dots.forEach((dot, i) => {
            dot.addEventListener('click', (e) => {
                e.stopPropagation();
                showImage(i);
            });
        });
    });
}

/**
 * Get number of nights from search params
 */
function getSearchNights() {
    const params = SearchSession.getSearchParams();
    if (params?.checkin && params?.checkout) {
        return HotelUtils.calculateNights(params.checkin, params.checkout);
    }
    return 1;
}

/**
 * Get rating text based on score
 */
function getRatingText(rating) {
    if (rating >= 4.5) return 'Excellent';
    if (rating >= 4) return 'Very Good';
    if (rating >= 3.5) return 'Good';
    if (rating >= 3) return 'Average';
    return 'Fair';
}

/**
 * View hotel details
 */
function viewHotelDetails(hotel) {
    SearchSession.saveSelectedHotel(hotel);
    window.location.href = `hotel-details.html?id=${hotel.id}`;
}

/**
 * Toggle wishlist
 */
function toggleWishlist(btn, hotel) {
    const icon = btn.querySelector('i');
    btn.classList.toggle('active');

    if (btn.classList.contains('active')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        showNotification(`${hotel.name} added to wishlist!`, 'success');
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        showNotification(`${hotel.name} removed from wishlist`, 'info');
    }
}

/**
 * Initialize map preview
 */
function initMapPreview(hotels) {
    const mapPreview = document.getElementById('mapPreview');
    if (!mapPreview || !hotels.length) return;

    // For preview, just show a static preview
    const firstHotel = hotels.find(h => h.latitude && h.longitude);
    if (firstHotel) {
        mapPreview.innerHTML = `
            <div style="position: relative; width: 100%; height: 100%; background: #e0f2fe;">
                <iframe 
                    src="https://www.openstreetmap.org/export/embed.html?bbox=${firstHotel.longitude - 0.05}%2C${firstHotel.latitude - 0.03}%2C${firstHotel.longitude + 0.05}%2C${firstHotel.latitude + 0.03}&layer=mapnik"
                    style="width: 100%; height: 100%; border: none; filter: saturate(0.7);"
                ></iframe>
            </div>
        `;
    }
}

/**
 * Initialize full map modal
 */
function initFullMap() {
    const mapContainer = document.getElementById('fullMapContainer');
    if (!mapContainer || map) return;

    // Get center from first hotel with coordinates
    const firstHotel = allHotels.find(h => h.latitude && h.longitude);
    const center = firstHotel ? [firstHotel.latitude, firstHotel.longitude] : [28.6139, 77.2090];

    map = L.map('fullMapContainer').setView(center, 13);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
    }).addTo(map);

    // Add markers for all hotels
    allHotels.forEach(hotel => {
        if (hotel.latitude && hotel.longitude) {
            const price = HotelUtils.formatPrice(hotel.price || 0, hotel.currency);

            const marker = L.marker([hotel.latitude, hotel.longitude])
                .bindPopup(`
                    <div class="hotel-map-popup">
                        <div class="popup-image" style="background-image: url('${hotel.image || hotel.images?.[0]}')"></div>
                        <div class="popup-title">${hotel.name}</div>
                        <div class="popup-rating">
                            <span class="rating-badge">${hotel.guest_rating || '4.0'}</span>
                            <span>${getRatingText(hotel.guest_rating)}</span>
                        </div>
                        <div class="popup-price">${price} / night</div>
                    </div>
                `)
                .addTo(map);

            markers.push(marker);
        }
    });

    // Fit bounds to show all markers
    if (markers.length > 0) {
        const group = new L.featureGroup(markers);
        map.fitBounds(group.getBounds().pad(0.1));
    }
}

/**
 * Apply filters and sort
 */
function applyFiltersAndSort() {
    let hotels = [...allHotels];

    // Apply price filter
    const maxPrice = parseInt(document.getElementById('priceRange').value);
    hotels = hotels.filter(h => (h.price || h.rates?.[0]?.price || 0) <= maxPrice);

    // Apply star filter
    const starFilters = document.querySelectorAll('.star-filter input:checked');
    if (starFilters.length > 0) {
        const selectedStars = Array.from(starFilters).map(i => parseInt(i.value));
        hotels = hotels.filter(h => selectedStars.includes(h.star_rating || 4));
    }

    // Apply property name search
    const propertySearch = document.getElementById('propertySearch')?.value?.toLowerCase();
    if (propertySearch) {
        hotels = hotels.filter(h => h.name.toLowerCase().includes(propertySearch));
    }

    // Apply rating filter
    const activeRatingPill = document.querySelector('.rating-pill.active');
    if (activeRatingPill && activeRatingPill.dataset.rating !== 'any') {
        const minRating = parseFloat(activeRatingPill.dataset.rating);
        hotels = hotels.filter(h => parseFloat(h.guest_rating || 0) >= minRating);
    }

    // Apply sort
    const sortValue = document.getElementById('sortSelect').value;
    switch (sortValue) {
        case 'price_low':
            hotels.sort((a, b) => (a.price || 0) - (b.price || 0));
            break;
        case 'price_high':
            hotels.sort((a, b) => (b.price || 0) - (a.price || 0));
            break;
        case 'rating':
            hotels.sort((a, b) => (b.guest_rating || 0) - (a.guest_rating || 0));
            break;
        case 'stars':
            hotels.sort((a, b) => (b.star_rating || 0) - (a.star_rating || 0));
            break;
    }

    filteredHotels = hotels;
    document.getElementById('resultsCount').textContent = hotels.length;

    currentPage = 1;
    renderHotels(hotels.slice(0, hotelsPerPage));

    // Show/hide load more
    if (hotels.length > hotelsPerPage) {
        document.getElementById('loadMore').classList.remove('hidden');
    } else {
        document.getElementById('loadMore').classList.add('hidden');
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Search bar clicks - open modify modal
    document.querySelectorAll('.search-input-group').forEach(group => {
        group.addEventListener('click', openModifyModal);
    });

    document.getElementById('searchBtn')?.addEventListener('click', openModifyModal);

    // Tab navigation
    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => {
            document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
            btn.classList.add('active');
            // Filter by tab if needed
        });
    });

    // View in map button
    document.getElementById('viewMapBtn')?.addEventListener('click', () => {
        document.getElementById('mapModal').classList.add('active');
        initFullMap();
    });

    // Close map modal
    document.getElementById('closeMapModal')?.addEventListener('click', () => {
        document.getElementById('mapModal').classList.remove('active');
    });

    // Modify search buttons
    document.getElementById('modifySearchBtn2')?.addEventListener('click', openModifyModal);

    // Close modify modal
    document.getElementById('closeModifyModal')?.addEventListener('click', closeModifyModal);
    document.querySelector('#modifySearchModal .modal-overlay')?.addEventListener('click', closeModifyModal);

    // Modify search form
    document.getElementById('modifySearchForm')?.addEventListener('submit', handleModifySearch);

    // Modify search children change
    document.getElementById('modifyChildren')?.addEventListener('change', function () {
        updateChildAgeInputs(parseInt(this.value));
    });

    // Property search
    document.getElementById('propertySearch')?.addEventListener('input', debounce(applyFiltersAndSort, 300));

    // Rating pills
    document.querySelectorAll('.rating-pill').forEach(pill => {
        pill.addEventListener('click', () => {
            document.querySelectorAll('.rating-pill').forEach(p => p.classList.remove('active'));
            pill.classList.add('active');
            applyFiltersAndSort();
        });
    });

    // Filters
    document.getElementById('priceRange')?.addEventListener('input', (e) => {
        document.getElementById('maxPriceLabel').textContent = `₹${parseInt(e.target.value).toLocaleString()}+`;
    });
    document.getElementById('priceRange')?.addEventListener('change', applyFiltersAndSort);

    document.querySelectorAll('.star-filter input').forEach(input => {
        input.addEventListener('change', applyFiltersAndSort);
    });

    // Sort
    document.getElementById('sortSelect')?.addEventListener('change', applyFiltersAndSort);

    // Clear filters
    document.getElementById('clearFilters')?.addEventListener('click', clearFilters);

    // Retry button
    document.getElementById('retryBtn')?.addEventListener('click', () => {
        const params = SearchSession.getSearchParams();
        if (params) performSearch(params);
    });

    // Load more
    document.getElementById('loadMoreBtn')?.addEventListener('click', loadMoreHotels);

    // Init Currency
    initCurrency();
}

/**
 * Debounce helper
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Load more hotels
 */
function loadMoreHotels() {
    currentPage++;
    const start = (currentPage - 1) * hotelsPerPage;
    const end = start + hotelsPerPage;
    const moreHotels = filteredHotels.slice(start, end);

    renderHotels(moreHotels, true);

    if (end >= filteredHotels.length) {
        document.getElementById('loadMore').classList.add('hidden');
    }
}

/**
 * Clear all filters
 */
function clearFilters() {
    document.getElementById('priceRange').value = 50000;
    document.getElementById('maxPriceLabel').textContent = '₹50,000+';

    document.querySelectorAll('.star-filter input').forEach(input => {
        input.checked = parseInt(input.value) >= 3;
    });

    document.querySelectorAll('.amenity-filter input, .meal-filter input').forEach(input => {
        input.checked = false;
    });

    document.getElementById('sortSelect').value = 'recommended';
    document.getElementById('propertySearch').value = '';

    document.querySelectorAll('.rating-pill').forEach((p, i) => {
        p.classList.toggle('active', i === 1);
    });

    applyFiltersAndSort();
}

/**
 * Open modify search modal
 */
function openModifyModal() {
    const modal = document.getElementById('modifySearchModal');
    const params = SearchSession.getSearchParams();

    if (params) {
        document.getElementById('modifyDestination').value = params.destination || '';
        document.getElementById('modifyCheckin').value = params.checkin || '';
        document.getElementById('modifyCheckout').value = params.checkout || '';
        document.getElementById('modifyRooms').value = Array.isArray(params.rooms) ? params.rooms.length : (params.rooms || 1);
        document.getElementById('modifyAdults').value = params.adults || 2;

        // Handle Children
        const children = params.children_ages ? params.children_ages.length : 0;
        const childSelect = document.getElementById('modifyChildren');
        if (childSelect) {
            childSelect.value = children;
            // Update age inputs based on count
            updateChildAgeInputs(children);

            // Fill age inputs
            if (children > 0 && params.children_ages) {
                // Must wait for DOM update if we just set innerHTML in updateChildAgeInputs
                // But since it's synchronous, we should be fine, but let's select newly created elements
                const ageSelects = document.querySelectorAll('.child-age-select');
                params.children_ages.forEach((age, index) => {
                    if (ageSelects[index]) ageSelects[index].value = age;
                });
            }
        }

        // Set residency if element exists
        const residencySelect = document.getElementById('modifyResidency');
        if (residencySelect && params.residency) {
            residencySelect.value = params.residency;
        }
    }

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

/**
 * Close modify search modal
 */
function closeModifyModal() {
    document.getElementById('modifySearchModal').classList.remove('show');
    document.body.style.overflow = 'auto';
}

/**
 * Update child age inputs based on count
 */
function updateChildAgeInputs(count) {
    const container = document.getElementById('modifyChildAgesContainer');
    if (!container) return;

    const grid = container.querySelector('.child-ages-grid');

    if (count === 0) {
        container.style.display = 'none';
        grid.innerHTML = '';
        return;
    }

    container.style.display = 'block';

    // Create inputs
    let html = '';
    for (let i = 0; i < count; i++) {
        html += `
            <div class="child-age-input">
                <select class="child-age-select" required style="width: 100%; padding: 8px; border: 1px solid #e2e8f0; border-radius: 6px;">
                    <option value="" disabled selected>Age</option>
                    ${Array.from({ length: 18 }, (_, i) => `<option value="${i}">${i}</option>`).join('')}
                </select>
            </div>
        `;
    }
    grid.innerHTML = html;
}

/**
 * Handle modify search form
 */
function handleModifySearch(e) {
    e.preventDefault();

    const residencySelect = document.getElementById('modifyResidency');
    const residency = residencySelect ? residencySelect.value : 'in';

    // Collect children ages
    const childrenCount = parseInt(document.getElementById('modifyChildren').value);
    const childrenAges = [];

    if (childrenCount > 0) {
        document.querySelectorAll('.child-age-select').forEach(select => {
            if (select.value !== '') {
                childrenAges.push(parseInt(select.value));
            } else {
                // Default to 0 if not selected to avoid errors, or could validate
                childrenAges.push(0);
            }
        });
    }

    const params = {
        destination: document.getElementById('modifyDestination').value,
        checkin: document.getElementById('modifyCheckin').value,
        checkout: document.getElementById('modifyCheckout').value,
        rooms: parseInt(document.getElementById('modifyRooms').value),
        adults: parseInt(document.getElementById('modifyAdults').value),
        children_ages: childrenAges,
        residency: residency // ETG requires this for accurate pricing
    };

    SearchSession.saveSearchParams(params);
    SearchSession.remove(SearchSession.KEYS.SEARCH_RESULTS);

    closeModifyModal();
    updateSearchBar(params);
    performSearch(params);
}

// UI helper functions
function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('hotelsList').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
    document.getElementById('noResultsState').classList.add('hidden');
}

function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function showError(message) {
    hideLoading();
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('errorState').classList.remove('hidden');
    document.getElementById('hotelsList').classList.add('hidden');
}

function showNoResults() {
    hideLoading();
    document.getElementById('noResultsState').classList.remove('hidden');
    document.getElementById('hotelsList').classList.add('hidden');
}

function showHotelsList() {
    document.getElementById('hotelsList').classList.remove('hidden');
}

/**
 * Show notification
 */
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
            <i class="fas ${icons[type] || icons.info}"></i>
            <span>${message}</span>
        </div>
        <button class="notification-close">&times;</button>
    `;

    notification.style.cssText = `
        position: fixed;
        top: 100px;
        right: 20px;
        background: ${colors[type] || colors.info};
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

/**
 * Initialize Currency Selector
 */
function initCurrency() {
    const currencySelect = document.getElementById('currencySelect');
    if (currencySelect) {
        const savedCurrency = localStorage.getItem('ctc_currency') || 'INR';
        currencySelect.value = savedCurrency;

        currencySelect.addEventListener('change', function () {
            const newCurrency = this.value;
            localStorage.setItem('ctc_currency', newCurrency);

            // Update price filter label with new currency symbol
            const symbols = { 'INR': '₹', 'USD': '$', 'EUR': '€', 'GBP': '£', 'AED': 'AED ' };
            const symbol = symbols[newCurrency] || newCurrency + ' ';
            document.getElementById('maxPriceLabel').textContent = `${symbol}50,000+`;

            showNotification(`Currency changed to ${newCurrency}`, 'success');

            // Re-render the hotels with new currency (uses formatPrice which reads from localStorage)
            if (filteredHotels.length > 0) {
                applyFiltersAndSort();
            }
        });
    }
}
