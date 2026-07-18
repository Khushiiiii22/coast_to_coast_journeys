import re

with open('templates/hotel-booking.html', 'r', encoding='utf-8') as f:
    content = f.read()

new_search_logic = """        async function searchLocations(query) {
            highlightedIndex = -1;
            dropdownEmpty.style.display = 'none';
            dropdownLoading.classList.add('active');
            dropdownResults.innerHTML = '';
            locationDropdown.classList.add('active');

            try {
                // Try ETG / RateHawk suggest API first (works on home page)
                const response = await fetch(`/api/hotels/suggest?query=${encodeURIComponent(query)}&language=en`);
                const result = await response.json();

                dropdownLoading.classList.remove('active');

                if (result.success && result.data) {
                    const inner = result.data.data || result.data;
                    const regions = inner.regions || [];
                    const hotels = inner.hotels || [];

                    if (regions.length > 0 || hotels.length > 0) {
                        let html = '<div class="dropdown-header">Search Results</div>';
                        
                        regions.forEach(region => {
                            html += createLocationItemHtml({
                                name: region.name,
                                country: region.country || '',
                                type: 'city',
                                place_id: region.id,
                                full_description: region.name + ', ' + (region.country || '')
                            });
                        });
                        
                        hotels.forEach(hotel => {
                            html += createLocationItemHtml({
                                name: hotel.name,
                                country: hotel.region?.name || '',
                                type: 'hotel',
                                place_id: hotel.id,
                                full_description: hotel.name + ', ' + (hotel.region?.name || '')
                            });
                        });
                        
                        dropdownResults.innerHTML = html;
                        attachLocationListeners();
                        return;
                    }
                }
                
                // Fallback to old behavior (Google places) if ETG empty
                const fallbackResponse = await fetch(`/api/hotels/autocomplete?query=${encodeURIComponent(query)}`);
                const fallbackData = await fallbackResponse.json();
                
                if (fallbackData.success && fallbackData.predictions && fallbackData.predictions.length > 0) {
                    let html = '<div class="dropdown-header">Search Results</div>';
                    fallbackData.predictions.forEach(pred => {
                        const location = {
                            name: pred.structured_formatting?.main_text || pred.description.split(',')[0],
                            country: pred.structured_formatting?.secondary_text || pred.description.split(',').slice(1).join(',').trim(),
                            type: getLocationType(pred.types || []),
                            place_id: pred.place_id,
                            full_description: pred.description
                        };
                        html += createLocationItemHtml(location);
                    });
                    dropdownResults.innerHTML = html;
                    attachLocationListeners();
                } else {
                    dropdownEmpty.style.display = 'block';
                }
            } catch (error) {
                console.error('Autocomplete error:', error);
                dropdownLoading.classList.remove('active');
                showPopularDestinations();
            }
        }"""

# Use regex to replace the old searchLocations function
pattern = re.compile(r'async function searchLocations\(query\)\s*\{.*?catch \(error\)\s*\{\s*console\.error\(\'Autocomplete error:\', error\);\s*dropdownLoading\.classList\.remove\(\'active\'\);\s*// Fallback to popular destinations on error\s*showPopularDestinations\(\);\s*\}\s*\}', re.DOTALL)

new_content = pattern.sub(new_search_logic, content)

if new_content != content:
    with open('templates/hotel-booking.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Updated searchLocations in hotel-booking.html")
else:
    print("Could not find searchLocations to replace")

