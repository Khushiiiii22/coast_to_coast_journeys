import sys
import json
import os
import datetime
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.services.etg_service import ETGApiService

load_dotenv()
etg = ETGApiService()

# Simulate a 120 days out date
checkin = (datetime.date.today() + datetime.timedelta(days=120)).strftime('%Y-%m-%d')
checkout = (datetime.date.today() + datetime.timedelta(days=122)).strftime('%Y-%m-%d')

print(f"Testing for dates: {checkin} to {checkout}")

res = etg.search_by_hotels(
    hotel_ids=["8473727"],
    checkin=checkin,
    checkout=checkout,
    guests=[{"adults": 2, "children": []}],
    residency='gb',
    currency="USD"
)

if res.get('success'):
    data = res['data'].get('data', res['data'])
    hotels = data.get('hotels', [])
    if hotels:
        print(f"search_by_hotels Found {len(hotels[0].get('rates', []))} rates")
        for rate in hotels[0].get('rates', [])[:3]:
            print(f"Hash: {rate.get('book_hash', rate.get('match_hash'))}")
    else:
        print("No hotels returned in search_by_hotels")
else:
    print(res)
