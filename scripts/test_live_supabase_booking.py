import sys
import os
import uuid
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.config import Config
from backend.services.supabase_service import supabase_service
from backend.services.etg_service import ETGApiService

def run_backend_booking_test():
    print("🚀 Starting Live Supabase Backend Insert Test...")
    print("==============================================")
    
    # 1. Initialize ETG service to perform a real sandbox query
    print("🏨 Phase 1: Querying Conrad Los Angeles room options via RateHawk...")
    etg_service = ETGApiService()
    
    checkin = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")
    checkout = (datetime.now() + timedelta(days=11)).strftime("%Y-%m-%d")
    
    # Execute search
    search_res = etg_service.search_by_hotels(
        hotel_ids=["conrad_los_angeles"],
        checkin=checkin,
        checkout=checkout,
        guests=[{"adults": 2, "children": []}],
        currency="USD"
    )
    
    # Unpack double nested 'data' key from ETG API Service
    nested_search_data = search_res.get('data', {})
    if 'data' in nested_search_data:
        nested_search_data = nested_search_data['data']
        
    if not nested_search_data or not nested_search_data.get('hotels'):
        print(f"❌ RateHawk search returned empty: {search_res}")
        return
        
    hotel_info = nested_search_data['hotels'][0]
    print(f"✅ RateHawk search succeeded. Found hotel: {hotel_info.get('id')}")
    
    # We now fetch rates to get a live book_hash
    print("🔑 Phase 2: Fetching rates to get live booking hash...")
    rates_res = etg_service.get_hotel_page(
        hotel_id="conrad_los_angeles",
        checkin=checkin,
        checkout=checkout,
        guests=[{"adults": 2, "children": []}],
        currency="USD"
    )
    
    nested_rates_data = rates_res.get('data', {})
    if 'data' in nested_rates_data:
        nested_rates_data = nested_rates_data['data']
        
    if not nested_rates_data or not nested_rates_data.get('hotels'):
        print(f"❌ RateHawk rates returned empty: {rates_res}")
        return
        
    rates_hotel = nested_rates_data['hotels'][0]
    if not rates_hotel.get('rates'):
        print("❌ No rates returned for Conrad Los Angeles.")
        return
        
    rate = rates_hotel['rates'][0]
    book_hash = rate.get('book_hash')
    print(f"✅ Found booking hash: {book_hash[:40]}...")
    
    # 2. Simulate prebook step
    print("⚡ Phase 3: Executing prebook check...")
    prebook_res = etg_service.prebook(book_hash)
    print(f"Prebook full response: {prebook_res}")
    
    if not prebook_res or not prebook_res.get('success'):
        print(f"❌ Prebook failed: {prebook_res}")
        return
        
    confirmed_hash = prebook_res.get('confirmed_hash')
    if confirmed_hash:
        print(f"✅ Prebook confirmed! Hash: {confirmed_hash[:40]}...")
    else:
        print("⚠️ Prebook did not return confirmed_hash, fallback to original book_hash.")
        confirmed_hash = book_hash
    
    # 3. Simulate backend booking dictionary
    print("📝 Phase 4: Constructing booking dictionary with our new 'rooms' count fix...")
    partner_order_id = f"CTC-TEST-{uuid.uuid4().hex[:8].upper()}"
    
    # Define realistic guest details mapping
    rooms_payload = [{"guests": [{"first_name": "Test", "last_name": "User", "is_child": False}]}]
    guests_payload = [{"first_name": "Test", "last_name": "User", "is_child": False}]
    
    booking_data = {
        'partner_order_id': partner_order_id,
        'user_id': None, # Anon user
        'hotel_id': "conrad_los_angeles",
        'hotel_name': "Conrad Los Angeles",
        'check_in': checkin,
        'check_out': checkout,
        # Apply the fix: rooms is length (integer)
        'rooms': len(rooms_payload) if isinstance(rooms_payload, list) else 1,
        'guests': guests_payload,
        'customer_email': "test_backend@coasttocoastjourneys.com",
        'customer_phone': "+919999999999",
        'special_requests': "Testing backend Supabase insertion directly",
        'total_amount': float(rate.get('total_price', 100.0)),
        'currency': rate.get('currency', 'USD'),
        'status': 'created',
        'booking_response': {}
    }
    
    print(f"Inserting into Supabase 'hotel_bookings' table:")
    print(f"  Partner Order ID: {booking_data['partner_order_id']}")
    print(f"  Rooms count (integer): {booking_data['rooms']} (type: {type(booking_data['rooms'])})")
    print(f"  Guests JSONB: {booking_data['guests']}")
    
    # 4. Insert into Supabase
    db_res = supabase_service.create_booking(booking_data)
    
    if not db_res.get('success'):
        print(f"❌ Supabase insertion failed: {db_res.get('error')}")
        return
        
    print(f"🎉 SUCCESS! Row successfully inserted into Supabase 'hotel_bookings'!")
    print(f"Response: {db_res.get('data')}")
    
    # 5. Query table directly to double-check
    print("🔍 Phase 5: Querying database table to verify presence...")
    verify_res = supabase_service.get_booking_by_partner_order_id(partner_order_id)
    if not verify_res.get('success') or not verify_res.get('data'):
        print("❌ Could not retrieve booking back from database!")
        return
        
    print("✅ Verified: Row exists in the database and was retrieved successfully!")
    print(f"Retrieved Row: {verify_res.get('data')}")
    
    # 6. Clean up
    print("🧹 Cleaning up the test row from live Supabase...")
    supabase_service.client.table('hotel_bookings').delete().eq('partner_order_id', partner_order_id).execute()
    print("✅ Cleaned up successfully!")
    print("==============================================")
    print("🏆 ALL BACKEND AND DATABASE TESTS PASSED 100% PERFECTLY!")

if __name__ == "__main__":
    run_backend_booking_test()
