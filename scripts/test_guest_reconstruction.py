import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.etg_service import etg_service

def test_reconstruction():
    print("Testing Guest Reconstructor...")
    
    # Test Case 1: 2 rooms, 3 adults (Integer)
    res1 = etg_service.format_guests_for_search(adults=3, rooms=2)
    print(f"Test 1 (2 rooms, 3 adults): {res1}")
    assert len(res1) == 2
    assert res1[0]['adults'] == 2
    assert res1[1]['adults'] == 1
    
    # Test Case 2: 3 rooms, 5 adults, 2 children (Integer)
    res2 = etg_service.format_guests_for_search(adults=5, children_ages=[5, 12], rooms=3)
    print(f"Test 2 (3 rooms, 5 adults, 2 children): {res2}")
    assert len(res2) == 3
    assert sum(r['adults'] for r in res2) == 5
    assert len(res2[0]['children']) == 2
    
    # Test Case 3: Already an array (should pass through)
    rooms_array = [{"adults": 1, "children": [8]}, {"adults": 1, "children": []}]
    res3 = etg_service.format_guests_for_search(adults=2, rooms=rooms_array)
    print(f"Test 3 (Array input): {res3}")
    assert res3 == rooms_array
    
    print("✅ All reconstruction tests passed!")

if __name__ == "__main__":
    test_reconstruction()
