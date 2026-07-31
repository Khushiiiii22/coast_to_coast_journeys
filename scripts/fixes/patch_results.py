import re

with open('js/hotel-results.js', 'r') as f:
    content = f.read()

# Replace handleModifySearch
handle_modify = """function handleModifySearch(e) {
    e.preventDefault();

    const residencySelect = document.getElementById('modifyResidency');
    const residency = residencySelect ? residencySelect.value : 'in';

    // Validate that all child ages are selected
    let allAgesSelected = true;
    modifyRooms.forEach(room => {
        if (room.childAges.some(age => age === null)) allAgesSelected = false;
    });

    if (!allAgesSelected) {
        alert('Please select age for all children.');
        return;
    }

    const params = {
        destination: document.getElementById('modifyDestination').value,
        region_id: document.getElementById('modifyRegionId')?.value || '',
        hotel_id: document.getElementById('modifyHotelId')?.value || '',
        checkin: document.getElementById('modifyCheckin').value,
        checkout: document.getElementById('modifyCheckout').value,
        rooms: modifyRooms, // Pass the entire array
        residency: residency // ETG requires this for accurate pricing
    };

    SearchSession.saveSearchParams(params);
    SearchSession.remove(SearchSession.KEYS.SEARCH_RESULTS);

    closeModifyModal();
    updateSearchBar(params);
    performSearch(params);
}"""

content = re.sub(r'function handleModifySearch\(e\) \{[\s\S]*?performSearch\(params\);\n\}', handle_modify, content)

# Replace setupModifyDestAutocomplete
setup_autocomplete = """function setupModifyDestAutocomplete() {
    const input = document.getElementById('modifyDestination');
    if (!input) return;

    // Create dropdown container
    const wrapper = document.createElement('div');
    wrapper.className = 'autocomplete-wrapper';
    wrapper.style.position = 'relative';
    input.parentNode.insertBefore(wrapper, input);
    wrapper.appendChild(input);

    const dropdown = document.createElement('div');
    dropdown.className = 'autocomplete-dropdown';
    dropdown.style.display = 'none';
    dropdown.style.position = 'absolute';
    dropdown.style.top = '100%';
    dropdown.style.left = '0';
    dropdown.style.right = '0';
    dropdown.style.background = 'white';
    dropdown.style.boxShadow = '0 10px 25px rgba(0,0,0,0.1)';
    dropdown.style.borderRadius = '0 0 12px 12px';
    dropdown.style.zIndex = '1000';
    dropdown.style.maxHeight = '300px';
    dropdown.style.overflowY = 'auto';
    dropdown.style.padding = '8px 0';
    wrapper.appendChild(dropdown);

    function selectLocation(name, id, type) {
        input.value = name;
        if (type === 'region') {
            document.getElementById('modifyRegionId').value = id || '';
            document.getElementById('modifyHotelId').value = '';
        } else if (type === 'hotel') {
            document.getElementById('modifyRegionId').value = '';
            document.getElementById('modifyHotelId').value = id || '';
        }
        dropdown.style.display = 'none';
    }

    // Fetch from ETG backend
    const performSearch = debounce(async (query) => {
        if (query.length < 2) {
            dropdown.style.display = 'none';
            return;
        }

        try {
            dropdown.innerHTML = '<div style="padding: 10px 15px; color: #64748b; font-size: 0.9rem;"><i class="fas fa-spinner fa-spin"></i> Searching ETG...</div>';
            dropdown.style.display = 'block';

            const response = await fetch(`/api/hotels/suggest?query=${encodeURIComponent(query)}&language=en`);
            const result = await response.json();

            if (result.success && result.data) {
                const inner = result.data.data || result.data;
                const regions = inner.regions || [];
                const hotels = inner.hotels || [];

                if (regions.length === 0 && hotels.length === 0) {
                    dropdown.innerHTML = '<div style="padding: 10px 15px; color: #64748b; font-size: 0.9rem;">No destinations found</div>';
                    return;
                }

                let html = '';
                
                if (regions.length > 0) {
                    html += '<div style="padding: 8px 15px; font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase;">Regions</div>';
                    regions.forEach(region => {
                        const name = region.name || 'Unknown';
                        const country = region.country || '';
                        const id = region.id;
                        html += `
                            <div class="location-item-modify" data-type="region" data-id="${id}" data-name="${name}" data-country="${country}" style="padding: 10px 15px; cursor: pointer; display: flex; align-items: center; gap: 10px; hover:background: #f1f5f9;">
                                <i class="fas fa-map-marker-alt" style="color: #64748b;"></i>
                                <div>
                                    <div style="font-weight: 500; color: #1e293b;">${name}</div>
                                    <div style="font-size: 0.8rem; color: #64748b;">${country}</div>
                                </div>
                            </div>
                        `;
                    });
                }
                
                if (hotels.length > 0) {
                    html += '<div style="padding: 8px 15px; font-size: 0.8rem; font-weight: 600; color: #94a3b8; text-transform: uppercase;">Hotels</div>';
                    hotels.slice(0, 5).forEach(hotel => {
                        const name = hotel.name || hotel.label || 'Hotel';
                        const regionName = hotel.region_name || '';
                        const id = hotel.id;
                        html += `
                            <div class="location-item-modify" data-type="hotel" data-id="${id}" data-name="${name}" data-country="${regionName}" style="padding: 10px 15px; cursor: pointer; display: flex; align-items: center; gap: 10px; hover:background: #f1f5f9;">
                                <i class="fas fa-hotel" style="color: #64748b;"></i>
                                <div>
                                    <div style="font-weight: 500; color: #1e293b;">${name}</div>
                                    <div style="font-size: 0.8rem; color: #64748b;">${regionName}</div>
                                </div>
                            </div>
                        `;
                    });
                }

                dropdown.innerHTML = html;
                
                dropdown.querySelectorAll('.location-item-modify').forEach(item => {
                    item.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const type = item.dataset.type;
                        const id = item.dataset.id;
                        const name = item.dataset.name;
                        const country = item.dataset.country;
                        const fullName = `${name}${country ? ', ' + country : ''}`;
                        selectLocation(fullName, id, type);
                    });
                });
            } else {
                dropdown.innerHTML = '<div style="padding: 10px 15px; color: #64748b; font-size: 0.9rem;">No results found</div>';
            }
        } catch (error) {
            console.error('Autocomplete error:', error);
            dropdown.style.display = 'none';
        }
    }, 300);

    // Input listener
    input.addEventListener('input', function () {
        const query = this.value.trim();
        // Clear IDs if user types manually without selecting
        document.getElementById('modifyRegionId').value = '';
        document.getElementById('modifyHotelId').value = '';
        if (query.length > 0) {
            performSearch(query);
        } else {
            dropdown.style.display = 'none';
        }
    });

    // Blur listener
    document.addEventListener('click', function(e) {
        if (!wrapper.contains(e.target)) {
            dropdown.style.display = 'none';
        }
    });
}"""

content = re.sub(r'function setupModifyDestAutocomplete\(\) \{[\s\S]*?createLocationItemHtml\(loc\);\n        \}\);\n\n        dropdown\.innerHTML = html;\n        addClickListeners\(\);\n    \}\n\}', setup_autocomplete, content)


with open('js/hotel-results.js', 'w') as f:
    f.write(content)

