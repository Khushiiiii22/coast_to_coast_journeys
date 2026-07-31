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
            region_id: urlParams.get('region_id') || undefined,
            hotel_id: urlParams.get('hotel_id') || undefined,
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
function normalizeDateStr(dateStr) {
    if (!dateStr) return '';
    const str = String(dateStr).trim();
    if (/^\d{4}-\d{2}-\d{2}$/.test(str)) return str;
    const ddmmyyyy = str.match(/^(\d{1,2})[-/](\d{1,2})[-/](\d{4})$/);
    if (ddmmyyyy) {
        return `${ddmmyyyy[3]}-${ddmmyyyy[2].padStart(2, '0')}-${ddmmyyyy[1].padStart(2, '0')}`;
    }
    try {
        const d = new Date(str);
        if (!isNaN(d.getTime())) {
            return d.getFullYear() + '-' + String(d.getMonth() + 1).padStart(2, '0') + '-' + String(d.getDate()).padStart(2, '0');
        }
    } catch (e) {}
    return '';
}

function parseSafeDate(dateStr) {
    const norm = normalizeDateStr(dateStr);
    if (norm) {
        const [y, m, d] = norm.split('-').map(Number);
        if (!isNaN(y) && !isNaN(m) && !isNaN(d)) {
            return new Date(y, m - 1, d);
        }
    }
    return new Date();
}

function updateSearchBar(params) {
    const destinationEl = document.getElementById('searchDestination');
    const datesEl = document.getElementById('searchDates');
    const travelersEl = document.getElementById('searchTravelers');

    if (destinationEl) {
        destinationEl.textContent = params.destination || 'Select destination';
    }

    if (datesEl && params.checkin && params.checkout) {
        try {
            const checkinDate = parseSafeDate(params.checkin);
            const checkoutDate = parseSafeDate(params.checkout);
            const options = { weekday: 'short', month: 'short', day: 'numeric' };
            datesEl.textContent = `${checkinDate.toLocaleDateString('en-US', options)} - ${checkoutDate.toLocaleDateString('en-US', options)}`;
        } catch (e) {
            datesEl.textContent = `${params.checkin} - ${params.checkout}`;
        }
    }

    if (travelersEl) {
        let roomCount = Array.isArray(params.rooms) ? params.rooms.length : (params.rooms || 1);
        let adultCount = Array.isArray(params.rooms)
            ? params.rooms.reduce((sum, r) => sum + (r.adults || 0) + (r.children || r.childAges?.length || 0), 0)
            : ((params.adults || 2) + (params.children_ages ? params.children_ages.length : 0));
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
        const errorMsg = error.message?.includes('timed out')
            ? 'The search request timed out while fetching partner rates. Please try again.'
            : (error.message || 'Unable to load hotels. Please try again.');
        showError(errorMsg);
        showNotification(errorMsg, 'error');
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

    const countEl = document.getElementById('resultsCount');
    if (countEl) countEl.textContent = hotels.length;

    updateFilterCounts();
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
        images = hotel.images.map(img => typeof img === 'string' ? img.replace('{size}', '1024x768') : img);
    } else if (hotel.image) {
        images = [typeof hotel.image === 'string' ? hotel.image.replace('{size}', '1024x768') : hotel.image];
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
                    ${(() => {
                        const cancelStatus = HotelUtils.getCancellationStatus(hotel);
                        return cancelStatus.isRefundable ? '<span class="refundable-badge"><i class="fas fa-check-circle"></i> Fully refundable</span>' : '';
                    })()}
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
            let popupImg = hotel.image || hotel.images?.[0] || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=200';
            if (typeof popupImg === 'string') popupImg = popupImg.replace('{size}', '1024x768');
            
            const marker = L.marker([hotel.latitude, hotel.longitude])
                .bindPopup(`
                    <div class="hotel-map-popup">
                        <div class="popup-image" style="background-image: url('${popupImg}')"></div>
                        <div class="popup-title">${hotel.name}</div>
                        <div class="popup-rating">
                            <span class="rating-badge">${hotel.guest_rating || '4.0'}</span>
                            <span>${getRatingText(hotel.guest_rating)}</span>
                        </div>
                        <div class="popup-price">${HotelUtils.formatPrice(hotel.price || hotel.rates?.[0]?.price || 0, hotel.currency)} / night</div>
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
 * Update filter counts dynamically based on loaded hotels
 */
function updateFilterCounts() {
    if (!allHotels || allHotels.length === 0) return;

    const counts = {
        city_center: 0,
        hotel: 0,
        breakfast: 0,
        free_cancellation: 0,
        pool: 0
    };

    allHotels.forEach(h => {
        const addr = (h.address || '').toLowerCase();
        const name = (h.name || '').toLowerCase();
        const type = (h.property_type || '').toLowerCase();
        const amenities = (h.amenities || []).map(a => String(a).toLowerCase());
        const meal = (h.rates?.[0]?.meal_plan || h.meal_plan || '').toLowerCase();
        const cancel = (h.rates?.[0]?.cancellation || h.cancellation || '').toLowerCase();

        if (addr.includes('center') || addr.includes('downtown') || name.includes('center') || (h.guest_rating && h.guest_rating >= 4.5)) {
            counts.city_center++;
        }
        if (!type || type.includes('hotel') || type.includes('resort')) {
            counts.hotel++;
        }
        if (meal.includes('breakfast') || meal.includes('halfboard') || meal.includes('fullboard') || meal.includes('allinclusive') || amenities.includes('breakfast')) {
            counts.breakfast++;
        }
        if (h.cancellation_info?.is_free_cancellation || h.rates?.[0]?.cancellation_info?.is_free_cancellation) {
            counts.free_cancellation++;
        }
        if (amenities.some(a => a.includes('pool') || a.includes('swimming'))) {
            counts.pool++;
        }
    });

    document.querySelectorAll('.filter-checkbox').forEach(label => {
        const input = label.querySelector('input');
        const countSpan = label.querySelector('.filter-count');
        if (input && countSpan && counts[input.value] !== undefined) {
            countSpan.textContent = `(${counts[input.value]})`;
        }
    });
}

/**
 * Apply filters and sort
 */
function applyFiltersAndSort() {
    let hotels = [...allHotels];

    // 1. Tab navigation filter (All stays, Hotels, Homes)
    const activeTabBtn = document.querySelector('.tab-btn.active');
    const activeTab = activeTabBtn?.dataset?.tab || 'all';
    if (activeTab === 'hotels') {
        hotels = hotels.filter(h => {
            const type = (h.property_type || 'hotel').toLowerCase();
            return type.includes('hotel') || type.includes('resort') || type.includes('boutique');
        });
    } else if (activeTab === 'homes') {
        hotels = hotels.filter(h => {
            const type = (h.property_type || '').toLowerCase();
            return type.includes('home') || type.includes('apartment') || type.includes('villa') || type.includes('house');
        });
    }

    // 2. Apply price filter
    const priceEl = document.getElementById('priceRange');
    if (priceEl) {
        const maxPrice = parseInt(priceEl.value);
        hotels = hotels.filter(h => (h.price || h.rates?.[0]?.price || 0) <= maxPrice);
    }

    // 3. Apply star filter
    const starFilters = document.querySelectorAll('.star-filter input:checked');
    if (starFilters.length > 0) {
        const selectedStars = Array.from(starFilters).map(i => parseInt(i.value));
        hotels = hotels.filter(h => selectedStars.includes(h.star_rating || 4));
    }

    // 4. Apply property name search
    const propertySearch = document.getElementById('propertySearch')?.value?.toLowerCase()?.trim();
    if (propertySearch) {
        hotels = hotels.filter(h => h.name.toLowerCase().includes(propertySearch));
    }

    // 5. Apply rating filter
    const activeRatingPill = document.querySelector('.rating-pill.active');
    if (activeRatingPill && activeRatingPill.dataset.rating !== 'any') {
        const minRating = parseFloat(activeRatingPill.dataset.rating);
        hotels = hotels.filter(h => parseFloat(h.guest_rating || 0) >= minRating);
    }

    // 6. Apply popular filters checkboxes
    const popularFilters = document.querySelectorAll('.filter-checkbox input:checked');
    popularFilters.forEach(checkbox => {
        const val = checkbox.value;
        if (val === 'city_center') {
            hotels = hotels.filter(h => {
                const addr = (h.address || '').toLowerCase();
                const name = (h.name || '').toLowerCase();
                return addr.includes('center') || addr.includes('downtown') || name.includes('center') || (h.guest_rating && h.guest_rating >= 4.5);
            });
        } else if (val === 'hotel') {
            hotels = hotels.filter(h => {
                const type = (h.property_type || 'hotel').toLowerCase();
                return type.includes('hotel') || type.includes('resort');
            });
        } else if (val === 'breakfast') {
            hotels = hotels.filter(h => {
                const meal = (h.rates?.[0]?.meal_plan || h.meal_plan || '').toLowerCase();
                const amenities = (h.amenities || []).map(a => String(a).toLowerCase());
                return meal.includes('breakfast') || meal.includes('halfboard') || meal.includes('fullboard') || meal.includes('allinclusive') || amenities.includes('breakfast');
            });
        } else if (val === 'free_cancellation') {
            hotels = hotels.filter(h => {
                return h.cancellation_info?.is_free_cancellation || h.rates?.[0]?.cancellation_info?.is_free_cancellation;
            });
        } else if (val === 'pool') {
            hotels = hotels.filter(h => {
                const amenities = (h.amenities || []).map(a => String(a).toLowerCase());
                return amenities.some(a => a.includes('pool') || a.includes('swimming'));
            });
        }
    });

    // 7. Apply amenities filters checkboxes
    const amenityFilters = document.querySelectorAll('.amenity-filter input:checked');
    if (amenityFilters.length > 0) {
        const selectedAmenities = Array.from(amenityFilters).map(i => i.value.toLowerCase());
        hotels = hotels.filter(h => {
            const hAmenities = (h.amenities || []).map(a => String(a).toLowerCase());
            return selectedAmenities.every(req => {
                if (req === 'wifi') return hAmenities.some(a => a.includes('wifi') || a.includes('internet'));
                if (req === 'pool') return hAmenities.some(a => a.includes('pool') || a.includes('swimming'));
                if (req === 'parking') return hAmenities.some(a => a.includes('parking') || a.includes('valet'));
                if (req === 'spa') return hAmenities.some(a => a.includes('spa') || a.includes('wellness'));
                if (req === 'restaurant') return hAmenities.some(a => a.includes('restaurant') || a.includes('dining'));
                if (req === 'gym') return hAmenities.some(a => a.includes('gym') || a.includes('fitness'));
                if (req === 'ac') return hAmenities.some(a => a.includes('ac') || a.includes('air conditioning'));
                return hAmenities.includes(req);
            });
        });
    }

    // 8. Apply meal plan filters checkboxes
    const mealFilters = document.querySelectorAll('.meal-filter input:checked');
    if (mealFilters.length > 0) {
        const selectedMeals = Array.from(mealFilters).map(i => i.value.toLowerCase());
        hotels = hotels.filter(h => {
            const meal = (h.rates?.[0]?.meal_plan || h.meal_plan || '').toLowerCase();
            return selectedMeals.some(req => meal.includes(req));
        });
    }

    // 9. Apply sort
    const sortEl = document.getElementById('sortSelect');
    if (sortEl) {
        const sortValue = sortEl.value;
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
    }

    filteredHotels = hotels;
    const countEl = document.getElementById('resultsCount');
    if (countEl) countEl.textContent = hotels.length;

    currentPage = 1;
    renderHotels(hotels.slice(0, hotelsPerPage));

    // Show/hide load more
    const loadMoreDiv = document.getElementById('loadMore');
    if (loadMoreDiv) {
        if (hotels.length > hotelsPerPage) {
            loadMoreDiv.classList.remove('hidden');
        } else {
            loadMoreDiv.classList.add('hidden');
        }
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
            applyFiltersAndSort();
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

    // Date validation for modify search
    const modifyCheckin = document.getElementById('modifyCheckin');
    const modifyCheckout = document.getElementById('modifyCheckout');
    if (modifyCheckin && modifyCheckout) {
        modifyCheckin.addEventListener('change', (e) => {
            const normCheckin = normalizeDateStr(e.target.value);
            if (normCheckin) {
                const [y, m, d] = normCheckin.split('-').map(Number);
                const minCheckout = new Date(y, m - 1, d);
                minCheckout.setDate(minCheckout.getDate() + 1);
                
                const minCheckoutStr = minCheckout.getFullYear() + '-' + String(minCheckout.getMonth() + 1).padStart(2, '0') + '-' + String(minCheckout.getDate()).padStart(2, '0');
                if (/^\d{4}-\d{2}-\d{2}$/.test(minCheckoutStr)) {
                    modifyCheckout.min = minCheckoutStr;
                }
                
                if (modifyCheckout.value && modifyCheckout.value < minCheckoutStr) {
                    modifyCheckout.value = minCheckoutStr;
                }
            }
        });
    }

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

    // Popular filters
    document.querySelectorAll('.filter-checkbox input').forEach(input => {
        input.addEventListener('change', applyFiltersAndSort);
    });

    // Amenity filters
    document.querySelectorAll('.amenity-filter input').forEach(input => {
        input.addEventListener('change', applyFiltersAndSort);
    });

    // Meal plan filters
    document.querySelectorAll('.meal-filter input').forEach(input => {
        input.addEventListener('change', applyFiltersAndSort);
    });

    // Price range
    document.getElementById('priceRange')?.addEventListener('input', (e) => {
        const label = document.getElementById('maxPriceLabel');
        if (label) label.textContent = `₹${parseInt(e.target.value).toLocaleString()}+`;
    });
    document.getElementById('priceRange')?.addEventListener('change', applyFiltersAndSort);

    // Star filters
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
    const priceEl = document.getElementById('priceRange');
    if (priceEl) priceEl.value = 50000;
    const maxPriceLabel = document.getElementById('maxPriceLabel');
    if (maxPriceLabel) maxPriceLabel.textContent = '₹50,000+';

    document.querySelectorAll('.star-filter input').forEach(input => {
        input.checked = parseInt(input.value) >= 3;
    });

    document.querySelectorAll('.filter-checkbox input, .amenity-filter input, .meal-filter input').forEach(input => {
        input.checked = false;
    });

    document.querySelectorAll('.tab-btn').forEach((b, i) => {
        if (i === 0) b.classList.add('active');
        else b.classList.remove('active');
    });

    const sortEl = document.getElementById('sortSelect');
    if (sortEl) sortEl.value = 'recommended';
    
    const propSearch = document.getElementById('propertySearch');
    if (propSearch) propSearch.value = '';

    document.querySelectorAll('.rating-pill').forEach((p, i) => {
        if (i === 0) p.classList.add('active');
        else p.classList.remove('active');
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
        const checkinInput = document.getElementById('modifyCheckin');
        const checkoutInput = document.getElementById('modifyCheckout');
        
        document.getElementById('modifyDestination').value = params.destination || '';
        const regionInput = document.getElementById('modifyRegionId');
        const hotelInput = document.getElementById('modifyHotelId');
        if (regionInput) regionInput.value = params.region_id || '';
        if (hotelInput) hotelInput.value = params.hotel_id || '';
        const normCheckin = normalizeDateStr(params.checkin);
        const normCheckout = normalizeDateStr(params.checkout);
        checkinInput.value = normCheckin;
        checkoutInput.value = normCheckout;

        // Set min date constraints
        const today = new Date();
        const todayStr = today.getFullYear() + '-' + String(today.getMonth() + 1).padStart(2, '0') + '-' + String(today.getDate()).padStart(2, '0');
        checkinInput.min = todayStr;
        
        if (checkinInput.value) {
            const [y, m, d] = checkinInput.value.split('-').map(Number);
            if (!isNaN(y) && !isNaN(m) && !isNaN(d)) {
                const minCheckout = new Date(y, m - 1, d);
                minCheckout.setDate(minCheckout.getDate() + 1);
                
                const minCheckoutStr = minCheckout.getFullYear() + '-' + String(minCheckout.getMonth() + 1).padStart(2, '0') + '-' + String(minCheckout.getDate()).padStart(2, '0');
                if (/^\d{4}-\d{2}-\d{2}$/.test(minCheckoutStr)) {
                    checkoutInput.min = minCheckoutStr;
                }
                
                if (checkoutInput.value && checkoutInput.value < minCheckoutStr) {
                    checkoutInput.value = minCheckoutStr;
                }
            }
        } else {
            const minCheckout = new Date();
            minCheckout.setDate(minCheckout.getDate() + 1);
            checkoutInput.min = minCheckout.getFullYear() + '-' + String(minCheckout.getMonth() + 1).padStart(2, '0') + '-' + String(minCheckout.getDate()).padStart(2, '0');
        }

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
        region_id: document.getElementById('modifyRegionId')?.value || '',
        hotel_id: document.getElementById('modifyHotelId')?.value || '',
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

let loadingInterval;
const loadingMessages = [
    "Searching for the best available hotels...",
    "Checking live availability with our partners...",
    "Comparing prices across hundreds of properties...",
    "Almost there, finalizing your results...",
    "Just a few more seconds to get the best deals..."
];

// UI helper functions
function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('hotelsList').classList.add('hidden');
    document.getElementById('errorState').classList.add('hidden');
    document.getElementById('noResultsState').classList.add('hidden');
    
    const msgEl = document.getElementById('loadingMessage');
    if (msgEl) {
        let msgIdx = 0;
        msgEl.textContent = loadingMessages[0];
        clearInterval(loadingInterval);
        loadingInterval = setInterval(() => {
            msgIdx = (msgIdx + 1) % loadingMessages.length;
            msgEl.textContent = loadingMessages[msgIdx];
        }, 5000); // Change message every 5 seconds
    }
}

function hideLoading() {
    clearInterval(loadingInterval);
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
        const savedCurrency = localStorage.getItem('ctc_currency') || 'USD';
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
    dropdown.style.top = 'calc(100% + 6px)';
    dropdown.style.left = '0';
    dropdown.style.right = '0';
    dropdown.style.background = '#ffffff';
    dropdown.style.boxShadow = '0 16px 40px rgba(0, 0, 0, 0.14), 0 2px 6px rgba(0, 0, 0, 0.04)';
    dropdown.style.borderRadius = '16px';
    dropdown.style.border = '1px solid #e2e8f0';
    dropdown.style.zIndex = '10000';
    dropdown.style.maxHeight = '380px';
    dropdown.style.overflowY = 'auto';
    dropdown.style.padding = '8px';
    wrapper.appendChild(dropdown);

    function formatExpediaRegionItem(region) {
        const rawType = (region.type || 'region').toLowerCase();
        const name = region.name || 'Unknown';
        let mainTitle = name;
        let subtextParts = [];
        let iconClass = 'fa-location-dot';

        if (rawType.includes('airport')) {
            iconClass = 'fa-plane';
            if (region.iata) {
                mainTitle = `${name} (${region.iata} - ${name} Intl.)`;
            } else {
                mainTitle = `${name} Airport`;
            }
            if (region.country) subtextParts.push(region.country);
        } else if (rawType.includes('city')) {
            iconClass = 'fa-city';
            if (region.state) subtextParts.push(region.state);
            if (region.country) subtextParts.push(region.country);
        } else if (rawType.includes('neighborhood') || rawType.includes('district') || rawType.includes('point of interest') || rawType.includes('subway') || rawType.includes('landmark')) {
            iconClass = 'fa-building';
            if (region.city) subtextParts.push(region.city);
            if (region.state && region.state !== region.city) subtextParts.push(region.state);
            if (region.country) subtextParts.push(region.country);
        } else {
            iconClass = 'fa-location-dot';
            if (region.state) subtextParts.push(region.state);
            if (region.country) subtextParts.push(region.country);
        }

        const subtext = subtextParts.join(', ');
        const fullText = mainTitle + (subtext ? `, ${subtext}` : '');

        return { mainTitle, subtext, fullText, iconClass, region_id: region.id };
    }

    // Debounced search
    const performSearch = debounce(async (query) => {
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        try {
            dropdown.innerHTML = '<div style="padding: 14px; color: #64748b; font-size: 0.9rem;"><i class="fas fa-spinner fa-spin"></i> Searching locations...</div>';
            dropdown.style.display = 'block';

            const response = await fetch(`/api/hotels/suggest?query=${encodeURIComponent(query)}&language=en`);
            const result = await response.json();

            if (result.success && result.data) {
                const inner = result.data.data || result.data;
                const regions = inner.regions || [];
                const hotels = inner.hotels || [];
                
                if (regions.length > 0 || hotels.length > 0) {
                    let html = '';

                    regions.forEach(region => {
                        const itemData = formatExpediaRegionItem(region);
                        html += createLocationItemHtml({
                            name: itemData.mainTitle,
                            country: itemData.subtext,
                            full: itemData.fullText,
                            region_id: itemData.region_id,
                            iconClass: itemData.iconClass
                        });
                    });

                    hotels.slice(0, 5).forEach(hotel => {
                        const mainTitle = hotel.name || hotel.label || 'Hotel';
                        let subtextParts = [];
                        if (hotel.region_name) subtextParts.push(hotel.region_name);
                        if (hotel.country) subtextParts.push(hotel.country);
                        const subtext = subtextParts.join(', ') || 'Hotel';

                        html += createLocationItemHtml({
                            name: mainTitle,
                            country: subtext,
                            full: mainTitle,
                            hotel_id: hotel.id,
                            iconClass: 'fa-hotel'
                        });
                    });

                    dropdown.innerHTML = html;
                    addClickListeners();
                } else {
                    dropdown.innerHTML = '<div style="padding: 14px; color: #64748b; font-size: 0.9rem;">No locations found</div>';
                }
            } else {
                dropdown.innerHTML = '<div style="padding: 14px; color: #64748b; font-size: 0.9rem;">No locations found</div>';
            }
            
        } catch (error) {
            console.error('Autocomplete error:', error);
            dropdown.innerHTML = '<div style="padding: 14px; color: #64748b; font-size: 0.9rem;">No locations found</div>';
        }
    }, 300);

    // Input listener
    input.addEventListener('input', function () {
        const regionInput = document.getElementById('modifyRegionId');
        const hotelInput = document.getElementById('modifyHotelId');
        if (regionInput) regionInput.value = '';
        if (hotelInput) hotelInput.value = '';
        performSearch(this.value.trim());
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
        let html = '';
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
            <div class="location-item expedia-style-item" data-name="${location.name}" data-country="${location.country}" 
                data-full="${fullDesc}" data-region-id="${location.region_id || ''}" data-hotel-id="${location.hotel_id || ''}"
                style="padding: 10px 14px; cursor: pointer; display: flex; align-items: flex-start; gap: 14px; border-radius: 10px; transition: background 0.15s ease-in-out;">
                <div style="width: 24px; display: flex; justify-content: center; align-items: center; color: #1e293b; font-size: 1.15rem; margin-top: 2px;">
                    <i class="fas ${location.iconClass || 'fa-location-dot'}"></i>
                </div>
                <div style="flex: 1; min-width: 0;">
                    <div style="font-weight: 600; font-size: 0.92rem; color: #0f172a; line-height: 1.35; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${location.name}</div>
                    <div style="font-size: 0.8rem; color: #64748b; margin-top: 2px; line-height: 1.3; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">${location.country || ''}</div>
                </div>
            </div>
        `;
    }

    function addClickListeners() {
        dropdown.querySelectorAll('.location-item').forEach(item => {
            item.addEventListener('mouseenter', () => item.style.background = '#f1f5f9');
            item.addEventListener('mouseleave', () => item.style.background = 'transparent');

            item.addEventListener('click', function () {
                input.value = this.dataset.full;
                const regionInput = document.getElementById('modifyRegionId');
                const hotelInput = document.getElementById('modifyHotelId');
                if (regionInput) regionInput.value = this.dataset.regionId || '';
                if (hotelInput) hotelInput.value = this.dataset.hotelId || '';
                dropdown.style.display = 'none';
                input.blur();
            });

            // Prevent blur event from closing dropdown before click registers
            item.addEventListener('mousedown', (e) => e.preventDefault());
        });
    }
}
