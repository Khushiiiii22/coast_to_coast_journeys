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
    const originRaw = urlParams.get('from') || '';
    const destinationRaw = urlParams.get('to') || '';
    const departDate = urlParams.get('depart') || urlParams.get('date') || '';
    const returnDate = urlParams.get('return') || '';
    const adults = parseInt(urlParams.get('adults')) || 1;
    const children = parseInt(urlParams.get('children')) || 0;
    const infants = parseInt(urlParams.get('infants')) || 0;
    const fClass = urlParams.get('class') || 'economy';
    const tripType = urlParams.get('type') || 'oneway';

    function extractAirportCode(value) {
        if (!value) return '';
        const text = String(value).trim().toUpperCase();
        const prefix = text.match(/^([A-Z]{3})\s*-/);
        if (prefix) return prefix[1];
        const token = text.match(/\b([A-Z]{3})\b/);
        if (token) return token[1];
        return text.slice(0, 3);
    }

    const AIRPORT_CITY = {
        DEL: 'New Delhi', BOM: 'Mumbai', BLR: 'Bengaluru', MAA: 'Chennai', CCU: 'Kolkata',
        HYD: 'Hyderabad', GOI: 'Goa', JAI: 'Jaipur', DXB: 'Dubai', LHR: 'London',
        JFK: 'New York', SIN: 'Singapore', CDG: 'Paris', FRA: 'Frankfurt', BKK: 'Bangkok', MLE: 'Male'
    };

    const origin = extractAirportCode(originRaw);
    const destination = extractAirportCode(destinationRaw);

    function airportDisplay(code) {
        const upper = (code || '').toUpperCase();
        const city = AIRPORT_CITY[upper];
        return city ? `${upper} • ${city}` : upper;
    }

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

    function buildFlightDetailsHtml(flight) {
        const travelClass = flight.class ? (flight.class.charAt(0).toUpperCase() + flight.class.slice(1)) : 'Economy';
        const stopsText = flight.stops === 0 ? 'Non-stop' : `${flight.stops} stop${flight.stops > 1 ? 's' : ''}`;
        const totalTravelers = adults + children + infants;

        // Build segments HTML
        const segments = Array.isArray(flight.segments) ? flight.segments : [];
        const segmentsHtml = segments.length > 0
            ? segments.map((seg, idx) => {
                const segFrom = seg.origin || flight.origin;
                const segTo = seg.destination || flight.destination;
                const segFlightNo = seg.flight_number || flight.flight_number;
                const segAirline = seg.airline_name || flight.airline.name;
                const aircraft = seg.aircraft || flight.aircraft || '';
                const layover = seg.layover_minutes ? `
                    <div style="display:flex;align-items:center;gap:8px;padding:8px 14px;margin:6px 0;background:#fef3c7;border-radius:8px;border-left:3px solid #f59e0b;font-size:12px;color:#92400e;">
                        <i class="fas fa-clock" style="color:#f59e0b;"></i>
                        <span>Layover: <strong>${Math.floor(seg.layover_minutes / 60)}h ${seg.layover_minutes % 60}m</strong> at ${airportDisplay(segTo)}</span>
                    </div>` : '';

                return `
                    <div style="border:1px solid #e5e7eb;border-radius:12px;padding:14px 16px;margin-top:${idx === 0 ? '0' : '8px'};background:#fafbfc;">
                        <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                            <div style="display:flex;align-items:center;gap:8px;">
                                <img src="${flight.airline.logo}" alt="${segAirline}" style="height:24px;border-radius:4px;" onerror="this.style.display='none'">
                                <span style="font-weight:700;color:#111827;font-size:14px;">${segAirline}</span>
                                <span style="background:#f1f5f9;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;color:#475569;">${segFlightNo}</span>
                            </div>
                            <div style="font-size:12px;color:#64748b;">${seg.duration || ''} ${aircraft ? '• ' + aircraft : ''}</div>
                        </div>
                        <div style="display:flex;align-items:center;gap:16px;margin-top:12px;">
                            <div style="text-align:center;">
                                <div style="font-size:18px;font-weight:800;color:#0f172a;">${seg.depart_time || flight.depart_time}</div>
                                <div style="font-size:12px;font-weight:600;color:#3b82f6;">${airportDisplay(segFrom)}</div>
                            </div>
                            <div style="flex:1;display:flex;flex-direction:column;align-items:center;">
                                <div style="font-size:11px;color:#94a3b8;">${seg.duration || ''}</div>
                                <div style="width:100%;height:2px;background:linear-gradient(to right,#3b82f6,#8b5cf6);border-radius:2px;position:relative;margin:4px 0;">
                                    <i class="fas fa-plane" style="position:absolute;right:-2px;top:-7px;color:#3b82f6;font-size:12px;"></i>
                                </div>
                                <div style="font-size:11px;color:${flight.stops === 0 ? '#10b981' : '#f59e0b'};font-weight:600;">${idx === 0 ? stopsText : ''}</div>
                            </div>
                            <div style="text-align:center;">
                                <div style="font-size:18px;font-weight:800;color:#0f172a;">${seg.arrival_time || flight.arrival_time}</div>
                                <div style="font-size:12px;font-weight:600;color:#3b82f6;">${airportDisplay(segTo)}</div>
                            </div>
                        </div>
                    </div>
                    ${layover}
                `;
            }).join('')
            : `
                <div style="border:1px solid #e5e7eb;border-radius:12px;padding:14px 16px;background:#fafbfc;">
                    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;">
                        <div style="display:flex;align-items:center;gap:8px;">
                            <img src="${flight.airline.logo}" alt="${flight.airline.name}" style="height:24px;border-radius:4px;" onerror="this.style.display='none'">
                            <span style="font-weight:700;color:#111827;font-size:14px;">${flight.airline.name}</span>
                            <span style="background:#f1f5f9;padding:2px 8px;border-radius:6px;font-size:11px;font-weight:600;color:#475569;">${flight.flight_number}</span>
                        </div>
                        <div style="font-size:12px;color:#64748b;">${flight.duration} ${flight.aircraft ? '• ' + flight.aircraft : ''}</div>
                    </div>
                    <div style="display:flex;align-items:center;gap:16px;margin-top:12px;">
                        <div style="text-align:center;">
                            <div style="font-size:18px;font-weight:800;color:#0f172a;">${flight.depart_time}</div>
                            <div style="font-size:12px;font-weight:600;color:#3b82f6;">${airportDisplay(flight.origin)}</div>
                        </div>
                        <div style="flex:1;display:flex;flex-direction:column;align-items:center;">
                            <div style="font-size:11px;color:#94a3b8;">${flight.duration}</div>
                            <div style="width:100%;height:2px;background:linear-gradient(to right,#3b82f6,#8b5cf6);border-radius:2px;position:relative;margin:4px 0;">
                                <i class="fas fa-plane" style="position:absolute;right:-2px;top:-7px;color:#3b82f6;font-size:12px;"></i>
                            </div>
                            <div style="font-size:11px;color:${flight.stops === 0 ? '#10b981' : '#f59e0b'};font-weight:600;">${stopsText}</div>
                        </div>
                        <div style="text-align:center;">
                            <div style="font-size:18px;font-weight:800;color:#0f172a;">${flight.arrival_time}</div>
                            <div style="font-size:12px;font-weight:600;color:#3b82f6;">${airportDisplay(flight.destination)}</div>
                        </div>
                    </div>
                </div>
            `;

        // Price per traveler
        const pricePerPax = formatPrice(flight.price, flight.currency);
        const totalPrice = formatPrice(flight.price * totalTravelers, flight.currency);

        return `
            <div style="margin-top:10px;padding:16px;border:1px solid #e2e8f0;border-radius:14px;background:#fff;">
                <!-- Journey Summary -->
                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px;padding:12px;background:#f8fafc;border-radius:10px;">
                    <div style="font-size:11px;color:#64748b;">Route<br><span style="font-size:13px;color:#0f172a;font-weight:700;">${airportDisplay(flight.origin)} → ${airportDisplay(flight.destination)}</span></div>
                    <div style="font-size:11px;color:#64748b;">Travel Date<br><span style="font-size:13px;color:#0f172a;font-weight:700;">${formatDateDisplay(departDate)}</span></div>
                    <div style="font-size:11px;color:#64748b;">Duration<br><span style="font-size:13px;color:#0f172a;font-weight:700;">${flight.duration}</span></div>
                    <div style="font-size:11px;color:#64748b;">Class<br><span style="font-size:13px;color:#0f172a;font-weight:700;">${travelClass}</span></div>
                </div>

                <!-- Flight Segments -->
                <div style="font-size:13px;font-weight:700;color:#334155;margin-bottom:10px;display:flex;align-items:center;gap:6px;">
                    <i class="fas fa-route" style="color:#3b82f6;"></i> Flight Segments
                </div>
                ${segmentsHtml}

                <!-- Fare Breakdown -->
                <div style="margin-top:16px;padding:14px;background:#f0fdf4;border-radius:10px;border:1px solid #bbf7d0;">
                    <div style="font-size:13px;font-weight:700;color:#166534;margin-bottom:10px;display:flex;align-items:center;gap:6px;">
                        <i class="fas fa-receipt" style="color:#22c55e;"></i> Fare Breakdown
                    </div>
                    <div style="display:flex;justify-content:space-between;font-size:13px;color:#334155;padding:4px 0;">
                        <span>${adults} Adult${adults > 1 ? 's' : ''} × ${pricePerPax}</span>
                        <span style="font-weight:600;">${formatPrice(flight.price * adults, flight.currency)}</span>
                    </div>
                    ${children > 0 ? `<div style="display:flex;justify-content:space-between;font-size:13px;color:#334155;padding:4px 0;">
                        <span>${children} Child${children > 1 ? 'ren' : ''} × ${pricePerPax}</span>
                        <span style="font-weight:600;">${formatPrice(flight.price * children, flight.currency)}</span>
                    </div>` : ''}
                    ${infants > 0 ? `<div style="display:flex;justify-content:space-between;font-size:13px;color:#334155;padding:4px 0;">
                        <span>${infants} Infant${infants > 1 ? 's' : ''} (10% of adult fare)</span>
                        <span style="font-weight:600;">${formatPrice(Math.round(flight.price * 0.1 * infants), flight.currency)}</span>
                    </div>` : ''}
                    <div style="display:flex;justify-content:space-between;font-size:13px;color:#334155;padding:4px 0;">
                        <span>Taxes & Fees</span>
                        <span style="font-weight:600;color:#16a34a;">Included</span>
                    </div>
                    <div style="margin-top:8px;padding-top:8px;border-top:2px solid #86efac;display:flex;justify-content:space-between;font-size:15px;font-weight:800;color:#15803d;">
                        <span>Total</span>
                        <span>${totalPrice}</span>
                    </div>
                </div>

                <!-- Baggage & Policies -->
                <div style="margin-top:14px;display:grid;grid-template-columns:1fr 1fr;gap:12px;">
                    <div style="padding:12px;background:#eff6ff;border-radius:10px;border:1px solid #bfdbfe;">
                        <div style="font-size:12px;font-weight:700;color:#1e40af;margin-bottom:8px;"><i class="fas fa-suitcase" style="margin-right:4px;"></i> Baggage</div>
                        <div style="font-size:12px;color:#334155;line-height:1.6;">
                            <div>✓ Cabin bag: 7 kg</div>
                            <div>✓ Check-in: 15 kg${travelClass !== 'Economy' ? ' (23 kg for ' + travelClass + ')' : ''}</div>
                        </div>
                    </div>
                    <div style="padding:12px;background:#fefce8;border-radius:10px;border:1px solid #fde68a;">
                        <div style="font-size:12px;font-weight:700;color:#92400e;margin-bottom:8px;"><i class="fas fa-info-circle" style="margin-right:4px;"></i> Policies</div>
                        <div style="font-size:12px;color:#334155;line-height:1.6;">
                            <div>• Cancellation: Charges apply</div>
                            <div>• Date change: Permitted</div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }

    // Update search bar display
    document.getElementById('flightOriginDisplay').textContent = airportDisplay(origin || '');
    document.getElementById('flightDestDisplay').textContent = airportDisplay(destination || '');
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
        const newFrom = extractAirportCode(document.getElementById('modifyFrom').value);
        const newTo = extractAirportCode(document.getElementById('modifyTo').value);
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
                                <span class="airport-code">${airportDisplay(flight.origin)}</span>
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
                                <span class="airport-code">${airportDisplay(flight.destination)}</span>
                                ${flight.next_day ? '<small style="color: #ef4444; font-size: 0.68rem; display:block;">+1 day</small>' : ''}
                            </div>
                        </div>

                        <div class="flight-price-action">
                            <span class="price-label">per traveler</span>
                            <span class="price">${priceDisplay}</span>
                            <button class="btn-select-flight" data-flight-id="${flight.id}" data-airline="${flight.airline.name}" data-flight-num="${flight.flight_number}" data-origin="${flight.origin}" data-dest="${flight.destination}" data-depart="${flight.depart_time}" data-arrive="${flight.arrival_time}" data-price="${priceDisplay}" data-raw-price="${flight.price}" data-currency="${flight.currency || 'INR'}" data-date="${departDate}" data-stops="${flight.stops}" data-duration="${flight.duration}" data-class="${flight.class || 'economy'}">
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

                    <div class="flight-details-toggle" data-details-id="details-${flight.id}" style="margin-top:10px;padding-top:10px;border-top:1px dashed #e5e7eb;cursor:pointer;color:#1d4ed8;font-weight:600;font-size:13px;display:flex;align-items:center;gap:6px;">
                        <i class="fas fa-chevron-down"></i><span class="details-label">Flight Details</span>
                    </div>
                    <div id="details-${flight.id}" style="display:none;">
                        ${buildFlightDetailsHtml(flight)}
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

        document.querySelectorAll('.flight-details-toggle').forEach(toggle => {
            toggle.addEventListener('click', function () {
                const panel = document.getElementById(this.dataset.detailsId);
                const icon = this.querySelector('i');
                const label = this.querySelector('.details-label');
                if (!panel) return;

                const isOpen = panel.style.display === 'block';
                panel.style.display = isOpen ? 'none' : 'block';
                if (label) label.textContent = isOpen ? 'Flight Details' : 'Hide Details';
                if (icon) {
                    icon.classList.toggle('fa-chevron-down', isOpen);
                    icon.classList.toggle('fa-chevron-up', !isOpen);
                }
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

    // ========== Select Flight - Redirect to Passenger Details ==========
    function selectFlight(btn) {
        const flightData = {
            flightId: btn.dataset.flightId || '',
            airline: btn.dataset.airline || '',
            flightNumber: btn.dataset.flightNum || '',
            origin: btn.dataset.origin || '',
            destination: btn.dataset.dest || '',
            departTime: btn.dataset.depart || '',
            arriveTime: btn.dataset.arrive || '',
            price: parseFloat(btn.dataset.rawPrice) || 0,
            currency: btn.dataset.currency || 'INR',
            date: btn.dataset.date || '',
            stops: btn.dataset.stops || '0',
            duration: btn.dataset.duration || '',
            flightClass: btn.dataset.class || 'economy',
            travelers: adults || 1
        };

        // Save flight selection to sessionStorage
        sessionStorage.setItem('ctc_flight_booking', JSON.stringify(flightData));

        // Redirect to passenger details page
        window.location.href = 'flight-passenger-details.html';
    }

    // Start search
    fetchFlights();
});
