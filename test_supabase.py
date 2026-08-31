import sys
import os
import json
sys.path.append('backend')
from services.supabase_service import supabase_service

print("Fetching shangri_la_eros_new_delhi from Supabase...")
res = supabase_service.get_hotel_static_data('shangri_la_eros_new_delhi')
if res:
    print(f"Success! Data keys: {res.keys()}")
    if 'room_groups' in res:
        print(f"Room groups count: {len(res['room_groups'])}")
        # Print the first room group name and images
        if len(res['room_groups']) > 0:
            rg = res['room_groups'][0]
            print(f"First RG Name: {rg.get('name')}")
            print(f"First RG Images: {len(rg.get('images', []))} / {len(rg.get('images_ext', []))}")
    else:
        print("NO room_groups in Supabase response!")
else:
    print("Hotel not found in Supabase!")
