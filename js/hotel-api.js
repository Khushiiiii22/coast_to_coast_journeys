/**
 * C2C Journeys - Hotel API Service
 * Connects frontend to Flask backend for hotel search and booking
 */

// API Configuration
const API_CONFIG = {
    BASE_URL: '/api',  // Relative URL for deployment flexibility
    TIMEOUT: 30000
};

/**
 * Hotel API Service
 */
const HotelAPI = {
    /**
     * Make API request with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${API_CONFIG.BASE_URL}${endpoint}`;

        const defaultOptions = {
            headers: {
                'Content-Type': 'application/json'
            },
            ...options
        };

        try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), API_CONFIG.TIMEOUT);

            const response = await fetch(url, {
                ...defaultOptions,
                signal: controller.signal
            });

            clearTimeout(timeoutId);

            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'Request failed');
            }

            return data;
        } catch (error) {
            if (error.name === 'AbortError') {
                throw new Error('Request timed out');
            }
            throw error;
        }
    },

    /**
     * Health check
     */
    async healthCheck() {
        return this.request('/health');
    },

    // ==========================================
    // SEARCH METHODS
    // ==========================================

    /**
     * Search hotels by destination name
     * @param {Object} params - Search parameters
     * @param {string} params.destination - Destination name (e.g., "Goa, India")
     * @param {string} params.checkin - Check-in date (YYYY-MM-DD)
     * @param {string} params.checkout - Check-out date (YYYY-MM-DD)
     * @param {number} params.adults - Number of adults
     * @param {Array} params.children_ages - Ages of children (optional)
     * @param {number} params.radius - Search radius in meters (optional)
     * @param {string} params.residency - Guest citizenship/residency code (e.g., "in", "gb")
     */
    async searchByDestination(params) {
        return this.request('/hotels/search/destination', {
            method: 'POST',
            body: JSON.stringify({
                destination: params.destination,
                checkin: params.checkin,
                checkout: params.checkout,
                adults: params.adults || 2,
                children_ages: params.children_ages || [],
                radius: params.radius || 10000,
                currency: params.currency || 'USD',
                residency: params.residency || 'in'  // ETG/RateHawk residency parameter
            })
        });
    },

    /**
     * Search hotels by region ID
     */
    async searchByRegion(params) {
        return this.request('/hotels/search/region', {
            method: 'POST',
            body: JSON.stringify({
                region_id: params.region_id,
                checkin: params.checkin,
                checkout: params.checkout,
                adults: params.adults || 2,
                children_ages: params.children_ages || [],
                currency: params.currency || 'USD'
            })
        });
    },

    /**
     * Search hotels by coordinates
     */
    async searchByGeo(params) {
        return this.request('/hotels/search/geo', {
            method: 'POST',
            body: JSON.stringify({
                latitude: params.latitude,
                longitude: params.longitude,
                radius: params.radius || 5000,
                checkin: params.checkin,
                checkout: params.checkout,
                adults: params.adults || 2,
                children_ages: params.children_ages || [],
                currency: params.currency || 'USD'
            })
        });
    },

    // ==========================================
    // HOTEL DETAILS
    // ==========================================

    /**
     * Get hotel page with all room rates
     */
    async getHotelDetails(params) {
        return this.request('/hotels/details', {
            method: 'POST',
            body: JSON.stringify({
                hotel_id: params.hotel_id,
                checkin: params.checkin,
                checkout: params.checkout,
                adults: params.adults || 2,
                children_ages: params.children_ages || [],
                currency: params.currency || 'USD'
            })
        });
    },

    /**
     * Get static hotel info
     */
    async getHotelInfo(hotelId) {
        return this.request(`/hotels/info/${hotelId}`);
    },

    /**
     * Get hotel policies (metapolicy_struct and metapolicy_extra_info)
     * IMPORTANT: policy_struct is deprecated and ignored per RateHawk
     */
    async getHotelPolicies(hotelId) {
        return this.request(`/hotels/policies/${hotelId}`);
    },

    /**
     * Get room groups from hotel static data
     * Used for matching rates with room images and amenities
     * Matching: rate's rg_ext.rg <-> room_groups[].rg_hash
     */
    async getRoomGroups(hotelId) {
        return this.request(`/hotels/room-groups/${hotelId}`);
    },

    /**
     * Get photos for a Google Places hotel
     * Returns array of photo URLs for the hotel gallery
     * @param {string} placeId - Google Place ID (without 'google_' prefix)
     */
    async getGooglePlacePhotos(placeId) {
        return this.request(`/hotels/photos/google/${placeId}`);
    },

    /**
     * Get hotel details with rates enriched with room static data
     * Auto-matches rates with room groups using rg_ext.rg
     */
    async getEnrichedHotelDetails(params) {
        return this.request('/hotels/details-enriched', {
            method: 'POST',
            body: JSON.stringify({
                hotel_id: params.hotel_id,
                checkin: params.checkin,
                checkout: params.checkout,
                adults: params.adults || 2,
                children_ages: params.children_ages || [],
                currency: params.currency || 'USD'
            })
        });
    },

    // ==========================================
    // BOOKING
    // ==========================================

    /**
     * Prebook rate - check availability
     */
    async prebookRate(bookHash, priceIncreasePercent = 5) {
        return this.request('/hotels/prebook', {
            method: 'POST',
            body: JSON.stringify({
                book_hash: bookHash,
                price_increase_percent: priceIncreasePercent
            })
        });
    },

    /**
     * Create booking
     * @param {Object} params - Booking parameters
     * @param {string} params.book_hash - Hash from prebook
     * @param {Array} params.guests - Array of {first_name, last_name}
     * @param {string} params.hotel_id - Hotel ID
     * @param {string} params.hotel_name - Hotel name
     * @param {string} params.checkin - Check-in date
     * @param {string} params.checkout - Check-out date
     * @param {number} params.total_amount - Total amount
     */
    async createBooking(params) {
        return this.request('/hotels/book', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    },

    /**
     * Finish booking process
     */
    async finishBooking(partnerOrderId) {
        return this.request('/hotels/book/finish', {
            method: 'POST',
            body: JSON.stringify({
                partner_order_id: partnerOrderId
            })
        });
    },

    /**
     * Poll booking status until final
     */
    async pollBookingStatus(partnerOrderId) {
        return this.request('/hotels/book/poll', {
            method: 'POST',
            body: JSON.stringify({
                partner_order_id: partnerOrderId
            })
        });
    },

    /**
     * Get booking info
     */
    async getBookingInfo(partnerOrderId) {
        return this.request(`/hotels/booking/${partnerOrderId}`);
    },

    /**
     * Cancel booking
     */
    async cancelBooking(partnerOrderId) {
        return this.request('/hotels/booking/cancel', {
            method: 'POST',
            body: JSON.stringify({
                partner_order_id: partnerOrderId
            })
        });
    },

    /**
     * Get user bookings
     */
    async getUserBookings(userId) {
        return this.request(`/hotels/user/${userId}/bookings`);
    },

    // ==========================================
    // MAPS
    // ==========================================

    /**
     * Geocode address
     */
    async geocode(address) {
        return this.request('/maps/geocode', {
            method: 'POST',
            body: JSON.stringify({ address })
        });
    },

    /**
     * Search places
     */
    async searchPlaces(params) {
        return this.request('/maps/search', {
            method: 'POST',
            body: JSON.stringify(params)
        });
    },

    /**
     * Get static map URL
     */
    getStaticMapUrl(latitude, longitude, zoom = 15, size = '600x300') {
        return `${API_CONFIG.BASE_URL}/maps/static-map?latitude=${latitude}&longitude=${longitude}&zoom=${zoom}&size=${size}`;
    }
};

/**
 * Search Session Storage
 * Stores search parameters and results between pages
 */
const SearchSession = {
    KEYS: {
        SEARCH_PARAMS: 'ctc_hotel_search_params',
        SEARCH_RESULTS: 'ctc_hotel_search_results',
        SELECTED_HOTEL: 'ctc_selected_hotel',
        SELECTED_RATE: 'ctc_selected_rate',
        BOOKING_DATA: 'ctc_booking_data'
    },

    save(key, data) {
        sessionStorage.setItem(key, JSON.stringify(data));
    },

    get(key) {
        const data = sessionStorage.getItem(key);
        return data ? JSON.parse(data) : null;
    },

    remove(key) {
        sessionStorage.removeItem(key);
    },

    clear() {
        Object.values(this.KEYS).forEach(key => this.remove(key));
    },

    // Convenience methods
    saveSearchParams(params) {
        this.save(this.KEYS.SEARCH_PARAMS, params);
    },

    getSearchParams() {
        return this.get(this.KEYS.SEARCH_PARAMS);
    },

    saveSearchResults(results) {
        this.save(this.KEYS.SEARCH_RESULTS, results);
    },

    getSearchResults() {
        return this.get(this.KEYS.SEARCH_RESULTS);
    },

    saveSelectedHotel(hotel) {
        this.save(this.KEYS.SELECTED_HOTEL, hotel);
    },

    getSelectedHotel() {
        return this.get(this.KEYS.SELECTED_HOTEL);
    },

    saveSelectedRate(rate) {
        this.save(this.KEYS.SELECTED_RATE, rate);
    },

    getSelectedRate() {
        return this.get(this.KEYS.SELECTED_RATE);
    },

    saveBookingData(data) {
        this.save(this.KEYS.BOOKING_DATA, data);
    },

    getBookingData() {
        return this.get(this.KEYS.BOOKING_DATA);
    }
};

/**
 * Format utilities
 */
const HotelUtils = {
    // Currency conversion rates (base: INR)
    conversionRates: {
        'INR': 1,
        'USD': 0.012,
        'EUR': 0.011,
        'GBP': 0.0095,
        'AED': 0.044
    },

    /**
     * Get user's selected currency
     */
    getSelectedCurrency() {
        return localStorage.getItem('ctc_currency') || 'INR';
    },

    /**
     * Convert amount between currencies
     */
    convertCurrency(amount, fromCurrency, toCurrency) {
        if (fromCurrency === toCurrency) return amount;

        // First convert to INR (base), then to target
        const toINR = amount / (this.conversionRates[fromCurrency] || 1);
        const converted = toINR * (this.conversionRates[toCurrency] || 1);
        return Math.round(converted);
    },

    /**
     * Format price with currency - uses user's selected currency
     */
    formatPrice(amount, originalCurrency = 'INR') {
        const symbols = {
            'INR': '₹',
            'USD': '$',
            'EUR': '€',
            'GBP': '£',
            'AED': 'AED '
        };

        // Get user's selected currency
        const displayCurrency = this.getSelectedCurrency();

        // Convert if needed
        const convertedAmount = this.convertCurrency(amount, originalCurrency, displayCurrency);

        const symbol = symbols[displayCurrency] || displayCurrency + ' ';

        // Use appropriate locale for formatting
        const locale = displayCurrency === 'INR' ? 'en-IN' : 'en-US';
        return `${symbol}${convertedAmount.toLocaleString(locale)}`;
    },

    /**
     * Format date for display
     */
    formatDate(dateStr) {
        const date = new Date(dateStr);
        return date.toLocaleDateString('en-IN', {
            weekday: 'short',
            day: 'numeric',
            month: 'short',
            year: 'numeric'
        });
    },

    /**
     * Calculate number of nights
     */
    calculateNights(checkin, checkout) {
        const start = new Date(checkin);
        const end = new Date(checkout);
        const diffTime = Math.abs(end - start);
        return Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    },

    /**
     * Generate star rating HTML
     */
    generateStars(rating) {
        const fullStars = Math.floor(rating);
        const halfStar = rating % 1 >= 0.5;
        const emptyStars = 5 - fullStars - (halfStar ? 1 : 0);

        let html = '';
        for (let i = 0; i < fullStars; i++) {
            html += '<i class="fas fa-star"></i>';
        }
        if (halfStar) {
            html += '<i class="fas fa-star-half-alt"></i>';
        }
        for (let i = 0; i < emptyStars; i++) {
            html += '<i class="far fa-star"></i>';
        }
        return html;
    },

    /**
     * Get meal plan display text
     */
    getMealPlanText(mealPlan) {
        const plans = {
            'nomeal': 'Room Only',
            'breakfast': 'Breakfast Included',
            'halfboard': 'Half Board',
            'fullboard': 'Full Board',
            'allinclusive': 'All Inclusive'
        };
        return plans[mealPlan] || mealPlan || 'Room Only';
    },

    /**
     * Parse guests from form
     */
    parseGuests(rooms, adultsPerRoom, childrenPerRoom) {
        const guests = [];
        for (let i = 0; i < rooms; i++) {
            guests.push({
                adults: adultsPerRoom,
                children: childrenPerRoom || []
            });
        }
        return guests;
    }
};

// Export for use in other scripts
window.HotelAPI = HotelAPI;
window.SearchSession = SearchSession;
window.HotelUtils = HotelUtils;

console.log('Hotel API Service loaded successfully!');
