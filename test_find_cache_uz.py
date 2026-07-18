import sys
import os
import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.services.etg_service import ETGApiService

load_dotenv()
etg = ETGApiService()

hotel_id = "8473727"
print(f"Scanning for valid book_hashes (h-) for hotel {hotel_id} with residency 'uz'...")

for offset in range(10, 180, 5):  # Scan every 5 days from 10 to 180
    checkin = (datetime.date.today() + datetime.timedelta(days=offset)).strftime('%Y-%m-%d')
    checkout = (datetime.date.today() + datetime.timedelta(days=offset + 2)).strftime('%Y-%m-%d')
    
    res = etg.search_by_hotels(
        hotel_ids=[hotel_id],
        checkin=checkin,
        checkout=checkout,
        guests=[{"adults": 2, "children": []}],
        residency='uz',
        currency="USD"
    )
    
    if res.get('success'):
        data = res['data'].get('data', res['data'])
        hotels = data.get('hotels', [])
        if hotels and hotels[0].get('rates'):
            rate = hotels[0]['rates'][0]
            hash_val = rate.get('book_hash', rate.get('match_hash'))
            if hash_val.startswith('h-'):
                print(f"✅ FOUND BOOKABLE DATE! Checkin: {checkin}, Checkout: {checkout}")
                sys.exit(0)
            
print("❌ Could not find any bookable dates in the sandbox for the next 180 days.")
