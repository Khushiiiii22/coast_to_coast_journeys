/**
 * C2C Journeys - Hotel Details Page
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
 * Uses enriched endpoint that matches rates with room static data
 * Matching: rate's rg_ext.rg <-> room_groups[].rg_hash
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

        // Try enriched endpoint first (includes room images and amenities from static data)
        try {
            const enrichedResult = await HotelAPI.getEnrichedHotelDetails({
                hotel_id: hotelId,
                checkin: searchParams?.checkin || getDefaultCheckin(),
                checkout: searchParams?.checkout || getDefaultCheckout(),
                adults: searchParams?.adults || 2
            });

            if (enrichedResult.success && enrichedResult.data?.hotels?.length > 0) {
                currentHotel = enrichedResult.data.hotels[0];
                currentHotel.room_groups_matched = enrichedResult.data.room_groups_count || 0;
                displayHotelDetails(currentHotel);
                console.log(`✅ Loaded hotel with ${enrichedResult.data.room_groups_count} room groups matched`);
                return;
            }
        } catch (enrichedError) {
            console.log('Enriched endpoint not available, falling back to standard endpoint');
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

    // Fetch and display hotel policies (metapolicy_struct & metapolicy_extra_info)
    fetchHotelPolicies(hotel.id || hotel.hid);

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
 * Fetch hotel policies from RateHawk static data
 * Uses metapolicy_struct and metapolicy_extra_info (NOT deprecated policy_struct)
 */
async function fetchHotelPolicies(hotelId) {
    const loadingEl = document.getElementById('policiesLoading');
    const contentEl = document.getElementById('policiesContent');
    const errorEl = document.getElementById('policiesError');

    if (!hotelId || hotelId.startsWith('google_') || hotelId.startsWith('demo_') || hotelId.startsWith('test_')) {
        // Hide policies section for non-RateHawk hotels
        loadingEl?.classList.add('hidden');
        errorEl?.classList.remove('hidden');
        return;
    }

    try {
        const result = await HotelAPI.getHotelPolicies(hotelId);

        if (result.success && result.data) {
            loadingEl?.classList.add('hidden');
            contentEl?.classList.remove('hidden');
            displayHotelPolicies(result.data.formatted_policies);
        } else {
            loadingEl?.classList.add('hidden');
            errorEl?.classList.remove('hidden');
        }
    } catch (error) {
        console.log('Could not fetch hotel policies:', error);
        loadingEl?.classList.add('hidden');
        errorEl?.classList.remove('hidden');
    }
}

/**
 * Display formatted hotel policies
 */
function displayHotelPolicies(policies) {
    const sections = {
        'check_in_out': 'policyCheckInOut',
        'children': 'policyChildren',
        'pets': 'policyPets',
        'internet': 'policyInternet',
        'parking': 'policyParking',
        'payments': 'policyPayments',
        'extra_beds': 'policyExtraBeds',
        'meals': 'policyMeals',
        'other': 'policyOther'
    };

    let hasAnyPolicies = false;

    for (const [key, elementId] of Object.entries(sections)) {
        const sectionEl = document.getElementById(elementId);
        const itemsEl = sectionEl?.querySelector('.policy-items');
        const policyItems = policies[key] || [];

        if (policyItems.length > 0) {
            hasAnyPolicies = true;
            sectionEl?.classList.remove('hidden');

            itemsEl.innerHTML = policyItems.map(item => `
                <div class="policy-item">
                    <i class="fas ${item.icon}"></i>
                    <div class="policy-item-content">
                        <span class="policy-label">${item.label}:</span>
                        <span class="policy-value">${item.value}</span>
                    </div>
                </div>
            `).join('');
        } else {
            sectionEl?.classList.add('hidden');
        }
    }

    if (!hasAnyPolicies) {
        document.getElementById('policiesContent')?.classList.add('hidden');
        document.getElementById('policiesError')?.classList.remove('hidden');
    }
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
 * Includes room images and amenities from ETG static data if available
 * Matching: rate's rg_ext.rg <-> room_groups[].rg_hash
 * 
 * Tax handling:
 * - Non-included taxes (included_by_supplier: false) are displayed separately
 * - These taxes must be paid directly at check-in
 * - Each tax is shown in its original currency (currency_code)
 */
function createRateCard(rate, index) {
    const card = document.createElement('div');
    card.className = 'rate-card';
    card.dataset.rateIndex = index;

    const price = HotelUtils.formatPrice(rate.price);
    const originalPrice = rate.original_price ? HotelUtils.formatPrice(rate.original_price) : null;

    // Meal Plan Logic (ETG 'meal_data')
    const mealInfo = rate.meal_info || {};
    let mealPlanHtml = '';

    if (mealInfo.display_name) {
        mealPlanHtml = `<p class="rate-meal-plan"><i class="fas fa-utensils"></i> ${mealInfo.display_name}</p>`;

        // Check if child meal is NOT included when children are present
        // Check searchParams first, then fallback to current url params if needed
        const hasChildren = searchParams && (
            (searchParams.children_ages && searchParams.children_ages.length > 0) ||
            (Array.isArray(searchParams.rooms) && searchParams.rooms.some(r => r.children > 0))
        );

        if (hasChildren && mealInfo.no_child_meal) {
            mealPlanHtml += `
                <div class="child-meal-warning">
                    <i class="fas fa-exclamation-circle"></i>
                    <span>Meals NOT included for children</span>
                </div>
            `;
        }
    } else {
        // Fallback for old data
        const mealText = HotelUtils.getMealPlanText(rate.meal_plan || rate.meal);
        mealPlanHtml = `<p class="rate-meal-plan"><i class="fas fa-utensils"></i> ${mealText}</p>`;
    }

    const nights = searchParams ? HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout) : 1;
    const totalPrice = HotelUtils.formatPrice(rate.price * nights);

    const featuresHtml = (rate.features || []).map(f =>
        `<span class="rate-feature"><i class="fas fa-check"></i> ${f}</span>`
    ).join('');

    // Build cancellation badge with deadline from ETG API
    // free_cancellation_before contains the UTC+0 timestamp for free cancellation deadline
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

        // Build detailed cancellation policy timeline
        const policies = cancellationInfo.policies || [];
        let policyTimelineHtml = '';

        if (policies.length > 0) {
            const policyItems = policies.map(policy => {
                let icon, label, dateRange, penaltyText, tierClass;

                if (policy.type === 'free') {
                    icon = 'fa-check-circle';
                    label = 'Free cancellation';
                    tierClass = 'tier-free';
                    dateRange = policy.end_formatted ? `Until ${policy.end_formatted}` : 'Before deadline';
                    penaltyText = 'No penalty';
                } else if (policy.type === 'partial_penalty') {
                    icon = 'fa-exclamation-circle';
                    label = 'Partial penalty';
                    tierClass = 'tier-partial';
                    dateRange = policy.start_formatted ? `From ${policy.start_formatted}` : '';
                    const amount = parseFloat(policy.penalty_amount || 0).toFixed(2);
                    penaltyText = `Penalty: $${amount}`;
                } else if (policy.type === 'full_penalty') {
                    icon = 'fa-times-circle';
                    label = 'Full penalty (No refund)';
                    tierClass = 'tier-full';
                    dateRange = policy.start_formatted ? `From ${policy.start_formatted}` : 'After deadline';
                    const amount = parseFloat(policy.penalty_amount || 0).toFixed(2);
                    penaltyText = `Penalty: $${amount}`;
                } else {
                    return '';
                }

                return `
                    <div class="policy-tier ${tierClass}">
                        <div class="tier-icon"><i class="fas ${icon}"></i></div>
                        <div class="tier-content">
                            <span class="tier-label">${label}</span>
                            <span class="tier-date">${dateRange}</span>
                            ${policy.type !== 'free' ? `<span class="tier-penalty">${penaltyText}</span>` : ''}
                        </div>
                    </div>
                `;
            }).join('');

            policyTimelineHtml = `
                <div class="cancellation-policy-details">
                    <button class="policy-toggle" onclick="this.parentElement.classList.toggle('expanded')">
                        <i class="fas fa-chevron-down"></i> View cancellation policy details
                    </button>
                    <div class="policy-timeline">
                        <div class="timeline-header">
                            <i class="fas fa-calendar-alt"></i> Cancellation Policy Timeline (UTC)
                        </div>
                        ${policyItems}
                    </div>
                </div>
            `;
        }

        cancellationDetailsHtml = `
            <div class="cancellation-deadline">
                <i class="fas fa-clock"></i>
                <span>Cancel free until <strong>${deadline.datetime}</strong></span>
            </div>
            ${policyTimelineHtml}
        `;
    } else if (rate.cancellation === 'free') {
        // Fallback for old data without cancellation_info
        cancellationBadge = '<span class="cancellation-badge free"><i class="fas fa-check-circle"></i> Free Cancellation</span>';
    } else {
        cancellationBadge = '<span class="cancellation-badge non-refund"><i class="fas fa-ban"></i> Non-refundable</span>';
        // Show non-refundable policy info
        cancellationDetailsHtml = `
            <div class="non-refundable-notice">
                <i class="fas fa-exclamation-triangle"></i>
                <span>This rate is non-refundable. Full charges apply if cancelled.</span>
            </div>
        `;
    }

    // Get room static data (images and amenities from ETG static data)
    const roomStatic = rate.room_static || {};
    const roomImages = roomStatic.images || [];
    const roomAmenities = roomStatic.amenities || [];
    const isMatched = roomStatic.matched || false;

    // Build room image gallery HTML
    let roomImageHtml = '';
    if (roomImages.length > 0) {
        const mainImage = roomImages[0];
        const thumbnails = roomImages.slice(1, 4);
        roomImageHtml = `
            <div class="room-image-gallery">
                <div class="room-main-image" style="background-image: url('${mainImage}');">
                    ${thumbnails.length > 0 ? `<span class="image-count"><i class="fas fa-images"></i> ${roomImages.length}</span>` : ''}
                </div>
                ${thumbnails.length > 0 ? `
                    <div class="room-thumbnails">
                        ${thumbnails.map(img => `<div class="room-thumb" style="background-image: url('${img}');"></div>`).join('')}
                    </div>
                ` : ''}
            </div>
        `;
    }

    // Build room amenities HTML from static data
    let roomAmenitiesHtml = '';
    if (roomAmenities.length > 0) {
        const amenityIcons = {
            'wi-fi': 'fa-wifi',
            'wifi': 'fa-wifi',
            'air-conditioning': 'fa-snowflake',
            'air_conditioning': 'fa-snowflake',
            'tv': 'fa-tv',
            'television': 'fa-tv',
            'minibar': 'fa-wine-bottle',
            'safe': 'fa-lock',
            'hairdryer': 'fa-wind',
            'bathtub': 'fa-bath',
            'shower': 'fa-shower',
            'balcony': 'fa-door-open',
            'sea-view': 'fa-water',
            'city-view': 'fa-city',
            'kitchen': 'fa-utensils',
            'coffee-maker': 'fa-coffee',
            'iron': 'fa-tshirt',
            'desk': 'fa-desk'
        };

        const displayAmenities = roomAmenities.slice(0, 6).map(amenity => {
            const code = typeof amenity === 'string' ? amenity : (amenity.code || '');
            const label = typeof amenity === 'string'
                ? amenity.replace(/-/g, ' ').replace(/_/g, ' ')
                : (amenity.label || amenity.name || code);
            const icon = amenityIcons[code.toLowerCase()] || 'fa-check';
            return `<span class="room-amenity"><i class="fas ${icon}"></i> ${label}</span>`;
        }).join('');

        roomAmenitiesHtml = `
            <div class="room-amenities-list">
                ${displayAmenities}
                ${roomAmenities.length > 6 ? `<span class="more-amenities">+${roomAmenities.length - 6} more</span>` : ''}
            </div>
        `;
    }

    // Build non-included taxes HTML
    // These are taxes that must be paid directly at check-in (included_by_supplier: false)
    let taxesHtml = '';
    const taxInfo = rate.tax_info || {};
    const nonIncludedTaxes = taxInfo.non_included_taxes || [];

    if (nonIncludedTaxes.length > 0) {
        const taxItems = nonIncludedTaxes.map(tax => {
            const amount = parseFloat(tax.amount || 0).toFixed(2);
            const currency = tax.currency_code || 'USD';
            const displayName = tax.display_name || tax.name || 'Tax';
            return `
                <div class="tax-item">
                    <span class="tax-name">${displayName}</span>
                    <span class="tax-amount">${currency} ${amount}</span>
                </div>
            `;
        }).join('');

        taxesHtml = `
            <div class="non-included-taxes-section">
                <div class="taxes-header">
                    <i class="fas fa-info-circle"></i>
                    <span>Additional Taxes & Fees (payable at check-in)</span>
                </div>
                <div class="taxes-list">
                    ${taxItems}
                </div>
                <p class="taxes-note">
                    <i class="fas fa-exclamation-triangle"></i>
                    These charges are not included in the booking price and must be paid directly at the hotel upon check-in.
                </p>
            </div>
        `;
    }

    card.innerHTML = `
        ${roomImageHtml}
        <div class="rate-card-content">
            <div class="rate-card-header">
                <div class="rate-info">
                    <h3 class="rate-room-name">${rate.room_name || roomStatic.room_name || 'Room'}</h3>
                    ${mealPlanHtml}
                    ${cancellationBadge}
                    ${cancellationDetailsHtml}
                    ${isMatched ? '<span class="static-data-badge"><i class="fas fa-image"></i> Room photos available</span>' : ''}
                </div>
                <div class="rate-price">
                    ${originalPrice ? `<span class="original-price">${originalPrice}</span>` : ''}
                    <span class="rate-per-night">${price} <small>/night</small></span>
                    <span class="rate-total">${totalPrice} <small>total</small></span>
                </div>
            </div>
            ${roomAmenitiesHtml}
            ${taxesHtml}
            <p class="rate-description">${rate.room_description || ''}</p>
            <div class="rate-features">${featuresHtml}</div>
            <button class="book-rate-btn" data-rate-index="${index}" style="background: linear-gradient(135deg, #22c55e, #16a34a); color: white; border: none; padding: 12px 28px; border-radius: 8px; font-weight: 600; cursor: pointer; transition: all 0.3s;">
                Book Now
            </button>
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

    // Redirect to checkout page (contact info + payment)
    setTimeout(() => {
        window.location.href = 'guest-details.html';
    }, 800);
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
async function proceedToBooking() {
    if (!selectedRate) {
        showNotification('Please select a room first', 'warning');
        return;
    }

    // Auth check
    if (typeof AuthGuard !== 'undefined') {
        const isAuth = await AuthGuard.isAuthenticated();
        if (!isAuth) {
            AuthGuard.showLoginModal();
            showNotification('Please login to proceed with booking', 'warning');
            return;
        }
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
