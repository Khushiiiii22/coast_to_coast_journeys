import sys
import os
import uuid
import datetime
import json
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.etg_service import ETGApiService

load_dotenv()

def run_test_booking():
    print("🚀 Starting Final Attempt: ETG Multi-Room Test Booking")
    etg_service = ETGApiService()
    
    test_hotel_id = '8473727'
    # Try multiple dates in the future
    date_offsets = [60, 90, 120]
    
    guests_search = [
        {'adults': 2, 'children': [10]},
        {'adults': 2, 'children': []}
    ]
    
    target_rate = None
    target_date = None

    for offset in date_offsets:
        checkin = (datetime.date.today() + datetime.timedelta(days=offset)).strftime('%Y-%m-%d')
        checkout = (datetime.date.today() + datetime.timedelta(days=offset + 2)).strftime('%Y-%m-%d')
        
        print(f"1️⃣  Searching Hotel {test_hotel_id} for dates: {checkin} to {checkout}...")
        
        search_result = etg_service.search_by_hotels(
            hotel_ids=[test_hotel_id],
            checkin=checkin,
            checkout=checkout,
            guests=guests_search,
            residency='uz',
            currency='USD'
        )
        
        if search_result.get('success') and search_result.get('data', {}).get('hotels'):
            hotel = search_result['data']['hotels'][0]
            if hotel.get('rates'):
                target_rate = hotel['rates'][0]
                target_date = (checkin, checkout)
                print(f"✅ Found available rates for {checkin}!")
                break
        else:
            print(f"   - No rates found for {checkin}. Status: {search_result.get('error')}")

    if not target_rate:
        print("❌ Could not find inventory even for test hotel 8473727 with Uzbek residency.")
        print("💡 Suggestion: The ETG Sandbox may require a specific residency-to-region mapping for test hotels.")
        return

    book_hash = target_rate.get('book_hash') or target_rate.get('match_hash')
    print(f"2️⃣  Prebooking with hash: {book_hash[:20]}...")
    prebook_result = etg_service.prebook(book_hash)
    
    if not prebook_result.get('success'):
        print("❌ Prebook failed:", prebook_result)
        return
        
    print("✅ Prebook successful!")
    
    partner_order_id = f"CERT_UZ_{uuid.uuid4().hex[:6].upper()}"
    print(f"3️⃣  Creating Booking: {partner_order_id}")
    
    booking_payload = {
        "hash": book_hash,
        "partner_order_id": partner_order_id,
        "payment_type": {"type": "now"},
        "user_ip": "127.0.0.1",
        "rooms": [
            {
                "guests": [
                    {"first_name": "Asror", "last_name": "Uzbek", "is_child": False},
                    {"first_name": "Lola", "last_name": "Uzbek", "is_child": False},
                    {"first_name": "Shoxruh", "last_name": "Uzbek", "is_child": True, "age": 10}
                ]
            },
            {
                "guests": [
                    {"first_name": "Zafar", "last_name": "Uzbek", "is_child": False},
                    {"first_name": "Nigora", "last_name": "Uzbek", "is_child": False}
                ]
            }
        ]
    }
    
    booking_result = etg_service._make_request("/hotel/order/booking/form/", booking_payload)
    
    if booking_result.get('status') == 'ok':
        print("\n🎉 BOOKING COMPLETE!")
        order_id = booking_result.get('data', {}).get('order_id', 'UNKNOWN')
        print(f"✅ ETG Order ID: {order_id}")
        print(f"✅ Residency: UZ, Guests: 2 Rooms (2A+1C, 2A)")
    else:
        print("\n❌ Booking Failed:")
        print(json.dumps(booking_result, indent=2))

if __name__ == "__main__":
    run_test_booking()
