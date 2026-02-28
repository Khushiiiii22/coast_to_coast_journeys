/**
 * C2C Journeys - Flight Results Controller
 * Handles display, filtering, and sorting of flight search results
 */

document.addEventListener('DOMContentLoaded', function () {
    // State
    let allOutboundFlights = [];
    let filteredFlights = [];
    let activeTimeFilter = 'all';
    let activeSortBy = 'cheapest';

    // UI Elements
    const flightsList = document.getElementById('flightsList');
    const loadingState = document.getElementById('loadingState');
    const errorState = document.getElementById('errorState');
    const flightCount = document.getElementById('flightCount');
    const airlineFilters = document.getElementById('airlineFilters');
    const maxPriceLabel = document.getElementById('maxPriceLabel');
    const priceRange = document.getElementById('priceRange');

    // USD to INR conversion (approximate)
    const USD_TO_INR = 83;

    // Get search parameters from URL (handle both 'depart' and 'date' param names)
    const urlParams = new URLSearchParams(window.location.search);
    const origin = urlParams.get('from') || '';
    const destination = urlParams.get('to') || '';
    const departDate = urlParams.get('depart') || urlParams.get('date') || '';
    const returnDate = urlParams.get('return') || '';
    const adults = parseInt(urlParams.get('adults')) || 1;
    const children = parseInt(urlParams.get('children')) || 0;
    const infants = parseInt(urlParams.get('infants')) || 0;
    const fClass = urlParams.get('class') || 'economy';
    const tripType = urlParams.get('type') || 'oneway';

    // Format date for display
    function formatDateDisplay(dateStr) {
        if (!dateStr) return 'Not set';
        try {
            const d = new Date(dateStr);
            const options = { weekday: 'short', day: 'numeric', month: 'short', year: 'numeric' };
            return d.toLocaleDateString('en-IN', options);
        } catch {
            return dateStr;
        }
    }

    // Format price in INR
    function formatPrice(price, currency) {
        let inrPrice = price;
        if (currency === 'USD') {
            inrPrice = Math.round(price * USD_TO_INR);
        }
        return '₹' + inrPrice.toLocaleString('en-IN');
    }

    // Update search bar display
    document.getElementById('flightOriginDisplay').textContent = origin || 'Unknown';
    document.getElementById('flightDestDisplay').textContent = destination || 'Unknown';
    document.getElementById('flightDateDisplay').textContent = formatDateDisplay(departDate);

    const totalTravelers = adults + children;
    let travelersText = `${totalTravelers} Traveler${totalTravelers > 1 ? 's' : ''}`;
    if (infants > 0) travelersText += `, ${infants} Infant${infants > 1 ? 's' : ''}`;
    const classLabels = { economy: 'Economy', premium: 'Premium', business: 'Business', first: 'First' };
    travelersText += `, ${classLabels[fClass] || 'Economy'}`;
    document.getElementById('flightTravelersDisplay').textContent = travelersText;

    // ========== Modify Search Modal ==========
    const modifyModal = document.getElementById('modifySearchModal');
    const modifyBtn = document.getElementById('modifySearchBtn');
    const cancelModify = document.getElementById('cancelModify');

    modifyBtn.addEventListener('click', () => {
        document.getElementById('modifyFrom').value = origin;
        document.getElementById('modifyTo').value = destination;
        document.getElementById('modifyDate').value = departDate;
        document.getElementById('modifyAdults').value = adults;
        modifyModal.classList.add('active');
    });

    cancelModify.addEventListener('click', () => {
        modifyModal.classList.remove('active');
    });

    modifyModal.addEventListener('click', (e) => {
        if (e.target === modifyModal) modifyModal.classList.remove('active');
    });

    document.getElementById('modifySearchForm').addEventListener('submit', (e) => {
        e.preventDefault();
        const newFrom = document.getElementById('modifyFrom').value;
        const newTo = document.getElementById('modifyTo').value;
        const newDate = document.getElementById('modifyDate').value;
        const newAdults = document.getElementById('modifyAdults').value;

        const params = new URLSearchParams({
            from: newFrom,
            to: newTo,
            depart: newDate,
            type: tripType,
            adults: newAdults,
            children: children,
            infants: infants,
            class: fClass
        });
        window.location.href = `flight-results.html?${params.toString()}`;
    });

    // ========== Sort Tabs ==========
    document.querySelectorAll('.sort-tab').forEach(tab => {
        tab.addEventListener('click', function () {
            document.querySelectorAll('.sort-tab').forEach(t => t.classList.remove('active'));
            this.classList.add('active');
            activeSortBy = this.dataset.sort;
            renderFlights();
        });
    });

    // ========== Time Filters ==========
    document.querySelectorAll('.time-filter-btn').forEach(btn => {
        btn.addEventListener('click', function () {
            document.querySelectorAll('.time-filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            activeTimeFilter = this.dataset.time;
            renderFlights();
        });
    });

    // ========== Fetch Flights ==========
    async function fetchFlights() {
        if (!origin || !destination || !departDate) {
            loadingState.classList.add('hidden');
            showError("Missing search parameters. Please go back and search again.");
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
                    returnDate: returnDate || undefined,
                    adults: adults,
                    class: fClass
                })
            });

            const result = await response.json();

            if (result.success && result.data) {
                allOutboundFlights = result.data.outbound || [];

                if (allOutboundFlights.length === 0) {
                    loadingState.classList.add('hidden');
                    showNoResults();
                    return;
                }

                // Update provider badge
                const providerBadge = document.getElementById('providerBadge');
                if (result.data.meta && result.data.meta.provider === 'duffel') {
                    providerBadge.innerHTML = '<i class="fas fa-bolt"></i> Live Duffel Prices';
                    providerBadge.style.background = '#2563eb';
                } else {
                    providerBadge.innerHTML = '<i class="fas fa-info-circle"></i> Demo Prices';
                    providerBadge.style.background = '#64748b';
                }

                updateFilters();
                updateSortTabs();
                renderFlights();
                flightsList.classList.remove('hidden');
            } else {
                showError(result.error || "No flights found for this route.");
            }
        } catch (err) {
            console.error("Flight search error:", err);
            showError("Connection error. Please check your network and try again.");
        } finally {
            loadingState.classList.add('hidden');
        }
    }

    // ========== Update Filters ==========
    function updateFilters() {
        // Airline filters
        const airlines = [];
        const seen = new Set();
        allOutboundFlights.forEach(f => {
            if (!seen.has(f.airline.code)) {
                seen.add(f.airline.code);
                airlines.push(f.airline);
            }
        });

        airlineFilters.innerHTML = airlines.map(airline => `
            <label class="filter-checkbox">
                <input type="checkbox" value="${airline.code}" checked class="airline-filter">
                <span class="checkmark"></span>
                <span class="filter-label">${airline.name}</span>
            </label>
        `).join('');

        // Attach listeners
        document.querySelectorAll('.airline-filter').forEach(cb => {
            cb.addEventListener('change', renderFlights);
        });

        // Update stop counts
        const stopCounts = { 0: 0, 1: 0, 2: 0 };
        allOutboundFlights.forEach(f => {
            const key = f.stops >= 2 ? 2 : f.stops;
            stopCounts[key]++;
        });
        ['0', '1', '2'].forEach(s => {
            const el = document.getElementById('stopCount' + s);
            if (el) el.textContent = stopCounts[parseInt(s)] > 0 ? `(${stopCounts[parseInt(s)]})` : '';
        });

        // Set price range
        if (allOutboundFlights.length > 0) {
            const prices = allOutboundFlights.map(f => {
                return f.currency === 'USD' ? Math.round(f.price * USD_TO_INR) : f.price;
            });
            const maxPrice = Math.max(...prices);
            const roundedMax = Math.ceil(maxPrice / 1000) * 1000;
            priceRange.max = roundedMax;
            priceRange.value = roundedMax;
            maxPriceLabel.textContent = `₹${roundedMax.toLocaleString('en-IN')}`;
        }
    }

    // ========== Update Sort Tabs ==========
    function updateSortTabs() {
        if (allOutboundFlights.length === 0) return;

        // Cheapest
        const cheapest = [...allOutboundFlights].sort((a, b) => a.price - b.price)[0];
        document.getElementById('cheapestPrice').textContent = formatPrice(cheapest.price, cheapest.currency);

        // Fastest
        const fastest = [...allOutboundFlights].sort((a, b) => getDurationMins(a.duration) - getDurationMins(b.duration))[0];
        document.getElementById('fastestDuration').textContent = fastest.duration;

        // Earliest
        const earliest = [...allOutboundFlights].sort((a, b) => a.depart_time.localeCompare(b.depart_time))[0];
        document.getElementById('earliestTime').textContent = earliest.depart_time;
    }

    // ========== Helper: Parse duration ==========
    function getDurationMins(durationStr) {
        const h = parseInt(durationStr.match(/(\d+)h/) ? durationStr.match(/(\d+)h/)[1] : 0);
        const m = parseInt(durationStr.match(/(\d+)m/) ? durationStr.match(/(\d+)m/)[1] : 0);
        return h * 60 + m;
    }

    // ========== Helper: Get departure hour ==========
    function getDepartHour(timeStr) {
        return parseInt(timeStr.split(':')[0]);
    }

    // ========== Render Flights ==========
    function renderFlights() {
        const selectedAirlines = [...document.querySelectorAll('.airline-filter:checked')].map(cb => cb.value);
        const maxPrice = parseFloat(priceRange.value);
        const selectedStops = [...document.querySelectorAll('.stop-filter:checked')].map(cb => parseInt(cb.value));

        filteredFlights = allOutboundFlights.filter(f => {
            // Airline filter
            const airlineMatch = selectedAirlines.length === 0 || selectedAirlines.includes(f.airline.code);

            // Price filter (convert to INR for comparison)
            const priceINR = f.currency === 'USD' ? Math.round(f.price * USD_TO_INR) : f.price;
            const priceMatch = priceINR <= maxPrice;

            // Stops filter
            const stopsMatch = selectedStops.includes(f.stops >= 2 ? 2 : f.stops);

            // Time filter
            let timeMatch = true;
            if (activeTimeFilter !== 'all') {
                const hour = getDepartHour(f.depart_time);
                if (activeTimeFilter === 'morning') timeMatch = hour >= 6 && hour < 12;
                else if (activeTimeFilter === 'afternoon') timeMatch = hour >= 12 && hour < 18;
                else if (activeTimeFilter === 'evening') timeMatch = hour >= 18 || hour < 6;
            }

            return airlineMatch && priceMatch && stopsMatch && timeMatch;
        });

        // Sort
        if (activeSortBy === 'cheapest') {
            filteredFlights.sort((a, b) => a.price - b.price);
        } else if (activeSortBy === 'fastest') {
            filteredFlights.sort((a, b) => getDurationMins(a.duration) - getDurationMins(b.duration));
        } else if (activeSortBy === 'earliest') {
            filteredFlights.sort((a, b) => a.depart_time.localeCompare(b.depart_time));
        }

        flightCount.textContent = filteredFlights.length;

        if (filteredFlights.length === 0) {
            flightsList.innerHTML = `
                <div class="flight-no-results">
                    <i class="fas fa-filter"></i>
                    <h3>No flights match your filters</h3>
                    <div class="no-results-suggestions">
                        <h4>💡 Try these:</h4>
                        <ul>
                            <li>Remove some filters</li>
                            <li>Increase your price range</li>
                            <li>Select "Any Time" for departure</li>
                            <li>Check all airline options</li>
                        </ul>
                    </div>
                    <button class="btn btn-primary" id="resetAllFilters">
                        <i class="fas fa-undo"></i> Reset All Filters
                    </button>
                </div>
            `;
            document.getElementById('resetAllFilters')?.addEventListener('click', resetAllFilters);
            return;
        }

        // Find cheapest for badge
        const cheapestPrice = Math.min(...filteredFlights.map(f => f.price));

        flightsList.innerHTML = filteredFlights.map((flight, index) => {
            const isCheapest = flight.price === cheapestPrice && index === 0;
            const priceDisplay = formatPrice(flight.price, flight.currency);

            return `
                <div class="flight-card ${isCheapest ? 'cheapest' : ''}">
                    <div class="flight-main-info">
                        <div class="airline-info">
                            <img src="${flight.airline.logo}" alt="${flight.airline.name}" class="airline-logo"
                                onerror="this.src='data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSI4MCIgaGVpZ2h0PSI0MCIgdmlld0JveD0iMCAwIDgwIDQwIj48cmVjdCB3aWR0aD0iODAiIGhlaWdodD0iNDAiIGZpbGw9IiNlMmU4ZjAiIHJ4PSI4Ii8+PHRleHQgeD0iNDAiIHk9IjI0IiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjNjQ3NDhiIiBmb250LXNpemU9IjEyIiBmb250LWZhbWlseT0iQXJpYWwiPiR7ZmxpZ2h0LmFpcmxpbmUuY29kZX08L3RleHQ+PC9zdmc+'">
                            <span class="airline-name">${flight.airline.name}</span>
                            <span class="flight-number">${flight.flight_number}</span>
                        </div>

                        <div class="flight-timing">
                            <div class="time-block">
                                <span class="time">${flight.depart_time}</span>
                                <span class="airport-code">${flight.origin}</span>
                            </div>

                            <div class="flight-path">
                                <span class="duration">${flight.duration}</span>
                                <div class="path-line">
                                    <i class="fas fa-plane path-line plane-icon"></i>
                                </div>
                                <span class="stops-info ${flight.stops === 0 ? 'direct' : ''}">
                                    ${flight.stops === 0 ? '✈ Non-stop' : flight.stops + (flight.stops === 1 ? ' stop' : ' stops')}
                                </span>
                            </div>

                            <div class="time-block">
                                <span class="time">${flight.arrival_time}</span>
                                <span class="airport-code">${flight.destination}</span>
                                ${flight.next_day ? '<small style="color: #ef4444; font-size: 0.68rem; display:block;">+1 day</small>' : ''}
                            </div>
                        </div>

                        <div class="flight-price-action">
                            <span class="price-label">per traveler</span>
                            <span class="price">${priceDisplay}</span>
                            <button class="btn-select-flight" data-flight-id="${flight.id}" data-airline="${flight.airline.name}" data-flight-num="${flight.flight_number}" data-origin="${flight.origin}" data-dest="${flight.destination}" data-depart="${flight.depart_time}" data-arrive="${flight.arrival_time}" data-price="${priceDisplay}" data-date="${departDate}" data-stops="${flight.stops}" data-duration="${flight.duration}" data-class="${flight.class || 'economy'}">
                                Select <i class="fas fa-arrow-right" style="font-size: 0.7rem;"></i>
                            </button>
                        </div>
                    </div>

                    <div class="flight-meta">
                        <div class="meta-item">
                            <i class="fas fa-suitcase-rolling"></i>
                            <span>Cabin bag included</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-couch"></i>
                            <span>${flight.class ? flight.class.charAt(0).toUpperCase() + flight.class.slice(1) : 'Economy'}</span>
                        </div>
                        <div class="meta-item">
                            <i class="fas fa-bolt"></i>
                            <span>Instant Confirmation</span>
                        </div>
                        ${flight.stops === 0 ? '<div class="meta-item"><i class="fas fa-check-circle" style="color:#10b981;"></i><span style="color:#10b981;">Direct Flight</span></div>' : ''}
                    </div>
                </div>
            `;
        }).join('');

        // Attach click handlers to all Select buttons
        document.querySelectorAll('.btn-select-flight').forEach(btn => {
            btn.addEventListener('click', function () {
                selectFlight(this);
            });
        });
    }

    // ========== Error & No Results ==========
    function showError(msg) {
        errorState.classList.remove('hidden');
        document.getElementById('errorMessage').textContent = msg;
        flightsList.classList.add('hidden');
    }

    function showNoResults() {
        flightsList.classList.remove('hidden');
        flightsList.innerHTML = `
            <div class="flight-no-results">
                <i class="fas fa-plane-slash"></i>
                <h3>No Flights Found</h3>
                <p>We couldn't find any flights from ${origin} to ${destination} on ${formatDateDisplay(departDate)}.</p>
                <div class="no-results-suggestions">
                    <h4>💡 Suggestions:</h4>
                    <ul>
                        <li>Try different travel dates</li>
                        <li>Search for nearby airports</li>
                        <li>Try a different destination</li>
                        <li>Check for connecting flights</li>
                    </ul>
                </div>
                <div class="error-actions">
                    <a href="flight-booking.html" class="btn btn-primary">
                        <i class="fas fa-search"></i> New Search
                    </a>
                    <a href="https://wa.me/919934547108?text=Hi%2C%20I%20need%20flights%20from%20${origin}%20to%20${destination}" target="_blank" class="btn btn-outline" style="color: #25d366; border-color: #25d366;">
                        <i class="fab fa-whatsapp"></i> Ask Our Team
                    </a>
                </div>
            </div>
        `;
    }

    // ========== Reset Filters ==========
    function resetAllFilters() {
        document.querySelectorAll('.stop-filter').forEach(cb => cb.checked = true);
        document.querySelectorAll('.airline-filter').forEach(cb => cb.checked = true);
        priceRange.value = priceRange.max;
        maxPriceLabel.textContent = `₹${parseInt(priceRange.max).toLocaleString('en-IN')}`;

        // Reset time filter
        document.querySelectorAll('.time-filter-btn').forEach(b => b.classList.remove('active'));
        document.querySelector('.time-filter-btn[data-time="all"]').classList.add('active');
        activeTimeFilter = 'all';

        renderFlights();
    }

    // ========== Event Listeners ==========
    priceRange.addEventListener('input', (e) => {
        maxPriceLabel.textContent = `₹${parseInt(e.target.value).toLocaleString('en-IN')}`;
        renderFlights();
    });

    document.querySelectorAll('.stop-filter').forEach(cb => {
        cb.addEventListener('change', renderFlights);
    });

    document.getElementById('clearFilters').addEventListener('click', resetAllFilters);

    // Sidebar menu
    const hamburgerMenu = document.getElementById('hamburgerMenu');
    const sidebar = document.getElementById('sidebar');
    const sidebarOverlay = document.getElementById('sidebarOverlay');
    const sidebarClose = document.getElementById('sidebarClose');

    if (hamburgerMenu) {
        hamburgerMenu.addEventListener('click', () => {
            sidebar.classList.add('open');
            sidebarOverlay.classList.add('active');
            document.body.style.overflow = 'hidden';
        });
    }

    if (sidebarClose) {
        sidebarClose.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('open');
            sidebarOverlay.classList.remove('active');
            document.body.style.overflow = '';
        });
    }

    // Mobile menu toggle
    const mobileMenuToggle = document.getElementById('mobileMenuToggle');
    const navMenu = document.getElementById('navMenu');
    if (mobileMenuToggle) {
        mobileMenuToggle.addEventListener('click', () => {
            navMenu.classList.toggle('active');
            mobileMenuToggle.classList.toggle('active');
        });
    }

    // Auth UI
    if (typeof SupabaseDB !== 'undefined' && SupabaseDB.initAuthUI) {
        SupabaseDB.initAuthUI();
    }

    // ========== Select Flight - Booking Modal ==========
    function selectFlight(btn) {
        const airline = btn.dataset.airline || '';
        const flightNum = btn.dataset.flightNum || '';
        const orig = btn.dataset.origin || '';
        const dest = btn.dataset.dest || '';
        const depart = btn.dataset.depart || '';
        const arrive = btn.dataset.arrive || '';
        const price = btn.dataset.price || '';
        const date = btn.dataset.date || '';
        const stops = btn.dataset.stops || '0';
        const duration = btn.dataset.duration || '';
        const flightClass = btn.dataset.class || 'economy';
        const classLabel = flightClass.charAt(0).toUpperCase() + flightClass.slice(1);

        const stopsText = stops === '0' ? 'Non-stop' : stops + (stops === '1' ? ' stop' : ' stops');

        // WhatsApp message
        const waMsg = encodeURIComponent(
            `Hi C2C Journeys! I want to book this flight:\n\n` +
            `✈️ ${airline} ${flightNum}\n` +
            `📍 ${orig} → ${dest}\n` +
            `📅 ${formatDateDisplay(date)}\n` +
            `⏰ ${depart} - ${arrive} (${duration})\n` +
            `🎫 ${classLabel} | ${stopsText}\n` +
            `💰 ${price} per person\n\n` +
            `Please confirm availability and assist with booking.`
        );

        // Remove any existing modal
        const existing = document.getElementById('flightBookingModal');
        if (existing) existing.remove();

        // Create booking modal
        const modal = document.createElement('div');
        modal.id = 'flightBookingModal';
        modal.style.cssText = 'position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.6);z-index:100000;display:flex;align-items:center;justify-content:center;backdrop-filter:blur(4px);padding:20px;';
        modal.innerHTML = `
            <div style="background:white;border-radius:16px;max-width:480px;width:100%;max-height:90vh;overflow-y:auto;box-shadow:0 20px 60px rgba(0,0,0,0.3);animation:slideUp 0.3s ease;">
                <div style="padding:24px 24px 0;">
                    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px;">
                        <h3 style="font-size:1.1rem;color:#1e293b;margin:0;">
                            <i class="fas fa-plane" style="color:#2563eb;margin-right:8px;"></i>Flight Selected
                        </h3>
                        <button id="closeFlightModal" style="background:none;border:none;font-size:1.2rem;color:#94a3b8;cursor:pointer;padding:4px;">
                            <i class="fas fa-times"></i>
                        </button>
                    </div>

                    <div style="background:linear-gradient(135deg,#eff6ff,#f0f7ff);border-radius:12px;padding:16px;margin-bottom:20px;border:1px solid #dbeafe;">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px;">
                            <span style="font-weight:700;color:#1e293b;">${airline}</span>
                            <span style="font-size:0.8rem;color:#64748b;">${flightNum}</span>
                        </div>
                        <div style="display:flex;align-items:center;justify-content:space-between;gap:12px;">
                            <div style="text-align:center;">
                                <div style="font-size:1.3rem;font-weight:700;color:#0f172a;">${depart}</div>
                                <div style="font-size:0.8rem;color:#64748b;">${orig}</div>
                            </div>
                            <div style="flex:1;text-align:center;">
                                <div style="font-size:0.72rem;color:#64748b;">${duration}</div>
                                <div style="height:2px;background:#cbd5e1;margin:6px 0;position:relative;">
                                    <i class="fas fa-plane" style="position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);color:#2563eb;font-size:0.65rem;background:#eff6ff;padding:0 4px;"></i>
                                </div>
                                <div style="font-size:0.72rem;font-weight:600;color:${stops === '0' ? '#10b981' : '#ef4444'};">${stopsText}</div>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:1.3rem;font-weight:700;color:#0f172a;">${arrive}</div>
                                <div style="font-size:0.8rem;color:#64748b;">${dest}</div>
                            </div>
                        </div>
                        <div style="margin-top:12px;padding-top:12px;border-top:1px dashed #cbd5e1;display:flex;justify-content:space-between;font-size:0.82rem;">
                            <span style="color:#64748b;"><i class="fas fa-calendar" style="margin-right:4px;"></i>${formatDateDisplay(date)}</span>
                            <span style="color:#64748b;"><i class="fas fa-couch" style="margin-right:4px;"></i>${classLabel}</span>
                        </div>
                    </div>

                    <div style="text-align:center;margin-bottom:20px;">
                        <div style="font-size:0.78rem;color:#64748b;">Total Price (per traveler)</div>
                        <div style="font-size:1.6rem;font-weight:800;color:#1e40af;">${price}</div>
                    </div>
                </div>

                <div style="padding:0 24px 24px;">
                    <p style="font-size:0.82rem;color:#475569;text-align:center;margin-bottom:16px;line-height:1.5;">
                        <i class="fas fa-info-circle" style="color:#2563eb;margin-right:4px;"></i>
                        To complete your booking, contact our travel experts:
                    </p>

                    <a href="https://wa.me/919934547108?text=${waMsg}" target="_blank"
                        style="display:flex;align-items:center;justify-content:center;gap:10px;width:100%;padding:14px;background:#25d366;color:white;border-radius:10px;font-weight:600;font-size:0.95rem;text-decoration:none;margin-bottom:10px;transition:transform 0.2s,background 0.2s;"
                        onmouseover="this.style.background='#1fb855';this.style.transform='translateY(-1px)'"
                        onmouseout="this.style.background='#25d366';this.style.transform=''">
                        <i class="fab fa-whatsapp" style="font-size:1.2rem;"></i>
                        Book via WhatsApp
                    </a>

                    <div style="display:flex;gap:10px;">
                        <a href="tel:+919934547108"
                            style="flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:12px;background:#f1f5f9;color:#1e293b;border-radius:10px;font-weight:600;font-size:0.85rem;text-decoration:none;transition:background 0.2s;"
                            onmouseover="this.style.background='#e2e8f0'"
                            onmouseout="this.style.background='#f1f5f9'">
                            <i class="fas fa-phone"></i> Call Us
                        </a>
                        <a href="mailto:sales@c2cjourneys.com?subject=Flight Booking: ${orig} to ${dest}&body=${decodeURIComponent(waMsg).replace(/\n/g, '%0A')}"
                            style="flex:1;display:flex;align-items:center;justify-content:center;gap:8px;padding:12px;background:#f1f5f9;color:#1e293b;border-radius:10px;font-weight:600;font-size:0.85rem;text-decoration:none;transition:background 0.2s;"
                            onmouseover="this.style.background='#e2e8f0'"
                            onmouseout="this.style.background='#f1f5f9'">
                            <i class="fas fa-envelope"></i> Email
                        </a>
                    </div>

                    <p style="text-align:center;font-size:0.72rem;color:#94a3b8;margin-top:14px;">
                        <i class="fas fa-lock" style="margin-right:4px;"></i>
                        Secure booking • Best price guarantee • 24/7 support
                    </p>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // CSS animation
        const style = document.createElement('style');
        style.textContent = '@keyframes slideUp{from{opacity:0;transform:translateY(20px)}to{opacity:1;transform:translateY(0)}}';
        if (!document.querySelector('style[data-flight-modal]')) {
            style.setAttribute('data-flight-modal', '');
            document.head.appendChild(style);
        }

        // Close handlers
        document.getElementById('closeFlightModal').addEventListener('click', () => modal.remove());
        modal.addEventListener('click', (e) => { if (e.target === modal) modal.remove(); });
        document.addEventListener('keydown', function escHandler(e) {
            if (e.key === 'Escape') { modal.remove(); document.removeEventListener('keydown', escHandler); }
        });
    }

    // Start search
    fetchFlights();
});
