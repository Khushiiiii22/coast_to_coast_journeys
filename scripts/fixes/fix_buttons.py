filepath = 'templates/hotel-booking.html'
with open(filepath, 'r') as f:
    content = f.read()

old_js = """        // View Details button click handlers for static hotel cards
        document.querySelectorAll('.hotel-card .btn-accent').forEach(btn => {
            btn.addEventListener('click', function () {
                const card = this.closest('.hotel-card');
                const hotelName = card.querySelector('.hotel-name').textContent;
                const destination = document.getElementById('destination').value || 'New York';
                const checkIn = document.getElementById('checkIn').value;
                const checkOut = document.getElementById('checkOut').value;

                // Construct query parameters
                const params = new URLSearchParams({
                    destination: destination,
                    checkin: checkIn,
                    checkout: checkOut,
                    rooms: JSON.stringify(rooms)
                });

                // Navigate to hotel results, which will show hotels for that destination
                window.location.href = `hotel-results.html?${params.toString()}`;
            });
        });"""

new_js = """        // View Details button click handlers for static hotel cards
        document.querySelectorAll('.hotel-card .btn-accent').forEach(btn => {
            btn.addEventListener('click', function () {
                const card = this.closest('.hotel-card');
                const hotelName = card.querySelector('.hotel-name').textContent;
                const priceStr = card.querySelector('.price-amount').textContent;
                const priceNum = parseFloat(priceStr.replace(/[^0-9.]/g, ''));
                const imgSrc = card.querySelector('.hotel-image img').src;
                
                // Construct a mock hotel object so hotel-details.html can load it
                const mockHotel = {
                    id: 'mock_' + Date.now(),
                    name: hotelName,
                    address: card.querySelector('.hotel-location').textContent.trim(),
                    star_rating: 5,
                    guest_rating: 4.8,
                    review_count: 50,
                    price: priceNum,
                    images: [imgSrc],
                    amenities: ['Free WiFi', 'Pool', 'Restaurant', 'Spa', 'Concierge']
                };
                
                // Save to session storage via SearchSession if available
                if (typeof SearchSession !== 'undefined') {
                    SearchSession.saveSelectedHotel(mockHotel);
                    SearchSession.saveSearchParams({
                        checkin: document.getElementById('checkIn').value || new Date().toISOString().split('T')[0],
                        checkout: document.getElementById('checkOut').value || new Date(Date.now() + 86400000).toISOString().split('T')[0],
                        adults: 2,
                        rooms: [{adults: 2, childAges: []}]
                    });
                } else {
                    sessionStorage.setItem('c2c_selected_hotel', JSON.stringify(mockHotel));
                }

                // Navigate to hotel details page
                window.location.href = `hotel-details.html?id=${mockHotel.id}`;
            });
        });"""

content = content.replace(old_js, new_js)

with open(filepath, 'w') as f:
    f.write(content)
