import sys
import os
import uuid
import datetime
import json
import random

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.etg_service import ETGApiService
from backend.config import Config

def run_test_booking():
    print("🚀 Starting Manual ETG Test Booking (2 Adults + 1 Child, Residency: UZ)")
    
    etg_service = ETGApiService()
    
    
    # 1. Search for ANY available hotel in a test region (e.g. 1996 - Paris? No let's use a safe one)
    # Using Region ID 6308866 (Test Region?) or just search serps.
    # Let's try searching by region for London (100371) or Dubai.
    # Actually, let's just search by region 121 (Test region often used) or 6049386 (Dubai)
    region_id = 100371 # London
    print(f"1️⃣  Searching for hotels in Region {region_id}...")
    
    checkin = (datetime.date.today() + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
    checkout = (datetime.date.today() + datetime.timedelta(days=32)).strftime('%Y-%m-%d')
    
    guests = [
        {'adults': 2, 'children': [10]}  # 2 Adults, 1 Child
    ]
    
    search_result = etg_service.search_by_region(
        region_id=region_id,
        checkin=checkin,
        checkout=checkout,
        guests=guests,
        residency='uz',
        currency='USD'
    )
    
    if not search_result.get('success') or not search_result.get('data', {}).get('hotels'):
        print(f"❌ Search failed for Region {region_id}.")
        print("Response:", search_result)
        return
        
    hotels = search_result['data']['hotels']
    hotel = hotels[0]
    hotel_id = hotel.get('id')
    print(f"✅ Found hotel: {hotel_id} - {hotel.get('id')}") # RateHawk IDs are strings
    rates = hotel.get('rates', [])
    
    if not rates:
        print("❌ Hotel found but no rates available.")
        return
        
    print(f"✅ Found {len(rates)} rates. Picking the first one.")
    rate = rates[0]
    book_hash = rate.get('book_hash') or rate.get('match_hash')
    
    if not book_hash:
        print("❌ No match_hash found in rate.")
        return
        
    print(f"2️⃣  Prebooking with hash: {book_hash[:20]}...")
    prebook_result = etg_service.prebook(book_hash)
    
    if not prebook_result.get('success'):
        print("❌ Prebook failed:", prebook_result)
        return
        
    print("✅ Prebook successful!")
    
    # 3. Create Booking
    partner_order_id = f"TEST_BOOKING_{uuid.uuid4().hex[:8]}"
    print(f"3️⃣  Creating Booking with Partner Order ID: {partner_order_id}")
    
    booking_guests = [
        {"first_name": "TestAdultOne", "last_name": "Uzbek", "is_child": False},
        {"first_name": "TestAdultTwo", "last_name": "Uzbek", "is_child": False},
        {"first_name": "TestChild", "last_name": "Uzbek", "is_child": True, "age": 10}
    ]
    
    # Check if create_booking needs specific structure
    # Based on etg_service.py: "rooms": [{"guests": guests}]
    # So we pass the list and it wraps it.
    
    booking_result = etg_service.create_booking(
        book_hash=book_hash,
        partner_order_id=partner_order_id,
        guests=booking_guests,
        user_ip="127.0.0.1",
        payment_type="now"
    )
    
    if booking_result.get('success'):
        print("\n🎉 BOOKING SUCCESSFUL!")
        etg_data = booking_result.get('data', {})
        order_id = etg_data.get('data', {}).get('order_id', 'UNKNOWN')
        print(f"✅ ETG Order ID: {order_id}")
        print(f"✅ Partner Order ID: {partner_order_id}")
    else:
        print("\n❌ Booking Failed:")
        print(booking_result)

if __name__ == "__main__":
    run_test_booking()
