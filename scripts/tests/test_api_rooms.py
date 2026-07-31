import requests

payload = {
    "hotel_id": "test",
    "checkin": "2026-08-01",
    "checkout": "2026-08-02",
    "currency": "USD",
    "adults": 2,
    "rooms": [{"adults": 2}],
    "destination": "mumbai",
    "region_id": 6289290
}

print("Fetching destination...")
res = requests.post('http://127.0.0.1:5000/api/hotels/search/destination', json=payload)
data = res.json()
if not data.get('success'):
    print("Failed destination search:", data)
    exit(1)

hotels = data.get('data', {}).get('hotels', [])
if not hotels:
    print("No hotels found")
    exit(1)

hotel_id = hotels[0]['id']
print(f"Testing hotel {hotel_id}...")

payload['hotel_id'] = hotel_id
res = requests.post('http://127.0.0.1:5000/api/hotels/search/hotel', json=payload)
data = res.json()

rates = data.get('data', {}).get('rates', [])
print(f"Found {len(rates)} rates")
for i, rate in enumerate(rates[:10]):
    rs = rate.get('room_static', {})
    print(f"Rate {i}: matched={rs.get('matched')} source={rs.get('image_source')} imgs={len(rs.get('images', []))}")
    if rs.get('matched') is False:
        print(f"   sig: {rs.get('rg_key')}")
