/**
 * C2C Journeys - Hotel Results Page
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
            children_ages: []
        };

        // If rooms is array, update total adults
        if (Array.isArray(params.rooms)) {
            params.adults = params.rooms.reduce((sum, r) => sum + (r.adults || 0), 0);
        }
        SearchSession.saveSearchParams(params);

        // Clear previous results to force new search
        SearchSession.remove(SearchSession.KEYS.SEARCH_RESULTS);
    }

    // Get search params from session
    const searchParams = SearchSession.getSearchParams();

    if (!searchParams) {
        // No search params, redirect to home
        showNotification('Please search for hotels first', 'warning');
        setTimeout(() => {
            window.location.href = 'index.html#hotels';
        }, 2000);
        return;
    }

    // Update search summary
    updateSearchSummary(searchParams);

    // Setup event listeners
    setupEventListeners();

    // Check for cached results first
    const cachedResults = SearchSession.getSearchResults();
    if (cachedResults && cachedResults.hotels) {
        displayResults(cachedResults);
    } else {
        // Perform search
        await performSearch(searchParams);
    }
}

/**
 * Update search summary bar
 */
function updateSearchSummary(params) {
    document.getElementById('destinationText').textContent = params.destination || 'Unknown';
    document.getElementById('checkinText').textContent = HotelUtils.formatDate(params.checkin);
    document.getElementById('checkoutText').textContent = HotelUtils.formatDate(params.checkout);

    const nights = HotelUtils.calculateNights(params.checkin, params.checkout);
    document.getElementById('nightsText').textContent = `${nights} Night${nights > 1 ? 's' : ''}`;

    let roomCount = 0;
    let adultCount = 0;

    if (Array.isArray(params.rooms)) {
        roomCount = params.rooms.length;
        adultCount = params.rooms.reduce((acc, r) => acc + (r.adults || 0), 0);
        const childCount = params.rooms.reduce((acc, r) => acc + (r.children || 0), 0);
        if (childCount > 0) {
            // Optional: Display children count if needed, but for now stick to main text pattern or append it
            // document.getElementById('guestsText').textContent += `, ${childCount} Child${childCount > 1 ? 'ren' : ''}`;
            // Let's just include it in the main text logic if you wish, or stick to Adults as per existing code.
            // The existing code only showed Adults. Let's make it comprehensive.
            document.getElementById('guestsText').textContent = `${roomCount} Room${roomCount > 1 ? 's' : ''}, ${adultCount} Adult${adultCount > 1 ? 's' : ''}, ${childCount} Child${childCount !== 1 ? 'ren' : ''}`;
            return;
        }
    } else {
        roomCount = params.rooms || 1;
        adultCount = params.adults || 2;
    }

    document.getElementById('guestsText').textContent = `${roomCount} Room${roomCount > 1 ? 's' : ''}, ${adultCount} Adult${adultCount > 1 ? 's' : ''}`;
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
 * Perform hotel search
 */
async function performSearch(params) {
    showLoading();

    try {
        // Check API health first
        try {
            await HotelAPI.healthCheck();
        } catch (e) {
            console.log('Backend server not reachable, using demo data');
            showDemoResults(params);
            return;
        }

        // Perform search
        const result = await HotelAPI.searchByDestination(params);

        if (result.success && result.data?.hotels?.length > 0) {
            SearchSession.saveSearchResults(result);
            displayResults(result);
        } else if (result.success) {
            // API succeeded but no results - show demo data
            console.log('No hotels found from API, using demo data');
            showDemoResults(params);
        } else {
            // API returned an error - fall back to demo data for better UX
            console.log('API error, using demo data:', result.error);
            showDemoResults(params);
        }
    } catch (error) {
        console.error('Search error:', error);
        // Always fall back to demo data on any error
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
    showHotelsGrid();
}

/**
 * Show demo results when API is not available
 */
function showDemoResults(params) {
    const demoHotels = generateDemoHotels(params.destination, 12);

    const result = {
        success: true,
        data: { hotels: demoHotels },
        demo: true
    };

    SearchSession.saveSearchResults(result);
    displayResults(result);

    showNotification('Showing demo hotels. Connect backend for real results.', 'info');
}

/**
 * Generate demo hotel data
 */
function generateDemoHotels(destination, count) {
    const hotelNames = [
        'The Grand Palace', 'Ocean View Resort', 'Mountain Retreat',
        'City Center Hotel', 'Luxury Suites', 'Beach Paradise',
        'Heritage Inn', 'Modern Plaza', 'Sunset Villa',
        'Garden Resort', 'Royal Hotel', 'Comfort Stay'
    ];

    const images = [
        'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600',
        'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600',
        'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=600',
        'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600',
        'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=600',
        'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600'
    ];

    const hotels = [];
    for (let i = 0; i < count; i++) {
        hotels.push({
            id: `demo_hotel_${i + 1}`,
            name: hotelNames[i % hotelNames.length] + (i >= hotelNames.length ? ` ${Math.floor(i / hotelNames.length) + 1}` : ''),
            star_rating: Math.floor(Math.random() * 3) + 3,
            guest_rating: (Math.random() * 2 + 3).toFixed(1),
            review_count: Math.floor(Math.random() * 500) + 50,
            address: `${destination}, India`,
            image: images[i % images.length],
            price: Math.floor(Math.random() * 20000) + 2000,
            original_price: Math.floor(Math.random() * 5000) + 25000,
            currency: 'INR',
            amenities: ['wifi', 'pool', 'parking', 'restaurant'].slice(0, Math.floor(Math.random() * 4) + 1),
            meal_plan: ['nomeal', 'breakfast', 'halfboard'][Math.floor(Math.random() * 3)],
            rates: [{
                book_hash: `demo_hash_${i}_${Date.now()}`,
                room_name: 'Deluxe Room',
                price: Math.floor(Math.random() * 20000) + 2000
            }]
        });
    }

    return hotels;
}

/**
 * Render hotels grid
 */
function renderHotels(hotels, append = false) {
    const grid = document.getElementById('hotelsGrid');

    if (!append) {
        grid.innerHTML = '';
    }

    hotels.forEach(hotel => {
        const card = createHotelCard(hotel);
        grid.appendChild(card);
    });
}

/**
 * Create hotel card element
 */
function createHotelCard(hotel) {
    const card = document.createElement('div');
    card.className = 'hotel-card';
    card.dataset.hotelId = hotel.id;

    const stars = HotelUtils.generateStars(hotel.star_rating || 4);
    const price = HotelUtils.formatPrice(hotel.price || hotel.rates?.[0]?.price || 0);
    const originalPrice = hotel.original_price ? HotelUtils.formatPrice(hotel.original_price) : null;
    const mealPlan = HotelUtils.getMealPlanText(hotel.meal_plan);

    const amenitiesHtml = (hotel.amenities || []).slice(0, 4).map(a => {
        const icons = {
            wifi: '<i class="fas fa-wifi" title="WiFi"></i>',
            pool: '<i class="fas fa-swimming-pool" title="Pool"></i>',
            parking: '<i class="fas fa-parking" title="Parking"></i>',
            spa: '<i class="fas fa-spa" title="Spa"></i>',
            restaurant: '<i class="fas fa-utensils" title="Restaurant"></i>',
            gym: '<i class="fas fa-dumbbell" title="Gym"></i>'
        };
        return icons[a] || '';
    }).join('');

    card.innerHTML = `
        <div class="hotel-card-image" style="background-image: url('${hotel.image || hotel.images?.[0] || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600'}')">
            <button class="wishlist-btn" data-hotel-id="${hotel.id}">
                <i class="far fa-heart"></i>
            </button>
            ${hotel.discount ? `<span class="discount-badge">${hotel.discount}% OFF</span>` : ''}
        </div>
        <div class="hotel-card-content">
            <div class="hotel-stars">${stars}</div>
            <h3 class="hotel-name">${hotel.name}</h3>
            <p class="hotel-address"><i class="fas fa-map-marker-alt"></i> ${hotel.address || 'Location available'}</p>
            <div class="hotel-amenities">${amenitiesHtml}</div>
            <div class="hotel-rating">
                <span class="rating-score">${hotel.guest_rating || '4.0'}</span>
                <span class="rating-text">${getRatingText(hotel.guest_rating || 4)}</span>
                <span class="review-count">(${hotel.review_count || 0} reviews)</span>
            </div>
            <div class="hotel-price-row">
                <div class="price-info">
                    ${originalPrice ? `<span class="original-price">${originalPrice}</span>` : ''}
                    <span class="current-price">${price}</span>
                    <span class="per-night">per night</span>
                </div>
                <button class="book-now-btn" data-hotel-id="${hotel.id}" style="background: linear-gradient(135deg, #28a745, #20c997); margin-right: 10px;">
                    <i class="fas fa-check"></i> Book Now
                </button>
                <button class="view-deal-btn" data-hotel-id="${hotel.id}">
                    View Deal <i class="fas fa-arrow-right"></i>
                </button>
            </div>
            <p class="meal-plan"><i class="fas fa-utensils"></i> ${mealPlan}</p>
        </div>
    `;

    // Add click event to book now button
    card.querySelector('.book-now-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        bookHotel(hotel);
    });

    // Add click event to view deal button
    card.querySelector('.view-deal-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        viewHotelDetails(hotel);
    });

    // Add click event to whole card
    card.addEventListener('click', () => {
        viewHotelDetails(hotel);
    });

    // Add wishlist toggle
    card.querySelector('.wishlist-btn').addEventListener('click', (e) => {
        e.stopPropagation();
        toggleWishlist(e.currentTarget, hotel);
    });

    return card;
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
    // Save selected hotel to session
    SearchSession.saveSelectedHotel(hotel);

    // Navigate to hotel details page
    window.location.href = `hotel-details.html?id=${hotel.id}`;
}

/**
 * Book hotel - redirect to payment
 */
function bookHotel(hotel) {
    const searchParams = SearchSession.getSearchParams();
    const nights = HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout);

    // Prepare rate object
    const rate = hotel.rates?.[0] || {
        room_name: 'Standard Room',
        price: hotel.price,
        meal_plan: hotel.meal_plan || 'nomeal',
        cancellation: 'non-refundable'
    };

    // Add total info to rate
    rate.total_price = rate.price * nights;
    rate.nights = nights;

    // Save using session helper
    SearchSession.saveBookingData({
        hotel: hotel,
        rate: rate,
        search_params: searchParams
    });



    // Redirect to payment checkout
    window.location.href = 'payment-checkout.html';
}

/**
 * Toggle wishlist
 */
function toggleWishlist(btn, hotel) {
    const icon = btn.querySelector('i');

    if (icon.classList.contains('far')) {
        icon.classList.remove('far');
        icon.classList.add('fas');
        icon.style.color = '#ef4444';
        showNotification(`${hotel.name} added to wishlist!`, 'success');
    } else {
        icon.classList.remove('fas');
        icon.classList.add('far');
        icon.style.color = '';
        showNotification(`${hotel.name} removed from wishlist`, 'info');
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
    // Modify search buttons
    document.getElementById('modifySearchBtn').addEventListener('click', openModifyModal);
    document.getElementById('modifySearchBtn2')?.addEventListener('click', openModifyModal);

    // Close modify modal
    document.getElementById('closeModifyModal').addEventListener('click', closeModifyModal);
    document.querySelector('#modifySearchModal .modal-overlay').addEventListener('click', closeModifyModal);

    // Modify search form
    document.getElementById('modifySearchForm').addEventListener('submit', handleModifySearch);

    // Filters
    document.getElementById('priceRange').addEventListener('input', (e) => {
        document.getElementById('maxPriceLabel').textContent = `₹${parseInt(e.target.value).toLocaleString()}+`;
    });
    document.getElementById('priceRange').addEventListener('change', applyFiltersAndSort);

    document.querySelectorAll('.star-filter input').forEach(input => {
        input.addEventListener('change', applyFiltersAndSort);
    });

    // Sort
    document.getElementById('sortSelect').addEventListener('change', applyFiltersAndSort);

    // Clear filters
    document.getElementById('clearFilters').addEventListener('click', clearFilters);

    // Retry button
    document.getElementById('retryBtn').addEventListener('click', () => {
        const params = SearchSession.getSearchParams();
        if (params) performSearch(params);
    });

    // Load more
    document.getElementById('loadMoreBtn').addEventListener('click', loadMoreHotels);
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
        document.getElementById('modifyRooms').value = params.rooms || 1;
        document.getElementById('modifyAdults').value = params.adults || 2;
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
 * Handle modify search form
 */
function handleModifySearch(e) {
    e.preventDefault();

    const params = {
        destination: document.getElementById('modifyDestination').value,
        checkin: document.getElementById('modifyCheckin').value,
        checkout: document.getElementById('modifyCheckout').value,
        rooms: parseInt(document.getElementById('modifyRooms').value),
        adults: parseInt(document.getElementById('modifyAdults').value),
        children_ages: []
    };

    SearchSession.saveSearchParams(params);
    SearchSession.remove(SearchSession.KEYS.SEARCH_RESULTS);

    closeModifyModal();
    updateSearchSummary(params);
    performSearch(params);
}

// UI helper functions
function showLoading() {
    document.getElementById('loadingState').classList.remove('hidden');
    document.getElementById('hotelsGrid').classList.add('hidden');
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
    document.getElementById('hotelsGrid').classList.add('hidden');
}

function showNoResults() {
    hideLoading();
    document.getElementById('noResultsState').classList.remove('hidden');
    document.getElementById('hotelsGrid').classList.add('hidden');
}

function showHotelsGrid() {
    document.getElementById('hotelsGrid').classList.remove('hidden');
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
