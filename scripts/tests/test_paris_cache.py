import sys
import os
import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.services.etg_service import ETGApiService

load_dotenv()
etg = ETGApiService()

print(f"Scanning for valid book_hashes (h-) in PARIS...")

for offset in range(10, 180, 5):
    checkin = (datetime.date.today() + datetime.timedelta(days=offset)).strftime('%Y-%m-%d')
    checkout = (datetime.date.today() + datetime.timedelta(days=offset + 2)).strftime('%Y-%m-%d')
    
    res = etg.search_by_region(
        region_id="2534", # Paris
        checkin=checkin,
        checkout=checkout,
        rooms=[{"adults": 2, "children": []}],
        residency='gb',
        currency="USD"
    )
    
    if res.get('success'):
        data = res['data'].get('data', res['data'])
        hotels = data.get('hotels', [])
        found_h_hash = False
        for hotel in hotels[:10]: # Check first 10 hotels
            if hotel.get('rates'):
                for rate in hotel['rates']:
                    hash_val = rate.get('book_hash', rate.get('match_hash'))
                    if hash_val and hash_val.startswith('h-'):
                        print(f"✅ FOUND BOOKABLE DATE IN PARIS! Checkin: {checkin}, Hotel ID: {hotel.get('id')}")
                        sys.exit(0)
                        
print("❌ Could not find any bookable dates in Paris in the sandbox for the next 180 days.")
