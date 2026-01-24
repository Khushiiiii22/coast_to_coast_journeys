/**
 * Coast to Coast Journeys - Hotel Details Page
 * Handles hotel details display and room selection
 */

document.addEventListener('DOMContentLoaded', function () {
    initHotelDetails();
});

// Global state
let selectedRate = null;
let currentHotel = null;
let searchParams = null;

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

        // Fetch hotel details
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
    const destination = searchParams?.destination || 'India';

    return {
        id: hotelId,
        name: name,
        star_rating: Math.floor(Math.random() * 2) + 4,
        guest_rating: (Math.random() * 1 + 4).toFixed(1),
        review_count: Math.floor(Math.random() * 500) + 100,
        address: `123 Hotel Street, ${destination}`,
        description: `Experience luxury and comfort at ${name}. Our hotel offers world-class amenities, exceptional service, and a prime location. Whether you're traveling for business or leisure, we ensure an unforgettable stay with our modern facilities and warm hospitality.`,
        images: [
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800',
            'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=800',
            'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=800',
            'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=800'
        ],
        latitude: 28.6139 + (Math.random() - 0.5) * 0.1,
        longitude: 77.2090 + (Math.random() - 0.5) * 0.1,
        amenities: ['wifi', 'pool', 'parking', 'spa', 'restaurant', 'gym', 'bar', 'room_service'],
        rates: [
            {
                book_hash: `demo_hash_1_${Date.now()}`,
                room_name: 'Deluxe Room',
                room_description: 'Spacious room with city view, king bed, and modern amenities.',
                meal_plan: 'breakfast',
                price: Math.floor(Math.random() * 5000) + 8000,
                original_price: Math.floor(Math.random() * 3000) + 12000,
                currency: 'INR',
                cancellation: 'free',
                features: ['King Bed', 'City View', '45 sqm', 'Free WiFi']
            },
            {
                book_hash: `demo_hash_2_${Date.now()}`,
                room_name: 'Premium Suite',
                room_description: 'Luxurious suite with separate living area and premium amenities.',
                meal_plan: 'halfboard',
                price: Math.floor(Math.random() * 8000) + 15000,
                original_price: Math.floor(Math.random() * 5000) + 20000,
                currency: 'INR',
                cancellation: 'free',
                features: ['King Bed', 'Sea View', '65 sqm', 'Lounge Access', 'Butler Service']
            },
            {
                book_hash: `demo_hash_3_${Date.now()}`,
                room_name: 'Standard Room',
                room_description: 'Comfortable room with all essential amenities for a pleasant stay.',
                meal_plan: 'nomeal',
                price: Math.floor(Math.random() * 3000) + 5000,
                currency: 'INR',
                cancellation: 'non-refundable',
                features: ['Queen Bed', 'Garden View', '30 sqm', 'Free WiFi']
            }
        ]
    };
}

/**
 * Display hotel details
 */
function displayHotelDetails(hotel) {
    hideLoading();
    document.getElementById('hotelContent').classList.remove('hidden');

    // Update page title and breadcrumb
    document.title = `${hotel.name} | Coast To Coast Journeys`;
    document.getElementById('hotelNameBreadcrumb').textContent = hotel.name;

    // Gallery
    const images = hotel.images || [hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=800'];
    document.getElementById('galleryMain').style.backgroundImage = `url('${images[0]}')`;

    const thumbsContainer = document.getElementById('galleryThumbs');
    thumbsContainer.innerHTML = '';
    images.forEach((img, index) => {
        const thumb = document.createElement('div');
        thumb.className = `gallery-thumb ${index === 0 ? 'active' : ''}`;
        thumb.style.backgroundImage = `url('${img}')`;
        thumb.addEventListener('click', () => {
            document.getElementById('galleryMain').style.backgroundImage = `url('${img}')`;
            document.querySelectorAll('.gallery-thumb').forEach(t => t.classList.remove('active'));
            thumb.classList.add('active');
        });
        thumbsContainer.appendChild(thumb);
    });

    // Hotel info
    document.getElementById('hotelStars').innerHTML = HotelUtils.generateStars(hotel.star_rating || 4);
    document.getElementById('hotelName').textContent = hotel.name;
    document.getElementById('hotelAddress').querySelector('span').textContent = hotel.address || 'Location available at booking';
    document.getElementById('hotelRating').textContent = hotel.guest_rating || '4.0';
    document.getElementById('ratingLabel').textContent = getRatingLabel(hotel.guest_rating || 4);
    document.getElementById('reviewCount').textContent = `(${hotel.review_count || 0} reviews)`;
    document.getElementById('hotelDescription').textContent = hotel.description || 'Experience exceptional hospitality at this wonderful property.';

    // Amenities
    displayAmenities(hotel.amenities || []);

    // Rates
    displayRates(hotel.rates || []);

    // Map
    if (hotel.latitude && hotel.longitude) {
        displayMap(hotel.latitude, hotel.longitude);
    }

    // Booking summary
    updateBookingSummary();
}

/**
 * Display amenities grid
 */
function displayAmenities(amenities) {
    const grid = document.getElementById('amenitiesGrid');
    const amenityData = {
        wifi: { icon: 'fa-wifi', label: 'Free WiFi' },
        pool: { icon: 'fa-swimming-pool', label: 'Swimming Pool' },
        parking: { icon: 'fa-parking', label: 'Free Parking' },
        spa: { icon: 'fa-spa', label: 'Spa & Wellness' },
        restaurant: { icon: 'fa-utensils', label: 'Restaurant' },
        gym: { icon: 'fa-dumbbell', label: 'Fitness Center' },
        bar: { icon: 'fa-glass-martini-alt', label: 'Bar/Lounge' },
        room_service: { icon: 'fa-concierge-bell', label: 'Room Service' },
        ac: { icon: 'fa-snowflake', label: 'Air Conditioning' },
        laundry: { icon: 'fa-tshirt', label: 'Laundry Service' }
    };

    grid.innerHTML = '';
    amenities.forEach(a => {
        const data = amenityData[a] || { icon: 'fa-check', label: a };
        const item = document.createElement('div');
        item.className = 'amenity-item';
        item.innerHTML = `<i class="fas ${data.icon}"></i> <span>${data.label}</span>`;
        grid.appendChild(item);
    });
}

/**
 * Display room rates
 */
function displayRates(rates) {
    const container = document.getElementById('ratesList');
    container.innerHTML = '';

    if (rates.length === 0) {
        container.innerHTML = '<p class="no-rates">No rooms available for selected dates.</p>';
        return;
    }

    rates.forEach((rate, index) => {
        const card = createRateCard(rate, index);
        container.appendChild(card);
    });
}

/**
 * Create rate card element
 */
function createRateCard(rate, index) {
    const card = document.createElement('div');
    card.className = 'rate-card';
    card.dataset.rateIndex = index;

    const price = HotelUtils.formatPrice(rate.price);
    const originalPrice = rate.original_price ? HotelUtils.formatPrice(rate.original_price) : null;
    const mealPlan = HotelUtils.getMealPlanText(rate.meal_plan);
    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = HotelUtils.formatPrice(rate.price * nights);

    const featuresHtml = (rate.features || []).map(f =>
        `<span class="rate-feature"><i class="fas fa-check"></i> ${f}</span>`
    ).join('');

    const cancellationBadge = rate.cancellation === 'free'
        ? '<span class="cancellation-badge free"><i class="fas fa-check-circle"></i> Free Cancellation</span>'
        : '<span class="cancellation-badge non-refund"><i class="fas fa-info-circle"></i> Non-refundable</span>';

    card.innerHTML = `
        <div class="rate-card-header">
            <div class="rate-info">
                <h3 class="rate-room-name">${rate.room_name}</h3>
                <p class="rate-meal-plan"><i class="fas fa-utensils"></i> ${mealPlan}</p>
                ${cancellationBadge}
            </div>
            <div class="rate-price">
                ${originalPrice ? `<span class="original-price">${originalPrice}</span>` : ''}
                <span class="rate-per-night">${price} <small>/night</small></span>
                <span class="rate-total">${totalPrice} <small>total</small></span>
            </div>
        </div>
        <p class="rate-description">${rate.room_description || ''}</p>
        <div class="rate-features">${featuresHtml}</div>
        <button class="book-rate-btn" data-rate-index="${index}">
            <i class="fas fa-bookmark"></i> Select Room
        </button>
    `;

    card.querySelector('.book-rate-btn').addEventListener('click', () => {
        selectRate(rate, index);
    });

    return card;
}

/**
 * Select a rate
 */
function selectRate(rate, index) {
    selectedRate = rate;

    // Update UI
    document.querySelectorAll('.rate-card').forEach(card => {
        card.classList.remove('selected');
    });
    document.querySelector(`.rate-card[data-rate-index="${index}"]`).classList.add('selected');

    // Update booking sidebar
    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = rate.price * nights;

    document.getElementById('selectedRoomBox').classList.remove('hidden');
    document.getElementById('selectedRoomName').textContent = rate.room_name;
    document.getElementById('selectedMealPlan').textContent = HotelUtils.getMealPlanText(rate.meal_plan);

    document.getElementById('bookingTotalBox').classList.remove('hidden');
    document.getElementById('totalPrice').textContent = HotelUtils.formatPrice(totalPrice);

    document.getElementById('selectRoomPrompt').classList.add('hidden');
    document.getElementById('proceedToBookBtn').classList.remove('hidden');
    document.getElementById('proceedToBookBtn').disabled = false;

    // Save selected rate
    SearchSession.saveSelectedRate({
        ...rate,
        total_price: totalPrice,
        nights: nights
    });

    showNotification(`${rate.room_name} selected!`, 'success');
}

/**
 * Update booking summary
 */
function updateBookingSummary() {
    if (searchParams) {
        document.getElementById('summaryCheckin').textContent = HotelUtils.formatDate(searchParams.checkin);
        document.getElementById('summaryCheckout').textContent = HotelUtils.formatDate(searchParams.checkout);

        const nights = HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout);
        document.getElementById('summaryNights').textContent = nights;
        document.getElementById('summaryRooms').textContent = searchParams.rooms || 1;
        document.getElementById('summaryGuests').textContent = (searchParams.adults || 2) + (searchParams.children_ages?.length || 0);
    }
}

/**
 * Display map
 */
function displayMap(lat, lng) {
    const mapUrl = HotelAPI.getStaticMapUrl(lat, lng, 15, '600x300');

    // If Google Maps not configured, use OpenStreetMap embed
    const mapImg = document.getElementById('mapImage');
    if (mapUrl) {
        mapImg.src = mapUrl;
    } else {
        // Fallback to OpenStreetMap
        document.getElementById('hotelMap').innerHTML = `
            <iframe 
                width="100%" 
                height="300" 
                frameborder="0" 
                style="border-radius: 12px;"
                src="https://www.openstreetmap.org/export/embed.html?bbox=${lng - 0.01},${lat - 0.01},${lng + 0.01},${lat + 0.01}&marker=${lat},${lng}&layers=M"
            ></iframe>
        `;
    }
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Proceed to book button
    document.getElementById('proceedToBookBtn').addEventListener('click', proceedToBooking);

    // Back to results
    document.querySelector('.breadcrumb a[href="hotel-results.html"]')?.addEventListener('click', (e) => {
        // Keep search results in session, just go back
    });
}

/**
 * Proceed to booking
 */
function proceedToBooking() {
    if (!selectedRate) {
        showNotification('Please select a room first', 'warning');
        return;
    }

    // Save booking data
    SearchSession.saveBookingData({
        hotel: currentHotel,
        rate: selectedRate,
        search_params: searchParams
    });

    window.location.href = 'payment-checkout.html';
}

/**
 * Get rating label
 */
function getRatingLabel(rating) {
    if (rating >= 4.5) return 'Excellent';
    if (rating >= 4) return 'Very Good';
    if (rating >= 3.5) return 'Good';
    if (rating >= 3) return 'Average';
    return 'Fair';
}

/**
 * Get default dates
 */
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

// UI helper functions
function hideLoading() {
    document.getElementById('loadingState').classList.add('hidden');
}

function showError(message) {
    hideLoading();
    document.getElementById('hotelContent').innerHTML = `
        <div class="error-state">
            <i class="fas fa-exclamation-circle"></i>
            <h3>Error Loading Hotel</h3>
            <p>${message}</p>
            <a href="hotel-results.html" class="btn btn-primary">Back to Results</a>
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
