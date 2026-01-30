import sys
import os
import uuid
import datetime
import json

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.etg_service import ETGApiService
from dotenv import load_dotenv

# Load .env
load_dotenv()

def run_test_booking():
    print("🚀 Starting Manual ETG Multi-Room Test Booking (2 Rooms, Residency: UZ)")
    
    etg_service = ETGApiService()
    
    # 1. Search for available hotels (Multi-room: 2A+1C and 2A)
    checkin = (datetime.date.today() + datetime.timedelta(days=45)).strftime('%Y-%m-%d')
    checkout = (datetime.date.today() + datetime.timedelta(days=47)).strftime('%Y-%m-%d')
    
    # Room 1: 2 Adults + 1 Child (10y)
    # Room 2: 2 Adults
    guests_search = [
        {'adults': 2, 'children': [10]},
        {'adults': 2, 'children': []}
    ]
    
    # Try different regions if one fails
    test_regions = [100371, 6049386, 1, 106] # London, Dubai, Global, Russia
    
    found_hotel = None
    
    for region_id in test_regions:
        print(f"1️⃣  Searching in Region {region_id}...")
        search_result = etg_service.search_by_region(
            region_id=region_id,
            checkin=checkin,
            checkout=checkout,
            guests=guests_search,
            residency='uz',
            currency='USD'
        )
        
        if search_result.get('success') and search_result.get('data', {}).get('hotels'):
            found_hotel = search_result['data']['hotels'][0]
            print(f"✅ Found hotel in Region {region_id}!")
            break
            
    if not found_hotel:
        print("❌ Could not find any hotels with available inventory for these criteria in the Sandbox.")
        return
        
    hotel_id = found_hotel.get('id')
    rates = found_hotel.get('rates', [])
    if not rates:
        print("❌ Found hotel but no rates available.")
        return
        
    rate = rates[0]
    # In search results, matches usually provide book_hash
    book_hash = rate.get('match_hash') or rate.get('book_hash')
    
    print(f"2️⃣  Prebooking with hash: {book_hash[:20]}...")
    prebook_result = etg_service.prebook(book_hash)
    
    if not prebook_result.get('success'):
        print("❌ Prebook failed:", prebook_result)
        return
        
    print("✅ Prebook successful!")
    
    # 3. Create Booking (Manually construct multi-room payload)
    partner_order_id = f"TEST_UZ_{uuid.uuid4().hex[:8]}"
    print(f"3️⃣  Creating Multi-Room Booking: {partner_order_id}")
    
    # Note: We are manually calling the _make_request because etg_service.create_booking currently only supports 1 room
    room_1_guests = [
        {"first_name": "AdultOne", "last_name": "RoomOne", "is_child": False},
        {"first_name": "AdultTwo", "last_name": "RoomOne", "is_child": False},
        {"first_name": "ChildOne", "last_name": "RoomOne", "is_child": True, "age": 10}
    ]
    room_2_guests = [
        {"first_name": "AdultThree", "last_name": "RoomTwo", "is_child": False},
        {"first_name": "AdultFour", "last_name": "RoomTwo", "is_child": False}
    ]
    
    booking_payload = {
        "hash": book_hash,
        "partner_order_id": partner_order_id,
        "payment_type": {"type": "now"},
        "user_ip": "127.0.0.1",
        "rooms": [
            {"guests": room_1_guests},
            {"guests": room_2_guests}
        ]
    }
    
    booking_result = etg_service._make_request("/hotel/order/booking/form/", booking_payload)
    
    if booking_result.get('status') == 'ok':
        print("\n🎉 MULTI-ROOM BOOKING SUCCESSFUL!")
        order_id = booking_result.get('data', {}).get('order_id', 'UNKNOWN')
        print(f"✅ ETG Order ID: {order_id}")
        print(f"✅ Partner Order ID: {partner_order_id}")
        print(f"✅ Criteria: 2 Rooms (2A+1C and 2A), Residency: UZ")
    else:
        print("\n❌ Booking Failed:")
        print(json.dumps(booking_result, indent=2))

if __name__ == "__main__":
    run_test_booking()
