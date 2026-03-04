import requests
import time
import json

BASE_URL = "http://127.0.0.1:5003/api/hotels"

def run_test():
    print("=== Testing Search with Children ===")
    search_payload = {
        "destination": "Dubai",
        "checkin": "2026-06-20",
        "checkout": "2026-06-25",
        "adults": 4,
        "children_ages": [10, 12],
        "rooms": [{"adults": 2, "childAges": [10, 12]}, {"adults": 2}],
        "currency": "USD"
    }
    
    print("1. Calling /search/destination...")
    resp = requests.post(f"{BASE_URL}/search/destination", json=search_payload)
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
        return
        
    data = resp.json()
    if not data.get('success'):
        print(f"API Error: {data}")
        return
        
    hotels = data.get('data', {}).get('hotels', [])
    print(f"SUCCESS: Found {len(hotels)} hotels.")
    
    if not hotels:
        print("No hotels found to test details.")
        return
        
    hotel = hotels[0]
    hotel_id = hotel.get('id')
        
    print(f"Using Hotel ID: {hotel_id}")
    
    print("\n=== Testing /details-enriched (hp) ===")
    details_payload = {
        **search_payload,
        "hotel_id": hotel_id
    }
    
    print("2. Calling /details-enriched...")
    resp = requests.post(f"{BASE_URL}/details-enriched", json=details_payload)
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
        return
        
    details_data = resp.json()
    if not details_data.get('success'):
        print(f"API Error: {details_data}")
        return
        
    rates = details_data.get('data', {}).get('rates', [])
    print(f"SUCCESS: Got {len(rates)} rates for hotel {hotel_id}")
    
    if not rates:
        print("No rates found to test prebook.")
        return
        
    rate = rates[0]
    book_hash = rate.get('book_hash')
    print(f"Using Book Hash: {book_hash}")
    
    print("\n=== Testing /prebook ===")
    prebook_payload = {
        "book_hash": book_hash,
        "price_increase_percent": 5
    }
    
    print("3. Calling /prebook...")
    resp = requests.post(f"{BASE_URL}/prebook", json=prebook_payload)
    if resp.status_code != 200:
        print(f"FAILED: {resp.text}")
        return
        
    prebook_data = resp.json()
    print(f"Prebook response: {json.dumps(prebook_data, indent=2)}")
    
if __name__ == "__main__":
    run_test()
