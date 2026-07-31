import sys
import os
sys.path.insert(0, os.path.abspath('backend'))
from services.etg_service import ETGApiService
from config import Config

def test():
    service = ETGApiService()
    print("1. Testing Suggest for 'Los Angeles'")
    res = service.suggest('Los Angeles')
    print("Suggest response:", res)

    if res.get('success') and res.get('data') and res['data'].get('data'):
        regions = res['data']['data'].get('regions', [])
        if regions:
            region_id = regions[0]['id']
            print(f"Got region_id: {region_id}")
            
            print(f"\n2. Testing Search for region_id {region_id}")
            guests = [{'adults': 2, 'children': []}]
            search_res = service.search_by_region(region_id, "2026-08-01", "2026-08-05", guests, "USD")
            
            if search_res.get('success'):
                hotels = search_res.get('hotels', [])
                print(f"Success! Found {len(hotels)} hotels in Los Angeles")
            else:
                print("Search failed:", search_res)
        else:
            print("No regions found in suggest response")

if __name__ == '__main__':
    test()
