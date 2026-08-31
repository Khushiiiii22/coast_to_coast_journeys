import sys
import os
import json
sys.path.append('backend')
from services.etg_service import etg_service

print("Fetching shangri_la_eros_new_delhi from ETG service...")
res = etg_service.get_hotels_static(['shangri_la_eros_new_delhi'])
if res:
    if 'data' in res and isinstance(res['data'], list) and len(res['data']) > 0:
        hotel_data = res['data'][0]
        print(f"Success! Data keys: {hotel_data.keys()}")
        if 'room_groups' in hotel_data:
            print(f"Room groups count: {len(hotel_data['room_groups'])}")
            if len(hotel_data['room_groups']) > 0:
                rg = hotel_data['room_groups'][0]
                print(f"First RG Name: {rg.get('name')}")
                print(f"First RG Images: {len(rg.get('images', []))} / {len(rg.get('images_ext', []))}")
                
                # Check for Deluxe Double Room
                for rg in hotel_data['room_groups']:
                    if 'deluxe' in rg.get('name', '').lower():
                        print(f"Found Deluxe RG: {rg.get('name')} | Images: {len(rg.get('images', []))}")
        else:
            print("NO room_groups in response!")
            print(json.dumps(hotel_data, indent=2))
    else:
        print("Data key missing or empty!")
        print(json.dumps(res, indent=2))
else:
    print("Hotel not found!")
