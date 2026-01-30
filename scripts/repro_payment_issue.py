
import requests
import json

BASE_URL = "http://localhost:5000/api"

def test_test_hotel_flow():
    print("--- Testing Test Hotel Flow ---")
    
    # 1. Test Prebook
    print("\n1. Testing Prebook Mock...")
    payload = {
        "book_hash": "test_hash_1_rupee"
    }
    response = requests.post(f"{BASE_URL}/hotels/prebook", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    # 2. Test Create Booking
    print("\n2. Testing Create Booking Mock...")
    payload = {
        "book_hash": "test_hash_1_rupee",
        "guests": [{"first_name": "Test", "last_name": "User"}],
        "hotel_id": "test_payment_1_rupee",
        "hotel_name": "💳 PAYMENT TEST - ₹1 Only Hotel",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "total_amount": 1,
        "currency": "INR"
    }
    response = requests.post(f"{BASE_URL}/hotels/book", json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code == 200:
        data = response.json()
        booking_id = data.get("booking_id")
        partner_order_id = data.get("partner_order_id")
        print(f"Success! Booking ID: {booking_id}, Partner Order ID: {partner_order_id}")
    else:
        print("Failed!")

if __name__ == "__main__":
    test_test_hotel_flow()
