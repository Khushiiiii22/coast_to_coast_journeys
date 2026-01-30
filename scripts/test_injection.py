
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_hotel_injection_on_failure():
    print("--- Testing Test Hotel Injection on Failure ---")
    
    # 1. Search by region with something that might fail or be empty
    print("\n1. Searching for region 1 (usually empty/invalid in sandbox)...")
    payload = {
        "region_id": 1,
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2
    }
    response = requests.post(f"{BASE_URL}/hotels/search/region", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        hotels = data.get("data", {}).get("hotels", [])
        print(f"Hotels found: {len(hotels)}")
        if hotels and hotels[0].get("id") == "test_payment_1_rupee":
            print("✅ Test hotel successfully injected despite questionable region")
        else:
            print("❌ Test hotel NOT found at index 0")
    else:
        print(f"❌ Search failed with status {response.status_code}: {response.text}")

    # 2. Search by destination with invalid name
    print("\n2. Searching for invalid destination 'InvalidPlaceName'...")
    payload = {
        "destination": "InvalidPlaceName",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2
    }
    response = requests.post(f"{BASE_URL}/hotels/search/destination", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        hotels = data.get("data", {}).get("hotels", [])
        print(f"Hotels found: {len(hotels)}")
        if hotels and hotels[0].get("id") == "test_payment_1_rupee":
            print("✅ Test hotel successfully injected despite invalid destination")
        else:
            print("❌ Test hotel NOT found at index 0")
    else:
        # Destination search usually fails with 400 if region not found, 
        # but my new code should catch it and return success with test hotel?
        # Let's check my code:
        # try: ... except: ... wait, I didn't wrap the region_id lookup in a try-except that returns test hotel yet.
        # I only wrapped the search_by_region call.
        print(f"❌ Search failed with status {response.status_code}: {response.text}")

if __name__ == "__main__":
    test_hotel_injection_on_failure()
