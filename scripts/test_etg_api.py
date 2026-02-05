#!/usr/bin/env python3
"""
Test ETG/RateHawk API Connection
Verifies that search and booking requests are being sent with key_id: 83
"""
import os
import sys

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'backend'))

from dotenv import load_dotenv
load_dotenv()

# Check credentials
print("=" * 60)
print("ETG/RateHawk API Configuration Check")
print("=" * 60)

key_id = os.getenv('ETG_API_KEY_ID')
key_secret = os.getenv('ETG_API_KEY_SECRET')
base_url = os.getenv('ETG_API_BASE_URL')

print(f"API Key ID: {key_id}")
print(f"API Secret: {'*' * 8 + key_secret[-8:] if key_secret else 'NOT SET'}")
print(f"Base URL: {base_url}")
print("=" * 60)

if key_id != '83':
    print(f"⚠️ WARNING: Key ID is '{key_id}' but expected '83'")
else:
    print("✅ Key ID is correctly set to 83")

# Test API connection
print("\n📡 Testing API Connection...")

from services.etg_service import etg_service

# Test suggest API (simple endpoint)
print("\n🔍 Testing Suggest API with 'Paris'...")
result = etg_service.suggest("Paris")

if result.get('success'):
    print("✅ API Connection Successful!")
    data = result.get('data', {})
    if isinstance(data, dict) and data.get('data'):
        regions = data['data'].get('regions', [])
        print(f"   Found {len(regions)} regions")
        if regions:
            print(f"   First region: {regions[0].get('name', 'N/A')}")
else:
    print(f"❌ API Error: {result.get('error', 'Unknown error')}")
    print(f"   Status Code: {result.get('status_code', 'N/A')}")

# Test search by region (Paris)
print("\n🏨 Testing Search by Region (Paris - 2734)...")
from datetime import datetime, timedelta

checkin = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
checkout = (datetime.now() + timedelta(days=10)).strftime('%Y-%m-%d')

guests = etg_service.format_guests_for_search(adults=2)
search_result = etg_service.search_by_region(
    region_id=2734,  # Paris
    checkin=checkin,
    checkout=checkout,
    guests=guests,
    currency='USD',
    residency='gb'
)

if search_result.get('success'):
    print("✅ Search API Working!")
    data = search_result.get('data', {})
    if isinstance(data, dict):
        inner_data = data.get('data', data)
        hotels = inner_data.get('hotels', [])
        print(f"   Found {len(hotels)} hotels in Paris")
else:
    print(f"❌ Search API Error: {search_result.get('error', 'Unknown error')}")
    print(f"   Status Code: {search_result.get('status_code', 'N/A')}")
    if search_result.get('response'):
        print(f"   Response: {search_result.get('response')}")

print("\n" + "=" * 60)
print("API Test Complete")
print("=" * 60)
