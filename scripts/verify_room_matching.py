import sys
import os

# Add backend dir to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

def test_room_matching():
    from routes.hotel_routes import enrich_rate_with_room_data
    
    # 1. Mock static room groups (indexed by rg_ext.rg)
    # The auditor wants TO BE SURE that rg_ext from one hotel 
    # doesn't match another. Since room_groups is built in 
    # the scope of a SINGLE hotel details request, this isolation is guaranteed.
    mock_room_groups = {
        12345: {
            'name': 'Superior Double Room',
            'images': ['img1.jpg', 'img2.jpg'],
            'room_amenities': ['wifi', 'tv']
        }
    }
    
    # 2. Test Case A: Exact Match
    rate_match = {
        'rg_ext': {'rg': 12345},
        'room_name': 'Dynamic Room Name',
        'payment_options': {'payment_types': [{'amount': '100'}]}
    }
    
    # In the real app, COMMISSION_PERCENT is a global from config
    # We will just verify that the static data is attached
    enriched_match = enrich_rate_with_room_data(rate_match, mock_room_groups)
    
    print("--- TEST CASE A: Matching rg_ext ---")
    print(f"Match status: {enriched_match['room_static']['matched']}")
    print(f"Matched Room Name: {enriched_match['room_static']['room_name']}")
    print(f"Matched Images: {len(enriched_match['room_static']['images'])}")
    
    assert enriched_match['room_static']['matched'] is True
    assert enriched_match['room_static']['room_name'] == 'Superior Double Room'
    
    # 3. Test Case B: No Match (Fallback to Dynamic Grouping)
    # The auditor said: "if you can't match... you should group these rates into a new block... based on the received rg_ext"
    rate_no_match = {
        'rg_ext': {'rg': 99999},
        'room_name': 'Fallback Room Name',
        'payment_options': {'payment_types': [{'amount': '200'}]}
    }
    
    enriched_no_match = enrich_rate_with_room_data(rate_no_match, mock_room_groups)
    
    print("\n--- TEST CASE B: Fallback (No Match) ---")
    print(f"Match status: {enriched_no_match['room_static']['matched']}")
    print(f"Fallback Room Name: {enriched_no_match['room_static']['room_name']}")
    print(f"RG Key: {enriched_no_match['room_static']['rg_key']}")
    
    assert enriched_no_match['room_static']['matched'] is False
    assert enriched_no_match['room_static']['room_name'] == 'Fallback Room Name'
    assert enriched_no_match['room_static']['rg_key'] == 99999

    print("\n✅ ROOM MATCHING & FALLBACK LOGIC VERIFIED!")

if __name__ == "__main__":
    test_room_matching()
