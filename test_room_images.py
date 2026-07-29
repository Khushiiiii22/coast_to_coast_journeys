import os
import sys
import json
sys.path.append('/Users/khushi22/coasttocoast/backend')
from services.etg_service import ETGApiService

service = ETGApiService()
res = service.suggest('mumbai')
hotel_id = None
if res.get('success'):
    for r in res.get('data', {}).get('hotels', []):
        hotel_id = r.get('id')
        break

if hotel_id:
    print(f"Testing with hotel ID: {hotel_id}")
    static = service.get_hotel_static_data([hotel_id])
    if static.get('success'):
        hotel = static['data'][0]
        rooms = hotel.get('room_groups', [])
        print(f"Found {len(rooms)} room groups.")
        for i, rg in enumerate(rooms[:2]):
            print(f"Room {i}: {rg.get('name')}")
            print(f"images_ext: {len(rg.get('images_ext', []))}")
            print(f"images: {len(rg.get('images', []))}")
            if rg.get('images_ext'):
                print(json.dumps(rg.get('images_ext', [])[:2], indent=2))
            elif rg.get('images'):
                print(json.dumps(rg.get('images', [])[:2], indent=2))
    else:
        print("Failed to get static data")
else:
    print("Could not find hotel ID")
