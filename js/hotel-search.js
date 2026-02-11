/**
 * C2C Journeys - Hotel Search Autocomplete
 * Handles location suggestions using RateHawk/ETG Multicomplete API
 */

document.addEventListener('DOMContentLoaded', function () {
    const input = document.getElementById('hotelDestination');
    const regionIdInput = document.getElementById('hotelRegionId');
    const dropdown = document.getElementById('hotelLocationDropdown');
    const resultsContainer = document.getElementById('hotelDropdownResults');
    const loading = document.getElementById('hotelDropdownLoading');
    const empty = document.getElementById('hotelDropdownEmpty');
    const clearBtn = document.getElementById('clearHotelDestination');

    // Country Code Map for better display
    const countryMap = {
        'in': 'India',
        'us': 'United States',
        'gb': 'United Kingdom',
        'ae': 'UAE',
        'fr': 'France',
        'de': 'Germany',
        'it': 'Italy',
        'es': 'Spain',
        'ca': 'Canada',
        'au': 'Australia',
        'th': 'Thailand',
        'sg': 'Singapore',
        'my': 'Malaysia',
        'id': 'Indonesia',
        'jp': 'Japan',
        'cn': 'China',
        'ru': 'Russia',
        'tr': 'Turkey',
        'ch': 'Switzerland',
        'nl': 'Netherlands',
        'za': 'South Africa',
        'br': 'Brazil',
        'mx': 'Mexico',
        'sa': 'Saudi Arabia'
    };

    // If elements are missing (e.g. on other pages), stop
    if (!input || !dropdown) return;

    let debounceTimer;

    // Input event listener
    input.addEventListener('input', function (e) {
        const query = e.target.value;

        // Show/hide clear button
        if (query.length > 0) {
            if (clearBtn) clearBtn.style.display = 'flex';
        } else {
            if (clearBtn) clearBtn.style.display = 'none';
        }

        // Clear existing region ID when user types if they change the text significantly
        // Ideally we only clear if they don't select again. 
        // For now, assume typing means new search.
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

    // Focus listener to show dropdown again if value exists? 
    // Maybe not needed for now.

    // Fetch suggestions from backend
    async function fetchSuggestions(query) {
        showLoading();

        try {
            const response = await fetch(`/api/hotels/suggest?query=${encodeURIComponent(query)}&language=en`);
            const result = await response.json();

            if (result.success && result.data) {
                // Determine data structure 
                const data = result.data.data || result.data || {};
                const regions = data.regions || [];
                const hotels = data.hotels || [];

                displayResults(regions, hotels);
            } else {
                showEmpty();
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
            showEmpty();
        }
    }

    // Display results in dropdown
    function displayResults(regions, hotels) {
        if (resultsContainer) resultsContainer.innerHTML = '';

        if (regions.length === 0 && hotels.length === 0) {
            showEmpty();
            return;
        }

        hideLoading();
        if (empty) empty.style.display = 'none';
        if (resultsContainer) resultsContainer.style.display = 'block';
        dropdown.classList.add('active');

        // Render Regions
        if (regions.length > 0) {
            const regionHeader = document.createElement('div');
            regionHeader.className = 'dropdown-header-home';
            regionHeader.textContent = 'Locations';
            resultsContainer.appendChild(regionHeader);

            regions.forEach(region => {
                const item = document.createElement('div');
                item.className = 'location-item-home';

                // Construct full name (City, Country)
                let countryName = region.country_code ? (countryMap[region.country_code.toLowerCase()] || region.country_code.toUpperCase()) : '';
                let typeName = region.type || 'Region';

                let subText = typeName;
                if (countryName) {
                    subText = `${countryName}`;
                }

                item.innerHTML = `
                    <div class="location-icon-home">
                        <i class="fas fa-map-marker-alt"></i>
                    </div>
                    <div class="location-details-home">
                        <div class="location-name-home">${region.name}</div>
                        <div class="location-country-home">${subText}</div>
                    </div>
                `;

                item.addEventListener('click', () => {
                    // Update input with "City, Country"
                    const fullName = countryName ? `${region.name}, ${countryName}` : region.name;
                    selectLocation(fullName, region.id, 'region');
                });

                resultsContainer.appendChild(item);
            });
        }

        // Render Hotels
        if (hotels.length > 0) {
            const hotelHeader = document.createElement('div');
            hotelHeader.className = 'dropdown-header-home';
            hotelHeader.textContent = 'Hotels';
            resultsContainer.appendChild(hotelHeader);

            hotels.slice(0, 5).forEach(hotel => {
                const item = document.createElement('div');
                item.className = 'location-item-home';

                // Try to get country from hotel info if available
                let regionName = hotel.region_name || '';
                let countryName = hotel.country_code ? (countryMap[hotel.country_code.toLowerCase()] || hotel.country_code.toUpperCase()) : '';

                let subText = 'Hotel';
                if (regionName) subText += ` • ${regionName}`;
                if (countryName) subText += ` • ${countryName}`;

                item.innerHTML = `
                    <div class="location-icon-home">
                        <i class="fas fa-hotel"></i>
                    </div>
                    <div class="location-details-home">
                        <div class="location-name-home">${hotel.name}</div>
                        <div class="location-country-home">${subText}</div>
                    </div>
                `;

                item.addEventListener('click', () => {
                    selectLocation(hotel.name, null, 'hotel');
                });

                resultsContainer.appendChild(item);
            });
        }
    }

    function selectLocation(name, id, type) {
        input.value = name;
        if (regionIdInput && type === 'region') {
            regionIdInput.value = id;
            console.log(`✅ Selected Region: ${name} (ID: ${id})`);
        } else if (regionIdInput) {
            regionIdInput.value = ''; // Clear ID for non-region selections
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

    function hideDropdown() {
        dropdown.classList.remove('active');
    }
});
