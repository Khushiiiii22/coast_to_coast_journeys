import sys
import os
import json
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from services.etg_service import ETGApiService

etg = ETGApiService()
print("Testing live API...")
info = etg.get_hotel_info("shangri_la_eros_new_delhi")
if 'success' in info and info['success']:
    data = info['data'].get('data', info['data'])
    print(f"Hotel Info fetched successfully.")
    print(f"Has room_groups? {'room_groups' in data}")
    if 'room_groups' in data:
        print(f"Number of room groups: {len(data['room_groups'])}")
    else:
        print("room_groups is MISSING from live API response!")
else:
    print("API call failed:")
    print(info)
