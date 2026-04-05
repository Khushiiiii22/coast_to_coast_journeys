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
        const parsedRooms = parseRoomsParam(urlParams.get('rooms'));

        // Extract children ages and total adults from rooms array
        let totalAdults = parseInt(urlParams.get('adults')) || 2;
        let allChildrenAges = [];

        if (Array.isArray(parsedRooms)) {
            totalAdults = parsedRooms.reduce((sum, r) => sum + (r.adults || 0), 0);
            // Collect all children ages from every room
            parsedRooms.forEach(room => {
                if (room.childAges && Array.isArray(room.childAges)) {
                    allChildrenAges = allChildrenAges.concat(room.childAges);
                } else if (room.children && typeof room.children === 'number' && room.children > 0) {
                    // If ages not specified, default to age 10 per child
                    for (let i = 0; i < room.children; i++) {
                        allChildrenAges.push(10);
                    }
                }
            });
        }

        const params = {
            destination: urlParams.get('destination'),
            checkin: urlParams.get('checkin'),
            checkout: urlParams.get('checkout'),
            rooms: parsedRooms,
            adults: totalAdults,
            children_ages: allChildrenAges,
            residency: urlParams.get('residency') || 'in'
        };
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

    // ALWAYS perform a live search — never use cached results
    // (ETG certification requires live API requests for every search)
    await performSearch(searchParams);
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
        const result = await HotelAPI.searchByDestination(params);

        if (result.success && result.data?.hotels?.length > 0) {
            // NOTE: Saving all results to session storage is removed as it exceeds browser quota (5MB) for large searches.
            // SearchSession.saveSearchResults(result); 
            displayResults(result);

            const hotelCount = result.hotels_count || result.data.hotels.length;
            const isRateHawk = result.source === 'ratehawk';

            console.log(`✅ Found ${hotelCount} hotels via ${result.source}`);

            if (isRateHawk) {
                showNotification(`${hotelCount} verified hotels loaded from global partners.`, 'success');
            }
        } else {
            console.log('No hotels found from API');
            showNoResults();
        }
    } catch (error) {
        console.error('Search error:', error);
        showNoResults();
        showNotification('Search failed: ' + error.message, 'error');
    }
}

/**
 * Display search results
 */
function displayResults(result) {
    console.log('📊 displayResults called with:', result);
    hideLoading();

    const hotels = result.data?.hotels || result.hotels || [];
    console.log(`📊 Processing ${hotels.length} hotels`);

    if (hotels.length === 0) {
        console.error('❌ No hotels to display');
        showNoResults();
        return;
    }

    allHotels = hotels;
    filteredHotels = [...hotels];
    console.log(`✅ Set allHotels: ${allHotels.length}, filteredHotels: ${filteredHotels.length}`);

    document.getElementById('resultsCount').textContent = hotels.length;

    applyFiltersAndSort();
    showHotelsList();

    // Initialize map preview
    initMapPreview(hotels);
}

/**
 * Render hotels list (Expedia-style horizontal cards)
 */
function renderHotels(hotels, append = false) {
    console.log(`🏨 renderHotels called with ${hotels.length} hotels, append: ${append}`);
    const list = document.getElementById('hotelsList');

    if (!list) {
        console.error('❌ hotelsList element not found!');
        return;
    }

    if (!append) {
        list.innerHTML = '';
    }

    if (hotels.length === 0) {
        console.warn('⚠️ No hotels to render');
        list.innerHTML = '<div class="no-hotels-message">No hotels found. Try a different search.</div>';
        return;
    }

    hotels.forEach((hotel, index) => {
        console.log(`🏨 Creating card ${index + 1}/${hotels.length}: ${hotel.name}`);
        try {
            const card = createHotelCardHorizontal(hotel);
            list.appendChild(card);
        } catch (error) {
            console.error(`❌ Error creating card for hotel ${hotel.name}:`, error);
        }
    });

    console.log(`✅ Rendered ${list.children.length} hotel cards`);

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

    // Build location string with city and country
    const searchParams = SearchSession.getSearchParams();
    const searchedDestination = searchParams?.destination || '';
    let locationDisplay = hotel.address || searchedDestination || 'Location available';
    // If the address doesn't already contain the destination context (city, country), append it
    if (searchedDestination && locationDisplay && !locationDisplay.toLowerCase().includes(searchedDestination.split(',')[0].trim().toLowerCase())) {
        locationDisplay = `${locationDisplay}, ${searchedDestination}`;
    }

    // Ensure we have valid image data with fallbacks
    const fallbackImage = 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800&q=80';
    let images = [];

    if (hotel.images && Array.isArray(hotel.images) && hotel.images.length > 0) {
        images = hotel.images;
    } else if (hotel.image) {
        images = [hotel.image];
    } else {
        images = [fallbackImage];
    }

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
                    <p class="hotel-location"><i class="fas fa-map-marker-alt"></i> ${locationDisplay}</p>
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
                        <div class="price-transparency-disclosure">
                            ${(() => {
            const fees = hotel.property_payable_fees || [];
            if (fees.length > 0) {
                // ETG Certification Requirement: Show original currency for property-payable fees
                return fees.map(fee => 
                    `<div class="property-fee-notice">
                        <i class="fas fa-exclamation-circle"></i> 
                        Pay at property: <strong>${fee.amount_native} ${fee.currency_native}</strong> ${fee.name}
                    </div>`
                ).join('');
            } else {
                return '<span class="price-includes"><i class="fas fa-check-circle" style="color:#059669"></i> Incl. taxes &amp; fees</span>';
            }
        })()}
                        </div>
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

    // Add/Remove Room buttons in Modify Modal
    document.getElementById('modifyAddRoomBtn')?.addEventListener('click', () => {
        if (modifyRooms.length < 8) {
            modifyRooms.push({ adults: 2, children: 0, childAges: [] });
            renderModifyRooms();
        }
    });

    document.getElementById('modifyRemoveRoomBtn')?.addEventListener('click', () => {
        if (modifyRooms.length > 1) {
            modifyRooms.pop();
            renderModifyRooms();
        }
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

    // Setup Autocomplete for Modify Search
    setupModifyDestAutocomplete();
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

let modifyRooms = [{ adults: 2, children: 0, childAges: [] }];

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

        // Initialize modifyRooms from params
        if (params.rooms && Array.isArray(params.rooms)) {
            modifyRooms = JSON.parse(JSON.stringify(params.rooms));
        } else if (params.rooms) {
            // Legacy/Fallback for simple room count
            modifyRooms = [];
            const count = parseInt(params.rooms);
            for (let i = 0; i < count; i++) {
                modifyRooms.push({
                    adults: params.adults || 2,
                    children: (params.children_ages && i === 0) ? params.children_ages.length : 0,
                    childAges: (params.children_ages && i === 0) ? [...params.children_ages] : []
                });
            }
        }

        // Set residency
        const residencySelect = document.getElementById('modifyResidency');
        if (residencySelect && params.residency) {
            residencySelect.value = params.residency;
        }

        renderModifyRooms();
    }

    modal.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function renderModifyRooms() {
    const container = document.getElementById('modifyRoomsContainer');
    if (!container) return;

    let html = '';
    modifyRooms.forEach((room, index) => {
        const totalGuests = room.adults + room.children;
        const canAddAdult = room.adults < 6 && totalGuests < 10;
        const canAddChild = room.children < 4 && totalGuests < 10;

        html += `
            <div class="room-block-modify" style="background: #f8fafc; padding: 15px; border-radius: 10px; margin-bottom: 15px; border: 1px solid #e2e8f0;">
                <div class="room-header" style="font-weight: 600; color: #1e293b; margin-bottom: 10px; display: flex; justify-content: space-between;">
                    <span>Room ${index + 1}</span>
                    ${totalGuests >= 10 ? '<span style="color: #ef4444; font-size: 0.75rem;"><i class="fas fa-exclamation-circle"></i> Max 10</span>' : ''}
                </div>
                <div class="traveler-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div class="traveler-info">
                        <span style="display: block; font-weight: 500; font-size: 0.9rem;">Adults</span>
                        <span style="display: block; font-size: 0.75rem; color: #64748b;">18+ years</span>
                    </div>
                    <div class="traveler-counter" style="display: flex; align-items: center; gap: 12px;">
                        <button type="button" class="counter-btn" onclick="updateModifyGuest(${index}, 'adults', -1)" 
                            style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #cbd5e1; background: white; cursor: pointer;"
                            ${room.adults <= 1 ? 'disabled' : ''}>-</button>
                        <span style="min-width: 20px; text-align: center;">${room.adults}</span>
                        <button type="button" class="counter-btn" onclick="updateModifyGuest(${index}, 'adults', 1)"
                            style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #cbd5e1; background: white; cursor: pointer;"
                            ${!canAddAdult ? 'disabled' : ''}>+</button>
                    </div>
                </div>
                <div class="traveler-row" style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                    <div class="traveler-info">
                        <span style="display: block; font-weight: 500; font-size: 0.9rem;">Children</span>
                        <span style="display: block; font-size: 0.75rem; color: #64748b;">0-17 years</span>
                    </div>
                    <div class="traveler-counter" style="display: flex; align-items: center; gap: 12px;">
                        <button type="button" class="counter-btn" onclick="updateModifyGuest(${index}, 'children', -1)"
                            style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #cbd5e1; background: white; cursor: pointer;"
                            ${room.children <= 0 ? 'disabled' : ''}>-</button>
                        <span style="min-width: 20px; text-align: center;">${room.children}</span>
                        <button type="button" class="counter-btn" onclick="updateModifyGuest(${index}, 'children', 1)"
                            style="width: 28px; height: 28px; border-radius: 50%; border: 1px solid #cbd5e1; background: white; cursor: pointer;"
                            ${!canAddChild ? 'disabled' : ''}>+</button>
                    </div>
                </div>
                ${room.children > 0 ? `
                    <div class="child-ages-container" style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; padding-top: 10px; border-top: 1px dashed #cbd5e1;">
                        ${room.childAges.map((age, i) => `
                            <div class="child-age-group">
                                <label style="display: block; font-size: 0.7rem; color: #64748b; margin-bottom: 4px;">Child ${i + 1} Age</label>
                                <select onchange="updateModifyChildAge(${index}, ${i}, this.value)" style="width: 100%; padding: 6px; border: 1px solid #cbd5e1; border-radius: 4px; font-size: 0.8rem;">
                                    ${Array.from({ length: 18 }, (_, k) => `<option value="${k}" ${age == k ? 'selected' : ''}>${k} year${k !== 1 ? 's' : ''}</option>`).join('')}
                                </select>
                            </div>
                        `).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    });

    container.innerHTML = html;
    
    // Update buttons
    const addBtn = document.getElementById('modifyAddRoomBtn');
    const removeBtn = document.getElementById('modifyRemoveRoomBtn');
    if (addBtn) addBtn.disabled = modifyRooms.length >= 8;
    if (removeBtn) removeBtn.style.display = modifyRooms.length > 1 ? 'block' : 'none';
}

window.updateModifyGuest = function(roomIndex, type, change) {
    const room = modifyRooms[roomIndex];
    if (!room) return;

    const totalGuests = room.adults + room.children;

    if (type === 'adults') {
        const newValue = room.adults + change;
        if (newValue >= 1 && newValue <= 6 && (newValue + room.children) <= 10) {
            room.adults = newValue;
        }
    } else if (type === 'children') {
        const newValue = room.children + change;
        if (newValue >= 0 && newValue <= 4 && (room.adults + newValue) <= 10) {
            room.children = newValue;
            if (change > 0) {
                room.childAges.push(7); // Default age 7
            } else {
                room.childAges.pop();
            }
        }
    }
    renderModifyRooms();
};

window.updateModifyChildAge = function(roomIndex, childIndex, value) {
    if (modifyRooms[roomIndex]) {
        modifyRooms[roomIndex].childAges[childIndex] = parseInt(value);
    }
};

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

    // Validate that all child ages are selected
    let allAgesSelected = true;
    modifyRooms.forEach(room => {
        if (room.childAges.some(age => age === null)) allAgesSelected = false;
    });

    if (!allAgesSelected) {
        alert('Please select age for all children.');
        return;
    }

    const params = {
        destination: document.getElementById('modifyDestination').value,
        checkin: document.getElementById('modifyCheckin').value,
        checkout: document.getElementById('modifyCheckout').value,
        rooms: modifyRooms, // Pass the entire array
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
/**
 * Popular destinations (sync with index.html)
 */
const popularHotelDestinationsResults = [
    { name: 'Mumbai', country: 'Maharashtra, India', type: 'city' },
    { name: 'Delhi', country: 'Delhi, India', type: 'city' },
    { name: 'Goa', country: 'Goa, India', type: 'city' },
    { name: 'Bangalore', country: 'Karnataka, India', type: 'city' },
    { name: 'Chennai', country: 'Tamil Nadu, India', type: 'city' },
    { name: 'Kolkata', country: 'West Bengal, India', type: 'city' },
    { name: 'Jaipur', country: 'Rajasthan, India', type: 'city' },
    { name: 'Hyderabad', country: 'Telangana, India', type: 'city' },
    { name: 'Pune', country: 'Maharashtra, India', type: 'city' },
    { name: 'Ahmedabad', country: 'Gujarat, India', type: 'city' },
    { name: 'Dubai', country: 'Dubai, UAE', type: 'city' },
    { name: 'Paris', country: 'Ile-de-France, France', type: 'city' },
    { name: 'London', country: 'Greater London, United Kingdom', type: 'city' },
    { name: 'Singapore', country: 'Singapore', type: 'city' }
];

/**
 * Setup autocomplete for modify destination input
 */
function setupModifyDestAutocomplete() {
    const input = document.getElementById('modifyDestination');
    if (!input) return;

    // Create dropdown container
    const wrapper = document.createElement('div');
    wrapper.className = 'autocomplete-wrapper';
    wrapper.style.position = 'relative';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown';
    dropdown.style.display = 'none';
    dropdown.style.position = 'absolute';
    dropdown.style.top = '100%';
    dropdown.style.left = '0';
    dropdown.style.right = '0';
    dropdown.style.background = 'white';
    dropdown.style.boxShadow = '0 10px 25px rgba(0,0,0,0.1)';
    dropdown.style.borderRadius = '0 0 12px 12px';
    dropdown.style.zIndex = '1000';
    dropdown.style.maxHeight = '300px';
    dropdown.style.overflowY = 'auto';
    dropdown.style.padding = '8px 0';
    wrapper.appendChild(dropdown);

    // Debounced search
    const performSearch = debounce(async (query) => {
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        try {
            dropdown.innerHTML = '<div style="padding: 10px 15px; color: #64748b; font-size: 0.9rem;"><i class="fas fa-spinner fa-spin"></i> Searching...</div>';
            dropdown.style.display = 'block';

            const response = await HotelAPI.autocompleteLocation(query);

            if (response.success && response.predictions && response.predictions.length > 0) {
                let html = '<div style="padding: 8px 15px; font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Search Results</div>';

                response.predictions.forEach(pred => {
                    const name = pred.structured_formatting?.main_text || pred.description.split(',')[0];
                    const country = pred.structured_formatting?.secondary_text || pred.description.split(',').slice(1).join(',').trim();
                    const location = {
                        name,
                        country,
                        type: 'city',
                        full: pred.description,
                        region_id: pred.place_id // Assuming place_id can be used as region_id or similar
                    };
                    html += createLocationItemHtml(location);
                });

                dropdown.innerHTML = html;
                addClickListeners();
            } else {
                dropdown.innerHTML = '<div style="padding: 10px 15px; color: #64748b; font-size: 0.9rem;">No results found</div>';
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
            dropdown.style.display = 'none';
        }
    }, 300);

    // Input listener
    input.addEventListener('input', function () {
        const query = this.value.trim();
        if (query.length === 0) {
            showPopular();
        } else {
            performSearch(query);
        }
    });

    // Focus listener
    input.addEventListener('focus', function () {
        if (this.value.trim().length === 0) {
            showPopular();
        }
    });

    // Blur listener (delayed)
    input.addEventListener('blur', function () {
        setTimeout(() => {
            dropdown.style.display = 'none';
        }, 200);
    });

    function showPopular() {
        let html = '<div style="padding: 8px 15px; font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase; letter-spacing: 0.5px;">Popular Destinations</div>';
        popularHotelDestinationsResults.forEach(loc => {
            html += createLocationItemHtml(loc);
        });
        dropdown.innerHTML = html;
        dropdown.style.display = 'block';
        addClickListeners();
    }

    function createLocationItemHtml(location) {
        const fullDesc = location.full || (location.country ? `${location.name}, ${location.country}` : location.name);
        return `
            <div class="location-item" data-name="${location.name}" data-country="${location.country}" 
                data-full="${fullDesc}"
                style="padding: 10px 15px; cursor: pointer; display: flex; align-items: flex-start; gap: 10px; transition: background 0.2s;">
                <div style="background: #f1f5f9; width: 32px; height: 32px; border-radius: 50%; display: flex; align-items: center; justify-content: center; color: #3b82f6;">
                    <i class="fas fa-map-marker-alt"></i>
                </div>
                <div>
                    <div style="font-weight: 500; color: #1e293b;">${location.name}</div>
                    <div style="font-size: 0.85rem; color: #64748b;">${location.country || ''}</div>
                </div>
            </div>
        `;
    }

    function addClickListeners() {
        dropdown.querySelectorAll('.location-item').forEach(item => {
            item.addEventListener('mouseenter', () => item.style.background = '#f8fafc');
            item.addEventListener('mouseleave', () => item.style.background = 'transparent');

            item.addEventListener('click', function () {
                input.value = this.dataset.full;
                dropdown.style.display = 'none';
            });

            // Prevent blur event from closing dropdown before click registers
            item.addEventListener('mousedown', (e) => e.preventDefault());
        });
    }
}
