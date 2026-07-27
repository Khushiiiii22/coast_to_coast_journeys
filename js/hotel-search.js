/**
 * C2C Journeys - Hotel Search Autocomplete
 * Handles location suggestions using RateHawk/ETG Multicomplete API
 */

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('hotelDestination') || document.getElementById('destination');
    const regionIdInput = document.getElementById('hotelRegionId') || document.getElementById('regionId');
    const dropdown = document.getElementById('hotelLocationDropdown') || document.getElementById('locationDropdown');
    const resultsContainer = document.getElementById('hotelDropdownResults') || document.getElementById('dropdownResults');
    const loading = document.getElementById('hotelDropdownLoading') || document.getElementById('dropdownLoading');
    const empty = document.getElementById('hotelDropdownEmpty') || document.getElementById('dropdownEmpty');
    const clearBtn = document.getElementById('clearHotelDestination') || document.getElementById('clearDestination');

    // Popular destinations (sync with other pages)
    const popularDestinations = [
        { name: 'Singapore', country: 'Singapore', type: 'city' },
        { name: 'London', country: 'England, United Kingdom', type: 'city' },
        { name: 'Tokyo', country: 'Tokyo Prefecture, Japan', type: 'city' },
        { name: 'Paris', country: 'Ile-de-France, France', type: 'city' },
        { name: 'Dubai', country: 'Dubai, UAE', type: 'city' },
        { name: 'New York', country: 'New York, United States', type: 'city' },
        { name: 'Bangkok', country: 'Bangkok, Thailand', type: 'city' },
        { name: 'Mumbai', country: 'Maharashtra, India', type: 'city' }
    ];

    // If elements are missing (e.g. on other pages), stop
    if (!input || !dropdown) return;

    let debounceTimer;

    // Show popular destinations on focus if empty
    input.addEventListener('focus', function () {
        if (this.value.trim().length >= 2) {
            fetchSuggestions(this.value.trim());
        }
    });

    // Input event listener
    input.addEventListener('input', function (e) {
        const query = e.target.value;

        // Show/hide clear button
        if (query.length > 0) {
            if (clearBtn) clearBtn.style.display = 'flex';
        } else {
            if (clearBtn) clearBtn.style.display = 'none';
        }

        // Clear existing region ID when user types
        if (regionIdInput) regionIdInput.value = '';

        clearTimeout(debounceTimer);

        if (query.length < 2) {
            hideDropdown();
            return;
        }

        debounceTimer = setTimeout(() => {
            fetchSuggestions(query);
        }, 300);
    });

    // Clear button listener
    if (clearBtn) {
        clearBtn.addEventListener('click', function () {
            input.value = '';
            if (regionIdInput) regionIdInput.value = '';
            clearBtn.style.display = 'none';
            hideDropdown();
            input.focus();
        });
    }

    // Close dropdown on outside click
    document.addEventListener('click', function (e) {
        if (!input.contains(e.target) && !dropdown.contains(e.target)) {
            hideDropdown();
        }
    });

    // Focus listener to show dropdown again if value exists
    input.addEventListener('focus', function () {
        if (input.value.trim().length >= 2) {
            fetchSuggestions(input.value.trim());
        }
    });

    // Fetch suggestions from ETG multicomplete API
    async function fetchSuggestions(query) {
        showLoading();
        dropdown.style.display = 'block';

        try {
            // Use ETG /search/multicomplete/ endpoint via backend
            const response = await fetch(`/api/hotels/suggest?query=${encodeURIComponent(query)}&language=en`);
            const result = await response.json();

            if (result.success && result.data) {
                const inner = result.data.data || result.data;
                const regions = inner.regions || [];
                const hotels = inner.hotels || [];

                if (regions.length > 0 || hotels.length > 0) {
                    displayETGResults(regions, hotels);
                    return;
                }
            }
            
            showEmpty();
        } catch (error) {
            console.error('❌ Autocomplete error:', error);
            showEmpty();
        }
    }

    // Helper to format Expedia-style location hierarchy
    function formatExpediaRegion(region) {
        const rawType = (region.type || 'region').toLowerCase();
        const name = region.name || 'Unknown';
        let mainTitle = name;
        let subtextParts = [];
        let iconClass = 'fa-location-dot';

        if (rawType.includes('airport')) {
            iconClass = 'fa-plane';
            if (region.iata) {
                mainTitle = `${name} (${region.iata} - ${name} Intl.)`;
            } else {
                mainTitle = `${name} Airport`;
            }
            if (region.country || region.country_name || region.country_code) subtextParts.push(region.country || region.country_name || region.country_code);
        } else if (rawType.includes('city')) {
            iconClass = 'fa-city';
            if (region.state) subtextParts.push(region.state);
            if (region.country || region.country_name || region.country_code) subtextParts.push(region.country || region.country_name || region.country_code);
        } else if (rawType.includes('neighborhood') || rawType.includes('district') || rawType.includes('point of interest') || rawType.includes('subway') || rawType.includes('landmark')) {
            iconClass = 'fa-building';
            if (region.city) subtextParts.push(region.city);
            if (region.state && region.state !== region.city) subtextParts.push(region.state);
            if (region.country || region.country_name || region.country_code) subtextParts.push(region.country || region.country_name || region.country_code);
        } else {
            iconClass = 'fa-location-dot';
            if (region.state) subtextParts.push(region.state);
            if (region.country || region.country_name || region.country_code) subtextParts.push(region.country || region.country_name || region.country_code);
        }

        const subtext = subtextParts.join(', ');
        const fullText = mainTitle + (subtext ? `, ${subtext}` : '');

        return { mainTitle, subtext, fullText, iconClass, id: region.id };
    }

    // Display ETG multicomplete results (Expedia-Style)
    function displayETGResults(regions, hotels) {
        if (resultsContainer) resultsContainer.innerHTML = '';
        hideLoading();
        if (empty) empty.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'block';
        dropdown.classList.add('active');

        // Regions section (Airports, Cities, Neighborhoods, Regions)
        if (regions.length > 0) {
            regions.forEach(region => {
                const itemData = formatExpediaRegion(region);
                const item = document.createElement('div');
                item.className = 'location-item-home expedia-style-item';

                item.innerHTML = `
                    <div class="location-icon-home expedia-icon-wrapper">
                        <i class="fas ${itemData.iconClass}"></i>
                    </div>
                    <div class="location-details-home">
                        <div class="location-name-home">${itemData.mainTitle}</div>
                        <div class="location-country-home">${itemData.subtext}</div>
                    </div>
                `;
                item.addEventListener('click', () => {
                    selectLocation(itemData.fullText, itemData.id, 'region');
                });
                resultsContainer.appendChild(item);
            });
        }

        // Hotels section
        if (hotels.length > 0) {
            hotels.slice(0, 6).forEach(hotel => {
                const item = document.createElement('div');
                item.className = 'location-item-home expedia-style-item';
                const mainTitle = hotel.name || hotel.label || 'Hotel';
                let subtextParts = [];
                if (hotel.region_name) subtextParts.push(hotel.region_name);
                if (hotel.country) subtextParts.push(hotel.country);
                const subtext = subtextParts.join(', ') || 'Hotel';

                item.innerHTML = `
                    <div class="location-icon-home expedia-icon-wrapper">
                        <i class="fas fa-hotel"></i>
                    </div>
                    <div class="location-details-home">
                        <div class="location-name-home">${mainTitle}</div>
                        <div class="location-country-home">${subtext}</div>
                    </div>
                `;
                item.addEventListener('click', () => {
                    selectLocation(mainTitle, hotel.id, 'hotel');
                });
                resultsContainer.appendChild(item);
            });
        }
    }

    // Display results in dropdown
    function displayResults(predictions) {
        if (resultsContainer) resultsContainer.innerHTML = '';

        if (!predictions || predictions.length === 0) {
            showEmpty();
            return;
        }

        hideLoading();
        if (empty) empty.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'block';
        dropdown.classList.add('active');

        // Render Locations header
        const header = document.createElement('div');
        header.className = 'dropdown-header-home';
        header.textContent = 'Locations';
        resultsContainer.appendChild(header);

        predictions.forEach(prediction => {
            const item = document.createElement('div');
            item.className = 'location-item-home';

            // Google prediction format: 
            // main_text: "Mumbai"
            // secondary_text: "Maharashtra, India"
            const name = prediction.structured_formatting?.main_text || prediction.description.split(',')[0];
            const subtext = prediction.structured_formatting?.secondary_text || prediction.description.split(',').slice(1).join(',').trim();
            const fullName = prediction.description; // e.g., "Mumbai, Maharashtra, India"

            // Get icon based on type
            let icon = 'fa-map-marker-alt';
            if (prediction.types && prediction.types.includes('airport')) icon = 'fa-plane';
            if (prediction.types && (prediction.types.includes('hotel') || prediction.types.includes('lodging'))) icon = 'fa-hotel';

            item.innerHTML = `
                <div class="location-icon-home">
                    <i class="fas ${icon}"></i>
                </div>
                <div class="location-details-home">
                    <div class="location-name-home">${name}</div>
                    <div class="location-country-home">${subtext}</div>
                </div>
            `;

            item.addEventListener('click', () => {
                selectLocation(fullName, null, 'region');
            });

            resultsContainer.appendChild(item);
        });
    }

    function selectLocation(name, id, type) {
        input.value = name;
        if (regionIdInput) {
            // Store the ETG region ID from multicomplete results
            regionIdInput.value = id || '';
            console.log(`✅ Selected: ${name} | Region ID: ${id || 'none'} | Type: ${type}`);
        }

        hideDropdown();
    }

    function showLoading() {
        dropdown.classList.add('active');
        if (loading) loading.style.display = 'block';
        if (resultsContainer) resultsContainer.style.display = 'none';
        if (empty) empty.style.display = 'none';
    }

    function showEmpty() {
        dropdown.classList.add('active');
        if (loading) loading.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'none';
        if (empty) empty.style.display = 'block';
    }

    function hideLoading() {
        if (loading) loading.style.display = 'none';
    }

    function hideDropdown() {
        dropdown.classList.remove('active');
        dropdown.style.display = 'none';
    }
});
