import os
import sys
import json

backend_dir = os.path.dirname(os.path.abspath(__file__))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

from dotenv import load_dotenv
load_dotenv(os.path.join(backend_dir, '.env'))

from services.etg_service import etg_service

def test_diagnostics():
    print("🔍 Diagnostic Query for Conrad Los Angeles")
    hp_result = etg_service.get_hotel_page(
        hotel_id="conrad_los_angeles",
        checkin="2026-05-28",
        checkout="2026-06-02",
        guests=[{"adults": 2, "children": [8]}],
        currency="USD"
    )
    if not hp_result.get('success'):
        print(f"❌ HP Request Failed: {hp_result.get('error')}")
        return

    hotels = hp_result['data'].get('data', {}).get('hotels', [])
    if not hotels:
        print("❌ No hotels found")
        return

    rates = hotels[0].get('rates', [])
    print(f"Total rates found: {len(rates)}")
    for idx, rate in enumerate(rates[:3]):
        print(f"\nRate #{idx+1}:")
        print(f"  Room Name: {rate.get('room_name')}")
        print(f"  Match Hash: {rate.get('match_hash')}")
        print(f"  Book Hash: {rate.get('book_hash')}")
        print(f"  Search Hash: {rate.get('search_hash')}")
        print(f"  Available keys: {list(rate.keys())}")

if __name__ == "__main__":
    test_diagnostics()
