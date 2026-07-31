import json

with open('/Users/khushi22/coasttocoast/backend/data/hotel_static_cache.json', 'r') as f:
    cache = json.load(f)

for hotel_id, hotel in list(cache.items())[:1]:
    rooms = hotel.get('room_groups', [])
    for i, rg in enumerate(rooms[:1]):
        print(f"Room group keys: {list(rg.keys())}")
        if 'room_group_id' in rg:
            print("room_group_id:", rg['room_group_id'])
        if 'id' in rg:
            print("id:", rg['id'])
