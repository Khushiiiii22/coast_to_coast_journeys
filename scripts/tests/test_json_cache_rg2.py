import json

with open('/Users/khushi22/coasttocoast/backend/data/hotel_static_cache.json', 'r') as f:
    cache = json.load(f)

for hotel_id, hotel in list(cache.items())[:1]:
    rooms = hotel.get('room_groups', [])
    for i, rg in enumerate(rooms[:2]):
        rg_ext = rg.get('rg_ext')
        print(f"rg_ext type: {type(rg_ext)}")
        if isinstance(rg_ext, dict):
            print(f"rg_ext keys: {list(rg_ext.keys())}")
        elif isinstance(rg_ext, list):
            print(f"rg_ext list length: {len(rg_ext)}")
            if len(rg_ext) > 0:
                print(f"First item type: {type(rg_ext[0])}")
        print("rg_ext value:", rg_ext)
