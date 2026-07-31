import json

with open('/Users/khushi22/coasttocoast/backend/data/hotel_static_cache.json', 'r') as f:
    cache = json.load(f)

for hotel_id, hotel in list(cache.items())[:1]:
    rooms = hotel.get('room_groups', [])
    print(f"Found {len(rooms)} room groups.")
    for i, rg in enumerate(rooms[:2]):
        print(f"Room {i}: {rg.get('name')}")
        
        images_ext = rg.get('images_ext')
        print(f"images_ext type: {type(images_ext)}")
        if isinstance(images_ext, list):
            print(f"images_ext list len: {len(images_ext)}")
        elif isinstance(images_ext, dict):
            print(f"images_ext dict keys: {list(images_ext.keys())}")
            
        images = rg.get('images')
        print(f"images type: {type(images)}")
        if isinstance(images, list):
            print(f"images list len: {len(images)}")
            if images:
                print(f"First image type: {type(images[0])}")
