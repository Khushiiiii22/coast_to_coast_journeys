/**
 * C2C Journeys - Flight Results Controller
 * Handles display and filtering of flight offers from Duffel API
 */

document.addEventListener('DOMContentLoaded', function () {
    // Current search state
    let allOutboundFlights = [];
    let filteredFlights = [];

    // UI Elements
    const flightsList = document.getElementById('flightsList');
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const flightCount = document.getElementById('flightCount');
    const airlineFilters = document.getElementById('airlineFilters');
    const maxPriceLabel = document.getElementById('maxPriceLabel');
    const priceRange = document.getElementById('priceRange');

    // 1. Get search parameters from URL
    const urlParams = new URLSearchParams(window.location.search);
    const origin = urlParams.get('from');
    const destination = urlParams.get('to');
    const departDate = urlParams.get('date');
    const adults = urlParams.get('adults') || 1;
    const fClass = urlParams.get('class') || 'economy';

    // Update UI displays
    document.getElementById('flightOriginDisplay').textContent = origin || 'Unknown';
    document.getElementById('flightDestDisplay').textContent = destination || 'Unknown';
    document.getElementById('flightDateDisplay').textContent = departDate || 'Not set';

    /**
     * Fetch flights from backend
     */
    async function fetchFlights() {
        if (!origin || !destination || !departDate) {
            loadingState.classList.add('hidden');
            showError("Missing search parameters. Please go back and try again.");
            return;
        }

        try {
            loadingState.classList.remove('hidden');
            errorState.classList.add('hidden');
            flightsList.classList.add('hidden');
            const response = await fetch('/api/flights/search', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    from: origin,
                    to: destination,
                    departDate: departDate,
                    adults: adults,
                    class: fClass
                })
            });

            const result = await response.json();

            if (result.success && result.data) {
                flightsList.classList.remove('hidden');
                allOutboundFlights = result.data.outbound || [];

                // Update Badge if needed
                const providerBadge = document.getElementById('providerBadge');
                if (result.data.meta && result.data.meta.provider === 'duffel') {
                    providerBadge.innerHTML = '<i class="fas fa-bolt"></i> Live Duffel Prices';
                    providerBadge.style.background = '#2563eb';
                } else {
                    providerBadge.innerHTML = '<i class="fas fa-info-circle"></i> Demo Data';
                    providerBadge.style.background = '#64748b';
                }

                updateFilters();
                renderFlights();
            } else {
                showError(result.error || "No flights found for this route.");
            }
        } catch (err) {
            console.error("Flight search error:", err);
            showError("Server error. Please check your connection and try again.");
        } finally {
            loadingState.classList.add('hidden');
        }
    }

    /**
     * Update filter UI based on available airlines
     */
    function updateFilters() {
        const airlines = [...new Set(allOutboundFlights.map(f => JSON.stringify(f.airline)))].map(s => JSON.parse(s));

        airlineFilters.innerHTML = airlines.map(airline => `
            <label class="filter-checkbox">
                <input type="checkbox" value="${airline.code}" checked class="airline-filter">
                <span class="checkmark"></span>
                <span class="filter-label">${airline.name}</span>
            </label>
        `).join('');

        // Attach listeners to new checkboxes
        document.querySelectorAll('.airline-filter').forEach(cb => {
            cb.addEventListener('change', renderFlights);
        });

        // Set max price for slider
        if (allOutboundFlights.length > 0) {
            const maxPrice = Math.max(...allOutboundFlights.map(f => f.price));
            priceRange.max = Math.ceil(maxPrice);
            priceRange.value = Math.ceil(maxPrice);
            maxPriceLabel.textContent = `$${Math.ceil(maxPrice)}`;
        }
    }

    /**
     * Render flight cards
     */
    function renderFlights() {
        const selectedAirlines = [...document.querySelectorAll('.airline-filter:checked')].map(cb => cb.value);
        const maxPrice = parseFloat(priceRange.value);
        const selectedStops = [...document.querySelectorAll('input[type="checkbox"][value="0"], input[type="checkbox"][value="1"], input[type="checkbox"][value="2"]')].filter(cb => cb.checked).map(cb => parseInt(cb.value));

        filteredFlights = allOutboundFlights.filter(f => {
            const airlineMatch = selectedAirlines.length === 0 || selectedAirlines.includes(f.airline.code);
            const priceMatch = f.price <= maxPrice;
            const stopsMatch = selectedStops.includes(f.stops >= 2 ? 2 : f.stops);
            return airlineMatch && priceMatch && stopsMatch;
        });

        // Sort
        const sortBy = document.getElementById('sortSelect').value;
        if (sortBy === 'price_low') filteredFlights.sort((a, b) => a.price - b.price);
        else if (sortBy === 'duration_low') filteredFlights.sort((a, b) => {
            const getMins = (s) => {
                const h = parseInt(s.match(/(\d+)h/) ? s.match(/(\d+)h/)[1] : 0);
                const m = parseInt(s.match(/(\d+)m/) ? s.match(/(\d+)m/)[1] : 0);
                return h * 60 + m;
            };
            return getMins(a.duration) - getMins(b.duration);
        });

        flightCount.textContent = filteredFlights.length;

        if (filteredFlights.length === 0) {
            flightsList.innerHTML = `
                <div class="no-results" style="text-align: center; padding: 40px; background: #f8fafc; border-radius: 12px;">
                    <i class="fas fa-search" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 15px;"></i>
                    <p style="font-weight: 600;">No flights match your filters</p>
                    <button class="btn btn-outline" id="resetFilters" style="margin-top: 10px;">Reset All Filters</button>
                </div>
            `;
            document.getElementById('resetFilters')?.addEventListener('click', () => {
                document.querySelectorAll('.filters-sidebar input').forEach(input => input.checked = true);
                renderFlights();
            });
            return;
        }

        flightsList.innerHTML = filteredFlights.map(flight => `
            <div class="flight-card">
                <div class="flight-main-info">
                    <div class="airline-info">
                        <img src="${flight.airline.logo}" alt="${flight.airline.name}" class="airline-logo">
                        <span class="airline-name">${flight.airline.name}</span>
                    </div>
                    
                    <div class="flight-timing">
                        <div class="time-block">
                            <span class="time">${flight.depart_time}</span>
                            <span class="airport-code">${flight.origin}</span>
                        </div>
                        
                        <div class="flight-path">
                            <span class="duration">${flight.duration}</span>
                            <div class="path-line"></div>
                            <span class="stops-info ${flight.stops === 0 ? 'direct' : ''}">
                                ${flight.stops === 0 ? 'Direct' : flight.stops + (flight.stops === 1 ? ' stop' : ' stops')}
                            </span>
                        </div>
                        
                        <div class="time-block">
                            <span class="time">${flight.arrival_time}</span>
                            <span class="airport-code">${flight.destination}</span>
                            ${flight.next_day ? '<small style="color: #ef4444; font-size: 0.7rem;">+1 day</small>' : ''}
                        </div>
                    </div>
                    
                    <div class="flight-price-action">
                        <span class="price-label">Per traveler</span>
                        <span class="price">${flight.currency === 'USD' ? '$' : flight.currency}${flight.price}</span>
                        <button class="btn-select-flight">Select Flight</button>
                    </div>
                </div>
                
                <div class="flight-meta">
                    <div class="meta-item">
                        <i class="fas fa-suitcase-rolling"></i>
                        <span>Carry-on included</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-couch"></i>
                        <span>${flight.class.charAt(0).toUpperCase() + flight.class.slice(1)}</span>
                    </div>
                    <div class="meta-item">
                        <i class="fas fa-bolt"></i>
                        <span>Instant Confirmation</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    function showError(msg) {
        errorState.classList.remove('hidden');
        document.getElementById('errorMessage').textContent = msg;
        flightsList.classList.add('hidden');
    }

    // Event Listeners
    priceRange.addEventListener('input', (e) => {
        maxPriceLabel.textContent = `$${e.target.value}`;
        renderFlights();
    });

    document.getElementById('sortSelect').addEventListener('change', renderFlights);

    document.querySelectorAll('input[type="checkbox"]').forEach(cb => {
        cb.addEventListener('change', renderFlights);
    });

    document.getElementById('clearFilters').addEventListener('click', () => {
        document.querySelectorAll('.filters-sidebar input[type="checkbox"]').forEach(cb => cb.checked = true);
        priceRange.value = priceRange.max;
        maxPriceLabel.textContent = `$${priceRange.max}`;
        renderFlights();
    });

    // Mobile menu
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }

    // Initial fetch
    fetchFlights();
});
