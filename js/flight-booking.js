/**
 * C2C Journeys - Flight Booking Search Form
 * Handles autocomplete, travelers dropdown, and search redirection
 */

document.addEventListener('DOMContentLoaded', function () {
    initFlightSearch();
});

function initFlightSearch() {
    const flightSearchForm = document.getElementById('flightSearchForm');
    const fromCityInput = document.getElementById('fromCity');
    const toCityInput = document.getElementById('toCity');
    const swapBtn = document.getElementById('swapCities');
    const tripTypeRadios = document.querySelectorAll('input[name="tripType"]');
    const departDateInput = document.getElementById('departDate');
    const returnDateInput = document.getElementById('returnDate');
    const returnDateField = document.getElementById('returnDateField');

    // Travelers Dropdown Elements
    const travelersDropdown = document.getElementById('travelersDropdown');
    const travelersPopup = document.getElementById('travelersPopup');
    const travelersDisplay = document.getElementById('travelersDisplay');
    const travelersDone = document.getElementById('travelersDone');

    const travelersData = { adults: 1, children: 0, infants: 0 };

    // 1. Autocomplete Logic
    setupAutocomplete(fromCityInput);
    setupAutocomplete(toCityInput);

    function extractAirportCode(value) {
        if (!value) return '';
        const text = String(value).trim().toUpperCase();
        const prefix = text.match(/^([A-Z]{3})\s*-/);
        if (prefix) return prefix[1];
        const token = text.match(/\b([A-Z]{3})\b/);
        if (token) return token[1];
        return text.slice(0, 3);
    }

    // 2. Swap Cities
    if (swapBtn) {
        swapBtn.addEventListener('click', function () {
            const temp = fromCityInput.value;
            fromCityInput.value = toCityInput.value;
            toCityInput.value = temp;
            this.classList.add('rotate');
            setTimeout(() => this.classList.remove('rotate'), 300);
        });
    }

    // 3. Trip Type Toggle
    tripTypeRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            if (this.value === 'roundtrip') {
                returnDateInput.disabled = false;
                returnDateField.style.opacity = '1';
                returnDateInput.required = true;
            } else {
                returnDateInput.disabled = true;
                returnDateField.style.opacity = '0.5';
                returnDateInput.required = false;
                returnDateInput.value = '';
                updateDateDisplay('returnDate', 'returnDateDisplay');
            }
        });
    });

    // 4. Date Logic
    const today = new Date().toISOString().split('T')[0];
    departDateInput.min = today;
    returnDateInput.min = today;

    departDateInput.addEventListener('change', function () {
        returnDateInput.min = this.value;
        if (returnDateInput.value && returnDateInput.value < this.value) {
            returnDateInput.value = '';
            updateDateDisplay('returnDate', 'returnDateDisplay');
        }
        updateDateDisplay('departDate', 'departDateDisplay');
    });

    returnDateInput.addEventListener('change', () => updateDateDisplay('returnDate', 'returnDateDisplay'));

    // 5. Travelers Popup
    if (travelersDropdown) {
        travelersDropdown.addEventListener('click', (e) => {
            e.stopPropagation();
            travelersPopup.classList.toggle('active');
        });

        travelersDone.addEventListener('click', () => travelersPopup.classList.remove('active'));

        document.addEventListener('click', (e) => {
            if (!travelersDropdown.contains(e.target) && !travelersPopup.contains(e.target)) {
                travelersPopup.classList.remove('active');
            }
        });

        document.querySelectorAll('#travelersPopup .counter-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                const type = this.dataset.type;
                const isPlus = this.classList.contains('plus');

                if (isPlus) {
                    if (type === 'adults' && travelersData.adults < 9) travelersData.adults++;
                    if (type === 'children' && travelersData.children < 9) travelersData.children++;
                    if (type === 'infants' && travelersData.infants < travelersData.adults) travelersData.infants++;
                } else {
                    if (type === 'adults' && travelersData.adults > 1) travelersData.adults--;
                    if (type === 'children' && travelersData.children > 0) travelersData.children--;
                    if (type === 'infants' && travelersData.infants > 0) travelersData.infants--;
                    if (travelersData.infants > travelersData.adults) travelersData.infants = travelersData.adults;
                }

                document.getElementById('adultsCount').textContent = travelersData.adults;
                document.getElementById('childrenCount').textContent = travelersData.children;
                document.getElementById('infantsCount').textContent = travelersData.infants;
                updateTravelersDisplay();
            });
        });

        document.querySelectorAll('.class-btn').forEach(btn => {
            btn.addEventListener('click', function (e) {
                e.stopPropagation();
                document.querySelectorAll('.class-btn').forEach(b => b.classList.remove('active'));
                this.classList.add('active');
                document.getElementById('cabinClass').value = this.dataset.value;
                updateTravelersDisplay();
            });
        });
    }

    function updateTravelersDisplay() {
        const total = travelersData.adults + travelersData.children;
        const infants = travelersData.infants;
        const cabinClass = document.getElementById('cabinClass').value;
        const classLabels = { economy: 'Economy', premium: 'Premium', business: 'Business', first: 'First' };
        let text = `${total} Traveler${total > 1 ? 's' : ''}`;
        if (infants > 0) text += `, ${infants} Infant${infants > 1 ? 's' : ''}`;
        text += `, ${classLabels[cabinClass]}`;
        travelersDisplay.textContent = text;
    }

    // 6. Form Submission
    if (flightSearchForm) {
        flightSearchForm.addEventListener('submit', function (e) {
            e.preventDefault();

            const from = fromCityInput.dataset.airportCode || extractAirportCode(fromCityInput.value);
            const to = toCityInput.dataset.airportCode || extractAirportCode(toCityInput.value);
            const depart = departDateInput.value;
            const rt = returnDateInput.value;
            const tripType = document.querySelector('input[name="tripType"]:checked').value;
            const cabinClass = document.getElementById('cabinClass').value;

            const params = new URLSearchParams({
                from: from,
                to: to,
                date: depart,
                type: tripType,
                adults: travelersData.adults,
                children: travelersData.children,
                infants: travelersData.infants,
                class: cabinClass
            });

            if (tripType === 'roundtrip' && rt) {
                params.append('return', rt);
            }

            window.location.href = `flight-results.html?${params.toString()}`;
        });
    }
}

/**
 * Custom Date Display Helper
 */
function updateDateDisplay(inputId, displayId) {
    const input = document.getElementById(inputId);
    const display = document.getElementById(displayId);
    if (!display) return;

    const dateVal = input.value;

    if (!dateVal) {
        display.querySelector('.date-main').textContent = 'dd/mm/yy';
        display.querySelector('.date-sub').textContent = 'Day';
        return;
    }

    const dateObj = new Date(dateVal);
    const day = dateObj.getDate().toString().padStart(2, '0');
    const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
    const yearShort = dateObj.getFullYear().toString().slice(-2);
    const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
    const dayName = dayNames[dateObj.getDay()];

    display.querySelector('.date-main').textContent = `${day}/${month}/${yearShort}`;
    display.querySelector('.date-sub').textContent = dayName;
}

/**
 * Autocomplete Implementation
 */
function setupAutocomplete(input) {
    let timeout = null;
    const menu = document.createElement('div');
    menu.className = 'autocomplete-menu';
    input.parentNode.appendChild(menu);

    const fallbackAirports = [
        { code: 'DEL', name: 'Indira Gandhi International Airport', city: 'New Delhi', country: 'IN' },
        { code: 'BOM', name: 'Chhatrapati Shivaji Maharaj International Airport', city: 'Mumbai', country: 'IN' },
        { code: 'BLR', name: 'Kempegowda International Airport', city: 'Bengaluru', country: 'IN' },
        { code: 'MAA', name: 'Chennai International Airport', city: 'Chennai', country: 'IN' },
        { code: 'CCU', name: 'Netaji Subhash Chandra Bose International Airport', city: 'Kolkata', country: 'IN' },
        { code: 'HYD', name: 'Rajiv Gandhi International Airport', city: 'Hyderabad', country: 'IN' },
        { code: 'GOI', name: 'Goa International Airport', city: 'Goa', country: 'IN' },
        { code: 'DXB', name: 'Dubai International Airport', city: 'Dubai', country: 'AE' },
        { code: 'LHR', name: 'Heathrow Airport', city: 'London', country: 'GB' }
    ];

    function showFallback(query) {
        const q = String(query || '').toUpperCase();
        const matches = fallbackAirports.filter(a =>
            a.code.includes(q) || a.city.toUpperCase().includes(q) || a.name.toUpperCase().includes(q)
        ).slice(0, 8);

        if (matches.length === 0) {
            menu.innerHTML = '';
            menu.classList.remove('active');
            return;
        }

        renderSuggestions(matches.map(a => ({
            code: a.code,
            name: a.name,
            city: a.city,
            country: a.country,
            label: `${a.code} - ${a.name}, ${a.city}, ${a.country}`
        })), menu, input);
        menu.classList.add('active');
    }

    input.addEventListener('input', function () {
        clearTimeout(timeout);
        const query = this.value.trim();
        if (query.length < 2) {
            menu.innerHTML = '';
            menu.classList.remove('active');
            return;
        }

        timeout = setTimeout(async () => {
            try {
                const response = await fetch(`/api/flights/suggest?q=${encodeURIComponent(query)}`);
                const result = await response.json();

                if (result.success && result.data.length > 0) {
                    renderSuggestions(result.data, menu, input);
                    menu.classList.add('active');
                } else {
                    showFallback(query);
                }
            } catch (err) {
                console.error('Autocomplete error:', err);
                showFallback(query);
            }
        }, 300);
    });

    document.addEventListener('click', (e) => {
        if (!input.contains(e.target) && !menu.contains(e.target)) {
            menu.classList.remove('active');
        }
    });

    input.addEventListener('focus', () => {
        if (menu.innerHTML) menu.classList.add('active');
    });
}

function renderSuggestions(suggestions, menu, input) {
    menu.innerHTML = suggestions.map(s => `
        <div class="suggestion-item" data-code="${s.code}" data-label="${s.label || `${s.code} - ${s.name}, ${s.city}, ${s.country}`}"
            style="display:flex;align-items:center;gap:12px;padding:12px 16px;cursor:pointer;border-bottom:1px solid #f3f4f6;transition:background 0.15s;">
            <div style="width:44px;height:44px;background:linear-gradient(135deg,#e0e7ff,#c7d2fe);border-radius:10px;display:flex;align-items:center;justify-content:center;flex-shrink:0;">
                <span style="font-weight:800;font-size:13px;color:#3730a3;letter-spacing:0.5px;">${s.code}</span>
            </div>
            <div style="flex:1;min-width:0;">
                <div style="font-weight:600;font-size:0.9rem;color:#111827;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${s.city || ''}, ${s.country || ''}</div>
                <div style="font-size:0.78rem;color:#6b7280;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;">${s.name}</div>
            </div>
            <div style="font-size:0.7rem;font-weight:700;color:#6366f1;background:#eef2ff;padding:3px 8px;border-radius:6px;flex-shrink:0;">${s.code}</div>
        </div>
    `).join('');

    menu.querySelectorAll('.suggestion-item').forEach(item => {
        item.addEventListener('mouseenter', () => item.style.background = '#f8fafc');
        item.addEventListener('mouseleave', () => item.style.background = '');
        item.addEventListener('click', function () {
            input.value = this.dataset.label;
            input.dataset.airportCode = this.dataset.code || '';
            menu.innerHTML = '';
            menu.classList.remove('active');
        });
    });
}
