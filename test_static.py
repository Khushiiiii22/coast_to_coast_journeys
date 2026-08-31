import json

try:
    with open('backend/data/hotel_static_cache.json', 'r') as f:
        cache = json.load(f)
        # Get the first hotel in the cache
        hotel_id = list(cache.keys())[0]
        hotel_data = cache[hotel_id]
        
        print(f"Hotel ID: {hotel_id}")
        
        # Check if room_groups exists
        room_groups = hotel_data.get('room_groups', [])
        print(f"Number of room groups: {len(room_groups)}")
        
        for i, rg in enumerate(room_groups[:3]):
            print(f"--- Room Group {i} ---")
            print("Name:", rg.get('name'))
            print("Keys:", list(rg.keys()))
            if 'images_ext' in rg:
                print("images_ext:", rg['images_ext'])
            if 'images' in rg:
                print("images:", rg['images'])
            print("rg_ext:", rg.get('rg_ext'))
            
except Exception as e:
    print(e)
