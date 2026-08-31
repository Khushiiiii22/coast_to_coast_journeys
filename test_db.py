import sys
import os
import json
sys.path.append('backend')
from services.supabase_service import supabase_service

def check():
    print("Checking hotel_cache for shangri_la_eros_new_delhi...")
    res = supabase_service.get_cached_hotel('shangri_la_eros_new_delhi')
    if res.get('success'):
        data = res.get('data')
        
        if isinstance(data, list) and len(data) > 0:
            data = data[0]
        elif isinstance(data, list):
            print("❌ No data returned in list!")
            return
            
        hotel_data = data.get('hotel_data', {}) if isinstance(data, dict) else {}
        print(f"✅ Found hotel in DB: {hotel_data.get('name')}")
        
        room_groups = hotel_data.get('room_groups', [])
        print(f"Room Groups Count: {len(room_groups)}")
        
        if room_groups:
            print("\nFirst 3 Room Groups:")
            for i, rg in enumerate(room_groups[:3]):
                images = rg.get('images', [])
                images_ext = rg.get('images_ext', [])
                print(f"{i+1}. {rg.get('name')}")
                print(f"   Images: {len(images)}")
                print(f"   Images_ext: {len(images_ext)}")
                print(f"   RG Ext Links: {len(rg.get('rg_ext', []))}")
        else:
            print("❌ No room_groups found in DB data!")
    else:
        print(f"❌ Failed to fetch from DB: {res.get('error')}")

if __name__ == '__main__':
    check()
