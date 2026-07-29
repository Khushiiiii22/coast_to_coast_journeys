import json

with open('/Users/khushi22/coasttocoast/backend/data/hotel_static_cache.json', 'r') as f:
    cache = json.load(f)

# Need a dynamic rate. I don't have one cached.
# But I can look at the make_rg_signature logic.
