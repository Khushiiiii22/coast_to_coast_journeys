/**
 * C2C Journeys - Flight Booking Search Form
 * Handles autocomplete, travelers dropdown, and search redirection
 */

// Global function to close all open calendars
window.closeAllCalendars = function() {
    document.querySelectorAll('.custom-calendar.open').forEach(cal => {
        cal.classList.remove('open');
    });
    document.querySelectorAll('.date-display.open').forEach(disp => {
        disp.classList.remove('open');
    });
};

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
    const searchFormGrid = document.querySelector('.search-form-grid');

    function applyTripType(type) {
        if (type === 'roundtrip') {
            returnDateField.style.display = '';
            returnDateInput.disabled = false;
            returnDateInput.required = true;
            if (searchFormGrid) searchFormGrid.style.gridTemplateColumns = '1fr 1fr 160px 160px 1fr';
        } else {
            returnDateField.style.display = 'none';
            returnDateInput.disabled = true;
            returnDateInput.required = false;
            returnDateInput.value = '';
            updateDateDisplay('returnDate', 'returnDateDisplay');
            if (searchFormGrid) searchFormGrid.style.gridTemplateColumns = '1fr 1fr 160px 1fr';
        }
        // Update active class on trip type labels
        document.querySelectorAll('.trip-type-option').forEach(lbl => {
            const radio = lbl.querySelector('input[type="radio"]');
            if (radio && radio.checked) {
                lbl.classList.add('active');
            } else {
                lbl.classList.remove('active');
            }
        });
    }

    tripTypeRadios.forEach(radio => {
        radio.addEventListener('change', function () {
            applyTripType(this.value);
        });
    });

    // Apply initial state (One Way is default checked)
    const initialTripType = document.querySelector('input[name="tripType"]:checked');
    if (initialTripType) {
        applyTripType(initialTripType.value);
    }

    // 4. Custom Calendar Date Pickers
    const today = new Date();
    today.setHours(0, 0, 0, 0);

    setupCalendar('departDateDisplay', 'departCalendar', 'departDate', today, null, function(selectedDate) {
        // When depart date changes, update return calendar min date
        const retVal = returnDateInput.value;
        if (retVal && retVal < selectedDate) {
            returnDateInput.value = '';
            updateDateDisplay('returnDate', 'returnDateDisplay');
        }
    });

    setupCalendar('returnDateDisplay', 'returnCalendar', 'returnDate', today, null, null);

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
    if (!input || !display) return;

    const dateVal = input.value;
    const dateMain = display.querySelector('.date-main');
    const dateSub = display.querySelector('.date-sub');

    if (!dateVal) {
        if (dateMain) dateMain.textContent = 'Select Date';
        if (dateSub) dateSub.textContent = inputId === 'departDate' ? 'Departure Day' : 'Return Day';
        return;
    }

    try {
        const parts = dateVal.split('-');
        const dateObj = new Date(parseInt(parts[0]), parseInt(parts[1]) - 1, parseInt(parts[2]));
        if (isNaN(dateObj.getTime())) return;

        const day = dateObj.getDate().toString().padStart(2, '0');
        const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
        const yearShort = dateObj.getFullYear().toString().slice(-2);
        const dayNames = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
        const dayName = dayNames[dateObj.getDay()];

        if (dateMain) dateMain.textContent = `${day}/${month}/${yearShort}`;
        if (dateSub) dateSub.textContent = dayName;
    } catch (e) {
        console.error("Error updating date display:", e);
    }
}

/**
 * Custom Calendar Picker
 */
function setupCalendar(displayId, calendarId, inputId, minDate, maxDate, onSelect) {
    const display = document.getElementById(displayId);
    const calendar = document.getElementById(calendarId);
    const input = document.getElementById(inputId);
    if (!display || !calendar || !input) return;

    const MONTHS = ['January','February','March','April','May','June',
                    'July','August','September','October','November','December'];
    const DAYS = ['Su','Mo','Tu','We','Th','Fr','Sa'];

    let viewYear = minDate.getFullYear();
    let viewMonth = minDate.getMonth();

    function renderCalendar() {
        const firstDay = new Date(viewYear, viewMonth, 1).getDay();
        const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
        const todayStr = toDateStr(new Date());
        const selectedVal = input.value;

        let html = `
            <div class="cal-header">
                <button class="cal-nav" id="${calendarId}_prev"><i class="fas fa-chevron-left"></i></button>
                <span class="cal-month-year">${MONTHS[viewMonth]} ${viewYear}</span>
                <button class="cal-nav" id="${calendarId}_next"><i class="fas fa-chevron-right"></i></button>
            </div>
            <div class="cal-weekdays">${DAYS.map(d => `<div class="cal-weekday">${d}</div>`).join('')}</div>
            <div class="cal-days">`;

        for (let i = 0; i < firstDay; i++) {
            html += `<button class="cal-day empty" disabled></button>`;
        }

        for (let d = 1; d <= daysInMonth; d++) {
            const dateStr = `${viewYear}-${String(viewMonth+1).padStart(2,'0')}-${String(d).padStart(2,'0')}`;
            const dateObj = new Date(viewYear, viewMonth, d);
            const isDisabled = dateObj < minDate || (maxDate && dateObj > maxDate);
            const isToday = dateStr === todayStr;
            const isSelected = dateStr === selectedVal;
            let cls = 'cal-day';
            if (isDisabled) cls += ' disabled';
            if (isToday) cls += ' today';
            if (isSelected) cls += ' selected';
            html += `<button class="${cls}" data-date="${dateStr}" ${isDisabled ? 'disabled' : ''}>${d}</button>`;
        }

        html += `</div>`;
        calendar.innerHTML = html;

        calendar.querySelector(`#${calendarId}_prev`).addEventListener('click', function(e) {
            e.stopPropagation();
            viewMonth--;
            if (viewMonth < 0) { viewMonth = 11; viewYear--; }
            renderCalendar();
        });

        calendar.querySelector(`#${calendarId}_next`).addEventListener('click', function(e) {
            e.stopPropagation();
            viewMonth++;
            if (viewMonth > 11) { viewMonth = 0; viewYear++; }
            renderCalendar();
        });

        calendar.querySelectorAll('.cal-day:not(.disabled):not(.empty)').forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.stopPropagation();
                const dateStr = this.dataset.date;
                input.value = dateStr;
                updateDateDisplay(inputId, displayId);
                closeCalendar();
                if (onSelect) onSelect(dateStr);
            });
        });
    }

    function openCalendar() {
        // Close all other calendars
        document.querySelectorAll('.custom-calendar.open').forEach(c => {
            if (c !== calendar) {
                c.classList.remove('open');
                const disp = c.closest('.date-field') && c.closest('.date-field').querySelector('.date-display');
                if (disp) disp.classList.remove('open');
            }
        });
        
        // Close travelers popup if open
        const travelersPopup = document.getElementById('travelersPopup');
        if (travelersPopup) {
            travelersPopup.classList.remove('active');
        }
        
        const val = input.value;
        if (val) {
            const parts = val.split('-');
            viewYear = parseInt(parts[0]);
            viewMonth = parseInt(parts[1]) - 1;
        } else {
            viewYear = minDate.getFullYear();
            viewMonth = minDate.getMonth();
        }
        renderCalendar();
        calendar.classList.add('open');
        display.classList.add('open');
    }

    function closeCalendar() {
        calendar.classList.remove('open');
        display.classList.remove('open');
        // Force remove any lingering open states
        setTimeout(() => {
            if (calendar.classList.contains('open')) {
                calendar.classList.remove('open');
            }
            if (display.classList.contains('open')) {
                display.classList.remove('open');
            }
        }, 10);
    }

    display.addEventListener('click', function(e) {
        e.stopPropagation();
        if (calendar.classList.contains('open')) {
            closeCalendar();
        } else {
            openCalendar();
        }
    });

    display.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' || e.key === ' ') {
            e.preventDefault();
            openCalendar();
        }
    });

    document.addEventListener('click', function(e) {
        if (!calendar.contains(e.target) && !display.contains(e.target)) {
            closeCalendar();
        }
    });
    
    // Also close when clicking on date field wrapper
    const dateFieldWrapper = display.closest('.date-field');
    if (dateFieldWrapper) {
        dateFieldWrapper.addEventListener('click', function(e) {
            // Only handle clicks on the wrapper itself, not its children
            if (e.target === dateFieldWrapper) {
                closeCalendar();
            }
        });
    }
}

function toDateStr(d) {
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
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
