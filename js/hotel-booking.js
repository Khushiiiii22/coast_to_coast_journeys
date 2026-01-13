/**
 * Coast to Coast Journeys - Hotel Booking Page
 * Handles guest details and booking submission
 */

document.addEventListener('DOMContentLoaded', function () {
    initBookingPage();
});

// Global state
let bookingData = null;
let hotel = null;
let rate = null;
let searchParams = null;

/**
 * Initialize booking page
 */
function initBookingPage() {
    bookingData = SearchSession.getBookingData();

    if (!bookingData) {
        showNotification('Booking data not found. Please select a room first.', 'error');
        setTimeout(() => window.location.href = 'hotel-results.html', 2000);
        return;
    }

    hotel = bookingData.hotel;
    rate = bookingData.rate;
    searchParams = bookingData.search_params;

    // Populate summary
    populateBookingSummary();

    // Add additional guest forms if needed
    addAdditionalGuestForms();

    // Setup form submission
    document.getElementById('bookingForm').addEventListener('submit', handleBookingSubmit);
}

/**
 * Populate booking summary sidebar
 */
function populateBookingSummary() {
    // Hotel info
    const hotelImage = hotel.images?.[0] || hotel.image || 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=200';
    document.getElementById('summaryHotelImage').style.backgroundImage = `url('${hotelImage}')`;
    document.getElementById('summaryHotelStars').innerHTML = HotelUtils.generateStars(hotel.star_rating || 4);
    document.getElementById('summaryHotelName').textContent = hotel.name;
    document.getElementById('summaryHotelAddress').innerHTML = `<i class="fas fa-map-marker-alt"></i> ${hotel.address || 'Location available'}`;

    // Room info
    document.getElementById('summaryRoomName').textContent = rate.room_name;
    document.getElementById('summaryMealPlan').innerHTML = `<i class="fas fa-utensils"></i> ${HotelUtils.getMealPlanText(rate.meal_plan)}`;

    // Dates
    if (searchParams) {
        document.getElementById('summaryCheckin').textContent = HotelUtils.formatDate(searchParams.checkin);
        document.getElementById('summaryCheckout').textContent = HotelUtils.formatDate(searchParams.checkout);
    }

    // Calculate pricing
    const nights = rate.nights || HotelUtils.calculateNights(searchParams.checkin, searchParams.checkout);
    const rooms = searchParams?.rooms || 1;
    const pricePerNight = rate.price;
    const subtotal = pricePerNight * nights * rooms;
    const taxes = Math.round(subtotal * 0.18); // 18% GST
    const total = subtotal + taxes;

    document.getElementById('pricePerNightLabel').textContent = `${rooms} Room × ${nights} Night${nights > 1 ? 's' : ''}`;
    document.getElementById('pricePerNightValue').textContent = HotelUtils.formatPrice(subtotal);
    document.getElementById('taxesValue').textContent = HotelUtils.formatPrice(taxes);
    document.getElementById('totalAmountValue').textContent = HotelUtils.formatPrice(total);
    document.getElementById('btnTotalPrice').textContent = total.toLocaleString('en-IN');

    // Cancellation policy
    if (rate.cancellation === 'free') {
        document.getElementById('cancellationText').innerHTML = `<span style="color: #22c55e;"><i class="fas fa-check-circle"></i> Free cancellation until 2 days before check-in</span>`;
    } else {
        document.getElementById('cancellationText').innerHTML = `<span style="color: #f59e0b;"><i class="fas fa-exclamation-circle"></i> This booking is non-refundable</span>`;
    }

    // Store total for booking
    bookingData.total_amount = total;
    bookingData.subtotal = subtotal;
    bookingData.taxes = taxes;
}

/**
 * Add additional guest forms for multiple guests
 */
function addAdditionalGuestForms() {
    const adults = searchParams?.adults || 2;
    const container = document.getElementById('additionalGuestsContainer');

    if (adults > 1) {
        for (let i = 2; i <= adults; i++) {
            const guestForm = document.createElement('div');
            guestForm.className = 'guest-form additional-guest';
            guestForm.innerHTML = `
                <h4>Guest ${i}</h4>
                <div class="form-row">
                    <div class="form-group">
                        <label for="firstName${i}">First Name *</label>
                        <input type="text" id="firstName${i}" name="firstName${i}" required 
                            placeholder="As per ID proof">
                    </div>
                    <div class="form-group">
                        <label for="lastName${i}">Last Name *</label>
                        <input type="text" id="lastName${i}" name="lastName${i}" required
                            placeholder="As per ID proof">
                    </div>
                </div>
            `;
            container.appendChild(guestForm);
        }
    }
}

/**
 * Handle booking form submission
 */
async function handleBookingSubmit(e) {
    e.preventDefault();

    // Validate terms accepted
    if (!document.getElementById('termsAccepted').checked) {
        showNotification('Please accept the terms and conditions', 'warning');
        return;
    }

    // Collect guest data
    const guests = [];
    const adults = searchParams?.adults || 2;

    for (let i = 1; i <= adults; i++) {
        const firstName = document.getElementById(`firstName${i}`)?.value;
        const lastName = document.getElementById(`lastName${i}`)?.value;

        if (firstName && lastName) {
            guests.push({
                first_name: firstName,
                last_name: lastName
            });
        }
    }

    if (guests.length === 0) {
        showNotification('Please enter guest details', 'warning');
        return;
    }

    const email = document.getElementById('email').value;
    const phone = document.getElementById('phone').value;
    const specialRequests = document.getElementById('specialRequests')?.value || '';

    // Show loading
    showLoadingOverlay('Processing your booking...');

    try {
        // Check API health
        let apiAvailable = false;
        try {
            await HotelAPI.healthCheck();
            apiAvailable = true;
        } catch (e) {
            console.log('API not available, using demo flow');
        }

        let bookingResult;

        if (apiAvailable && !rate.book_hash?.startsWith('demo_')) {
            // Real API booking
            bookingResult = await processRealBooking(guests, email, phone, specialRequests);
        } else {
            // Demo booking
            bookingResult = await processDemoBooking(guests, email, phone, specialRequests);
        }

        if (bookingResult.success) {
            // Save confirmation data
            SearchSession.saveBookingData({
                ...bookingData,
                confirmation: bookingResult,
                guests: guests,
                email: email,
                phone: phone
            });

            // Redirect to confirmation page
            window.location.href = 'booking-confirmation.html';
        } else {
            hideLoadingOverlay();
            showNotification(bookingResult.error || 'Booking failed. Please try again.', 'error');
        }

    } catch (error) {
        console.error('Booking error:', error);
        hideLoadingOverlay();
        showNotification('An error occurred. Please try again.', 'error');
    }
}

/**
 * Process real booking via API
 */
async function processRealBooking(guests, email, phone, specialRequests) {
    try {
        // Step 1: Prebook to check availability
        updateLoadingMessage('Checking availability...');
        const prebookResult = await HotelAPI.prebookRate(rate.book_hash);

        if (!prebookResult.success) {
            return { success: false, error: 'Room is no longer available at this price' };
        }

        // Step 2: Create booking
        updateLoadingMessage('Creating your reservation...');
        const bookingParams = {
            book_hash: rate.book_hash,
            guests: guests,
            hotel_id: hotel.id,
            hotel_name: hotel.name,
            checkin: searchParams.checkin,
            checkout: searchParams.checkout,
            total_amount: bookingData.total_amount,
            currency: 'INR'
        };

        const createResult = await HotelAPI.createBooking(bookingParams);

        if (!createResult.success) {
            return { success: false, error: createResult.error || 'Failed to create booking' };
        }

        // Step 3: Finish booking
        updateLoadingMessage('Finalizing your booking...');
        const finishResult = await HotelAPI.finishBooking(createResult.partner_order_id);

        // Step 4: Poll for confirmation
        updateLoadingMessage('Confirming with hotel...');
        const statusResult = await HotelAPI.pollBookingStatus(createResult.partner_order_id);

        if (statusResult.success && statusResult.status === 'confirmed') {
            return {
                success: true,
                partner_order_id: createResult.partner_order_id,
                confirmation_number: statusResult.data?.confirmation_number || createResult.partner_order_id,
                status: 'confirmed'
            };
        } else {
            return {
                success: false,
                error: statusResult.error || 'Booking confirmation failed'
            };
        }

    } catch (error) {
        console.error('Real booking error:', error);
        return { success: false, error: error.message };
    }
}

/**
 * Process demo booking
 */
async function processDemoBooking(guests, email, phone, specialRequests) {
    // Simulate API delay
    await sleep(1500);
    updateLoadingMessage('Checking availability...');
    await sleep(1000);
    updateLoadingMessage('Creating reservation...');
    await sleep(1000);
    updateLoadingMessage('Confirming with hotel...');
    await sleep(1000);

    const confirmationNumber = 'CTC-' + Date.now().toString().slice(-8).toUpperCase();

    return {
        success: true,
        partner_order_id: confirmationNumber,
        confirmation_number: confirmationNumber,
        status: 'confirmed',
        demo: true
    };
}

/**
 * Sleep helper
 */
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * Show loading overlay
 */
function showLoadingOverlay(message) {
    document.getElementById('loadingMessage').textContent = message;
    document.getElementById('loadingOverlay').classList.remove('hidden');
    document.getElementById('confirmBookingBtn').disabled = true;
}

/**
 * Hide loading overlay
 */
function hideLoadingOverlay() {
    document.getElementById('loadingOverlay').classList.add('hidden');
    document.getElementById('confirmBookingBtn').disabled = false;
}

/**
 * Update loading message
 */
function updateLoadingMessage(message) {
    document.getElementById('loadingMessage').textContent = message;
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
