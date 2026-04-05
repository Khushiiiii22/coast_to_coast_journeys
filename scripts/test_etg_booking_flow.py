import os
import sys
import json
import time

# Add backend directory to sys.path
backend_dir = os.path.join(os.getcwd(), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from services.etg_service import etg_service

def test_booking_workflow():
    print("🚀 Starting ETG Booking Workflow Integration Test")
    print("-" * 50)

    # 1. Get Hotel Page (HP) for Conrad LA
    print("\nStep 1: Calling /search/hp/ for Conrad Los Angeles...")
    hp_result = etg_service.get_hotel_page(
        hotel_id="conrad_los_angeles",
        checkin="2026-04-10",
        checkout="2026-04-11",
        guests=[{"adults": 2}],
        currency="USD",
        residency="us"
    )

    if not hp_result.get('success'):
        print(f"❌ Hotel Page request failed: {hp_result.get('error')}")
        return

    # Extract rates from the HP response
    hotels = hp_result['data'].get('data', {}).get('hotels', [])
    if not hotels:
        print("❌ No hotel data returned in HP response")
        return

    hotel = hotels[0]
    rates = hotel.get('rates', [])
    if not rates:
        print("❌ No rates found for this hotel in the Sandbox")
        return
        
    rate = rates[0]
    original_hash = rate.get('book_hash') or rate.get('hash')
    
    if not original_hash:
        print(f"❌ Rate found but no hash! Available keys: {list(rate.keys())}")
        return
        
    print(f"✅ Found hotel: {hotel.get('id')}")
    print(f"✅ Rate found. Original Hash: {original_hash[:20]}...")

    # 2. Prebook
    print("\nStep 2: Calling /hotel/prebook/...")
    prebook_result = etg_service.prebook(original_hash)
    
    if not prebook_result.get('success'):
        print(f"❌ Prebook failed: {prebook_result.get('error')}")
        print(f"Details: {prebook_result.get('response')}")
        return

    # ETG v3: The new hash is typically in data.data.hotels[0].rates[0].book_hash
    # but could also be in data.data.hash depending on the specific rate type
    inner_data = prebook_result['data'].get('data', {})
    new_hash = None
    
    if isinstance(inner_data, dict):
        new_hash = inner_data.get('hash')
        if not new_hash:
            hotels = inner_data.get('hotels', [])
            if hotels and isinstance(hotels, list):
                rates = hotels[0].get('rates', [])
                if rates and isinstance(rates, list):
                    new_hash = rates[0].get('book_hash') or rates[0].get('hash')

    if not new_hash:
        # Final fallback
        new_hash = prebook_result['data'].get('hash')
        
    if not new_hash:
        print("❌ Could not find new hash in prebook response")
        print(json.dumps(prebook_result, indent=2))
        return

    print(f"✅ Prebook successful. New Hash: {new_hash[:20]}...")
    
    if original_hash == new_hash:
        print("ℹ️ Note: Original hash and new hash are identical (common in some sandbox scenarios)")
    else:
        print("✅ Success: Hash has been updated by Prebook call!")

    # 3. Create Booking (Order Form)
    print("\nStep 3: Calling /hotel/order/booking/form/ (using NEW hash)...")
    partner_order_id = etg_service.generate_partner_order_id()
    create_result = etg_service.create_booking(
        book_hash=new_hash,
        partner_order_id=partner_order_id,
        guests=[{"first_name": "Test", "last_name": "User"}]
    )

    if not create_result.get('success'):
        print(f"❌ Create booking failed: {create_result.get('error')}")
        print(f"Details: {create_result.get('response')}")
        return

    print(f"✅ Booking form created. Partner Order ID: {partner_order_id}")

    # Extract amount and currency for finish_booking
    payment_options = rate.get('payment_options', {})
    payment_types = payment_options.get('payment_types', [])
    if not payment_types:
        print("❌ No payment types found in rate")
        return
        
    rate_amount = payment_types[0].get('amount')
    rate_currency = payment_types[0].get('currency_code')
    
    print(f"✅ Rate Price: {rate_amount} {rate_currency}")

    # 4. Finish Booking
    print("\nStep 4: Calling /hotel/order/booking/finish/...")
    finish_result = etg_service.finish_booking(
        partner_order_id=partner_order_id,
        email="test@example.com",
        phone="1234567890",
        guests=[{"first_name": "Test", "last_name": "User"}],
        amount=rate_amount,
        currency=rate_currency
    )

    if not finish_result.get('success'):
        print(f"❌ Finish booking failed: {finish_result.get('error')}")
        print(f"Details: {finish_result.get('response')}")
        return

    print(f"✅ Finish call initiated status: {finish_result['data'].get('status')}")

    # 5. Poll Status
    print("\nStep 5: Polling /hotel/order/booking/finish/status/...")
    attempts = 0
    max_attempts = 10
    confirmed = False

    while attempts < max_attempts:
        attempts += 1
        print(f"  Attempt {attempts}...")
        status_result = etg_service.check_booking_status(partner_order_id)
        print(f"  Debug Status Result: {json.dumps(status_result, indent=2)}")
        
        if not status_result.get('success'):
            print(f"  ❌ Status check failed: {status_result.get('error')}")
            break
            
        # ETG v3: The status is usually in the top-level of the data object
        etg_response = status_result.get('data', {})
        status = etg_response.get('status')
        
        # If it's not at the top level, check inside the 'data' field
        if not status and isinstance(etg_response.get('data'), dict):
            status = etg_response['data'].get('status')
        
        print(f"  Current Status: {status}")
        
        if status == 'ok':
            print("\n🎉 WORKFLOW COMPLETE: Booking confirmed in ETG Sandbox!")
            confirmed = True
            break
        elif status == 'error':
            error_msg = etg_response.get('error') or (etg_response.get('data', {}) if isinstance(etg_response.get('data'), dict) else None)
            print(f"  ❌ Booking failed with status error: {error_msg}")
            break
        elif status == 'processing':
            percent = etg_response.get('data', {}).get('percent', 0) if isinstance(etg_response.get('data'), dict) else '?'
            print(f"  Progress: {percent}%")
            
        time.sleep(5)

    if not confirmed:
        print("\n❌ Workflow did not reach confirmed status in time.")

if __name__ == "__main__":
    test_booking_workflow()
