/**
 * C2C Journeys - Flight Results Controller
 * Handles display, filtering, and sorting of flight search results
 */

document.addEventListener('DOMContentLoaded', function () {
    // State
    let allOutboundFlights = [];
    let allInboundFlights = [];
    let filteredOutbound = [];
    let filteredInbound = [];
    let selectedOutbound = null;
    let selectedInbound = null;
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

    // Booking Bar Elements
    const bookingBar = document.getElementById('bookingBar');
    const outboundPreview = document.getElementById('outboundPreview');
    const inboundPreview = document.getElementById('inboundPreview');
    const bookingTotalPrice = document.getElementById('bookingTotalPrice');
    const finalBookBtn = document.getElementById('finalBookBtn');

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
    const originStr = airportDisplay(origin || '');
    const destStr = airportDisplay(destination || '');

    // Extracting code (e.g. IXR) and city name if possible. Format is usually "City (CODE)" or just "CODE".
    const extractCodeAndCity = (str, code) => {
        let displayCode = code || '';
        let displayCity = str;
        // if str has parentheses, assume it's "City (CODE)"
        const match = str.match(/^(.*?)\s*\((.*?)\)$/);
        if (match) {
            displayCity = match[1].trim();
            displayCode = match[2].trim();
        } else if (str === code) {
            // we only have code, no city name available easily without a map, so we'll just show code for both or leave city blank
            displayCity = code;
        }
        return { city: displayCity, code: displayCode };
    };

    const originInfo = extractCodeAndCity(originStr, origin);
    const destInfo = extractCodeAndCity(destStr, destination);

    document.getElementById('flightOriginCodeDisplay').textContent = originInfo.code;
    document.getElementById('flightOriginCityDisplay').textContent = originInfo.city;

    document.getElementById('flightDestCodeDisplay').textContent = destInfo.code;
    document.getElementById('flightDestCityDisplay').textContent = destInfo.city;

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
                allInboundFlights = result.data.inbound || [];

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

    function renderFlights() {
        const selectedAirlines = [...document.querySelectorAll('.airline-filter:checked')].map(cb => cb.value);
        const maxPrice = parseFloat(priceRange.value);
        const selectedStops = [...document.querySelectorAll('.stop-filter:checked')].map(cb => parseInt(cb.value));

        // Filter Outbound
        filteredOutbound = allOutboundFlights.filter(f => {
            const airlineMatch = selectedAirlines.length === 0 || selectedAirlines.includes(f.airline.code);
            const priceINR = f.currency === 'USD' ? Math.round(f.price * USD_TO_INR) : f.price;
            const priceMatch = priceINR <= maxPrice;
            const stopsMatch = selectedStops.includes(f.stops >= 2 ? 2 : f.stops);
            let timeMatch = true;
            if (activeTimeFilter !== 'all') {
                const hour = getDepartHour(f.depart_time);
                if (activeTimeFilter === 'morning') timeMatch = hour >= 6 && hour < 12;
                else if (activeTimeFilter === 'afternoon') timeMatch = hour >= 12 && hour < 18;
                else if (activeTimeFilter === 'evening') timeMatch = hour >= 18 || hour < 6;
            }
            return airlineMatch && priceMatch && stopsMatch && timeMatch;
        });

        // Filter Inbound if roundtrip
        if (tripType === 'roundtrip') {
            filteredInbound = allInboundFlights.filter(f => {
                const airlineMatch = selectedAirlines.length === 0 || selectedAirlines.includes(f.airline.code);
                const stopsMatch = selectedStops.includes(f.stops >= 2 ? 2 : f.stops);
                let timeMatch = true;
                if (activeTimeFilter !== 'all') {
                    const hour = getDepartHour(f.depart_time);
                    if (activeTimeFilter === 'morning') timeMatch = hour >= 6 && hour < 12;
                    else if (activeTimeFilter === 'afternoon') timeMatch = hour >= 12 && hour < 18;
                    else if (activeTimeFilter === 'evening') timeMatch = hour >= 18 || hour < 6;
                }
                return airlineMatch && stopsMatch && timeMatch;
            });
        }

        // Sort both
        const sorter = (a, b) => {
            if (activeSortBy === 'cheapest') return a.price - b.price;
            if (activeSortBy === 'fastest') return getDurationMins(a.duration) - getDurationMins(b.duration);
            if (activeSortBy === 'earliest') return a.depart_time.localeCompare(b.depart_time);
            return 0;
        };
        filteredOutbound.sort(sorter);
        filteredInbound.sort(sorter);

        flightCount.textContent = filteredOutbound.length;

        if (filteredOutbound.length === 0) {
            flightsList.innerHTML = `<div class="flight-no-results" style="grid-column: 1 / -1; text-align: center; padding: 40px;">
                <i class="fas fa-search" style="font-size: 3rem; color: #cbd5e1; margin-bottom: 20px; display: block;"></i>
                <h3 style="color: #475569;">No flights match your filters</h3>
                <p style="color: #64748b;">Try adjusting your price range or airline filters.</p>
            </div>`;
            return;
        }

        // Render Logic
        if (tripType === 'oneway') {
            renderOneway();
        } else {
            renderRoundtrip();
        }
    }

    function generateFlightCardHtml(flight, type) {
        const isSelected = type === 'outbound'
            ? (selectedOutbound && selectedOutbound.id === flight.id)
            : (selectedInbound && selectedInbound.id === flight.id);

        const priceDisplay = formatPrice(flight.price, flight.currency);

        return `
            <div class="flight-card ${isSelected ? 'selected' : ''}" data-id="${flight.id}" data-type="${type}">
                ${isSelected ? '<div class="selection-indicator"><i class="fas fa-check"></i></div>' : ''}
                <div class="flight-main-info" style="padding: 16px;">
                    <div class="airline-info" style="flex: 0 0 100px;">
                        <img src="${flight.airline.logo}" alt="${flight.airline.name}" class="airline-logo" style="height:24px;">
                        <span class="airline-name" style="font-size:0.75rem;">${flight.airline.name}</span>
                        <span class="flight-number" style="font-size:0.65rem;">${flight.flight_number}</span>
                    </div>

                    <div class="flight-timing" style="min-width: 150px; font-size: 0.9rem;">
                        <div class="time-block">
                            <span class="time" style="font-size: 1.1rem;">${flight.depart_time}</span>
                            <span class="airport-code" style="font-size: 0.75rem;">${flight.origin}</span>
                        </div>
                        <div class="flight-path" style="flex: 0 0 60px;">
                            <div class="path-line"></div>
                        </div>
                        <div class="time-block">
                            <span class="time" style="font-size: 1.1rem;">${flight.arrival_time}</span>
                            <span class="airport-code" style="font-size: 0.75rem;">${flight.destination}</span>
                        </div>
                    </div>

                    <div class="flight-price-action" style="text-align: right; flex: 1;">
                        <span class="price" style="font-size: 1.1rem; display: block; color: var(--primary); font-weight: 800;">${priceDisplay}</span>
                        <button class="btn btn-primary select-leg-btn" 
                            style="padding: 4px 12px; font-size: 0.8rem; margin-top: 5px;"
                            data-flight-id="${flight.id}" 
                            data-type="${type}">
                            ${isSelected ? 'Selected' : 'Select'}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    function renderOneway() {
        flightsList.innerHTML = filteredOutbound.map(f => generateFlightCardHtml(f, 'outbound')).join('');
        attachCardListeners();
    }

    function renderRoundtrip() {
        flightsList.innerHTML = `
            <div class="round-trip-results">
                <div class="journey-column">
                    <div class="journey-header">
                        <i class="fas fa-plane-departure"></i>
                        <h3>Departure Flights</h3>
                    </div>
                    <div id="onward-list">
                        ${filteredOutbound.map(f => generateFlightCardHtml(f, 'outbound')).join('')}
                    </div>
                </div>
                <div class="journey-column">
                    <div class="journey-header">
                        <i class="fas fa-plane-arrival"></i>
                        <h3>Return Flights</h3>
                    </div>
                    <div id="return-list">
                        ${filteredInbound.map(f => generateFlightCardHtml(f, 'inbound')).join('')}
                    </div>
                </div>
            </div>
        `;
        attachCardListeners();
    }

    function attachCardListeners() {
        document.querySelectorAll('.select-leg-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                const id = this.dataset.flightId;
                const type = this.dataset.type;
                handleLegSelection(id, type);
            });
        });

        document.querySelectorAll('.flight-card').forEach(card => {
            card.addEventListener('click', function () {
                const id = this.dataset.id;
                const type = this.dataset.type;
                handleLegSelection(id, type);
            });
        });
    }

    function handleLegSelection(id, type) {
        const flight = type === 'outbound'
            ? allOutboundFlights.find(f => f.id === id)
            : allInboundFlights.find(f => f.id === id);

        if (type === 'outbound') {
            selectedOutbound = flight;
        } else {
            selectedInbound = flight;
        }

        updateBookingBar();
        renderFlights(); // Refresh to show selected state
    }

    function updateBookingBar() {
        if (!selectedOutbound && !selectedInbound) {
            bookingBar.classList.remove('active');
            return;
        }

        bookingBar.classList.add('active');

        // Outbound preview
        if (selectedOutbound) {
            outboundPreview.querySelector('.preview-value').textContent =
                `${selectedOutbound.airline.name} • ${selectedOutbound.depart_time}`;
        }

        // Inbound preview
        if (tripType === 'roundtrip') {
            inboundPreview.style.display = 'flex';
            if (selectedInbound) {
                inboundPreview.querySelector('.preview-value').textContent =
                    `${selectedInbound.airline.name} • ${selectedInbound.depart_time}`;
            } else {
                inboundPreview.querySelector('.preview-value').textContent = 'Select a flight';
            }
        } else {
            inboundPreview.style.display = 'none';
        }

        // Total Price
        let total = 0;
        let currency = 'INR';
        if (selectedOutbound) {
            total += selectedOutbound.price;
            currency = selectedOutbound.currency || 'INR';
        }
        if (selectedInbound) {
            total += selectedInbound.price;
        }

        bookingTotalPrice.textContent = formatPrice(total * (adults + children), currency);

        // Final Button
        if (tripType === 'oneway') {
            finalBookBtn.disabled = !selectedOutbound;
        } else {
            finalBookBtn.disabled = !(selectedOutbound && selectedInbound);
        }
    }

    finalBookBtn.addEventListener('click', function () {
        const outboundData = selectedOutbound ? {
            ...selectedOutbound,
            travelers: adults + children,
            class: fClass,
            date: departDate
        } : null;

        const inboundData = selectedInbound ? {
            ...selectedInbound,
            travelers: adults + children,
            class: fClass,
            date: returnDate
        } : null;

        const bookingData = {
            type: tripType,
            outbound: outboundData,
            inbound: inboundData,
            totalPrice: parseFloat(bookingTotalPrice.textContent.replace(/[^\d]/g, ''))
        };

        sessionStorage.setItem('ctc_flight_booking', JSON.stringify(bookingData));
        window.location.href = 'flight-passenger-details.html';
    });

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


    // Start search
    fetchFlights();
});
