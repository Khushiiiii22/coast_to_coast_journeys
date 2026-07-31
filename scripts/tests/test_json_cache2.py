import json

with open('/Users/khushi22/coasttocoast/backend/data/hotel_static_cache.json', 'r') as f:
    cache = json.load(f)

for hotel_id, hotel in list(cache.items())[:1]:
    rooms = hotel.get('room_groups', [])
    for i, rg in enumerate(rooms[:1]):
        images_ext = rg.get('images_ext', [])
        print("images_ext:", json.dumps(images_ext[:2], indent=2))
        
        images = rg.get('images', [])
        print("images:", json.dumps(images[:2], indent=2))
