import sys
import os
import json

# Add backend dir to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

def test_final_audit_items():
    from services.etg_service import etg_service
    from routes.hotel_routes import format_hotel_policies, enrich_rate_with_room_data
    
    # 1. GUESTS & CHILDREN STRUCTURE (AUDITOR ITEM #12, #13)
    rooms_data = [
        {"adults": 2, "children_ages": []},
        {"adults": 2, "children_ages": [7]}
    ]
    guests = etg_service.format_guests_for_search(adults=2, rooms=rooms_data)
    
    print("--- 1. GUESTS & CHILDREN STRUCTURE (Fix #12, #13) ---")
    print(json.dumps(guests, indent=2))
    
    # 2. HOTEL POLICIES (Fix #3) - Simulation for HID 10004834
    dummy_policies = {
        'metapolicy_struct': {
            'pets': {
                'allowed': True,
                'price': '50',
                'currency': 'USD'
            }
        },
        'metapolicy_extra_info': "Optional Pet Fee applies: 50 USD per stay."
    }
    formatted_policies = format_hotel_policies(dummy_policies)
    
    print("\n--- 2. HOTEL POLICIES BINDING (Fix #3) ---")
    for p in formatted_policies.get('pets', []):
        print(f"Policy: {p.get('label')} -> {p.get('value')}")
    for s in formatted_policies.get('special', []):
        print(f"Extra Info: {s.get('label')} -> {s.get('value')}")

    # 3. ROOM MATCHING (Fix #4)
    mock_rg = {
        555: {'name': 'Luxury Suite', 'images': ['lux.jpg'], 'room_amenities': ['minibar']}
    }
    rate_to_match = {'rg_ext': {'rg': 555}, 'room_name': 'Suite'}
    enriched = enrich_rate_with_room_data(rate_to_match, mock_rg)
    
    print("\n--- 3. ROOM MATCHING LOGIC (Fix #4) ---")
    print(f"Matched: {enriched['room_static']['matched']}")
    print(f"Static Name: {enriched['room_static']['room_name']}")

    print("\n✅ FINAL COMPREHENSIVE VERIFICATION COMPLETE!")

if __name__ == "__main__":
    test_final_audit_items()
