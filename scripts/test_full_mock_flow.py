
import requests
import json
import time

BASE_URL = "http://localhost:5000/api"

def test_full_mock_flow():
    print("--- Testing Full Mock Flow ---")
    
    # 1. Test Create Booking (Detects test hash and prefixes TEST-)
    print("\n1. Testing Create Booking (Mocked)...")
    create_payload = {
        "book_hash": "test_hash_1_rupee",
        "guests": [{"first_name": "Test", "last_name": "User"}],
        "hotel_id": "test_payment_1_rupee",
        "hotel_name": "💳 PAYMENT TEST - ₹1 Only Hotel",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "total_amount": 1,
        "currency": "INR"
    }
    create_response = requests.post(f"{BASE_URL}/hotels/book", json=create_payload)
    print(f"Status: {create_response.status_code}")
    print(f"Response: {create_response.text}")
    
    if create_response.status_code != 200:
        print("❌ Create Booking Failed")
        return
        
    create_data = create_response.json()
    partner_order_id = create_data.get("partner_order_id")
    print(f"✅ Created Booking with Partner Order ID: {partner_order_id}")
    
    if not partner_order_id.startswith("TEST-"):
        print("❌ Partner Order ID does not have TEST- prefix")
        return

    # 2. Test Finish Booking (Mocked for TEST-)
    print("\n2. Testing Finish Booking (Mocked)...")
    finish_payload = {"partner_order_id": partner_order_id}
    finish_response = requests.post(f"{BASE_URL}/hotels/book/finish", json=finish_payload)
    print(f"Status: {finish_response.status_code}")
    print(f"Response: {finish_response.text}")
    
    if finish_response.status_code != 200:
        print("❌ Finish Booking Failed")
        return
    print("✅ Finish Booking Successful (Mocked)")

    # 3. Test Poll Status (Mocked for TEST-)
    print("\n3. Testing Poll Status (Mocked)...")
    status_payload = {"partner_order_id": partner_order_id}
    status_response = requests.post(f"{BASE_URL}/hotels/book/status", json=status_payload)
    print(f"Status: {status_response.status_code}")
    print(f"Response: {status_response.text}")
    
    if status_response.status_code != 200:
        print("❌ Status Check Failed")
        return
    
    status_data = status_response.json()
    if status_data.get("data", {}).get("status") == "ok":
        print("✅ Status Check Successful (Mocked)")
    else:
        print(f"❌ Unexpected status: {status_data.get('data', {}).get('status')}")

    print("\n🎉 Full Mock Flow Verification Complete!")

if __name__ == "__main__":
    test_full_mock_flow()
