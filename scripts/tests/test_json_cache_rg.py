import json

with open('/Users/khushi22/coasttocoast/backend/data/hotel_static_cache.json', 'r') as f:
    cache = json.load(f)

for hotel_id, hotel in list(cache.items())[:1]:
    rooms = hotel.get('room_groups', [])
    for i, rg in enumerate(rooms[:2]):
        rg_ext_list = rg.get('rg_ext', [])
        for entry in rg_ext_list:
            rg_val = entry.get('rg')
            print(f"rg_val type: {type(rg_val)}, value: {rg_val}")
