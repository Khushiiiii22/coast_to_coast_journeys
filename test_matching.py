import json
import sys

def make_rg_signature(rg_ext):
    if not rg_ext: return ""
    if isinstance(rg_ext, list):
        if len(rg_ext) > 0 and isinstance(rg_ext[0], dict):
            rg_ext = rg_ext[0]
        else: return ""
    if not isinstance(rg_ext, dict): return ""
    
    STABLE_KEYS = {
        'balcony', 'bathroom', 'bedding', 'bedrooms', 'capacity', 
        'club', 'family', 'quality', 'class', 'sex', 'view'
    }
    parts = []
    for k in sorted(rg_ext.keys()):
        if k in STABLE_KEYS and rg_ext[k] not in (None, 0, '0', ''):
            parts.append(f"{k}:{rg_ext[k]}")
    if not parts:
        for k in sorted(rg_ext.keys()):
            if k != 'rg' and k != 'floor' and rg_ext[k] not in (None, 0, '0', ''):
                parts.append(f"{k}:{rg_ext[k]}")
    return ",".join(parts)

try:
    with open('backend/data/hotel_static_cache.json', 'r') as f:
        cache = json.load(f)
        
        # Find a hotel that might be Shangri-La
        target_hotel = None
        for hotel_id, data in cache.items():
            if 'shangri' in data.get('name', '').lower() or 'shangri' in hotel_id.lower():
                target_hotel = data
                break
                
        if not target_hotel:
            print("Could not find shangri-la in cache")
            sys.exit(0)
            
        print(f"Found hotel: {target_hotel.get('name')}")
        room_groups = target_hotel.get('room_groups', [])
        
        print("\n--- Static Room Groups ---")
        for rg in room_groups:
            name = rg.get('name', '')
            if 'deluxe' in name.lower() or 'premier' in name.lower():
                print(f"\nName: {name}")
                rg_ext = rg.get('rg_ext', {})
                print(f"rg_ext raw: {rg_ext}")
                sig = make_rg_signature(rg_ext)
                print(f"Signature: {sig}")
                
except Exception as e:
    print(e)
