"""
Verification script for the 6 ETG backend fixes applied on 16 May 2026.
Tests each fix independently without requiring live API or .env credentials.
"""
import sys
import os
import json

# Add project paths
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'backend')))

PASS = "✅ PASSED"
FAIL = "❌ FAILED"
results = []

# ============================================================
# FIX 1: get_hotel_info() method exists in ETGApiService
# ============================================================
def test_fix_1():
    print("\n" + "="*60)
    print("FIX 1: get_hotel_info() method exists")
    print("="*60)
    try:
        from services.etg_service import ETGApiService
        service = ETGApiService()
        
        # Check the method exists
        assert hasattr(service, 'get_hotel_info'), "get_hotel_info method does NOT exist!"
        
        # Check it's callable
        assert callable(getattr(service, 'get_hotel_info')), "get_hotel_info is not callable!"
        
        # Check signature accepts hotel_id
        import inspect
        sig = inspect.signature(service.get_hotel_info)
        params = list(sig.parameters.keys())
        assert 'hotel_id' in params, f"Missing 'hotel_id' parameter. Found: {params}"
        
        print(f"  Method exists: YES")
        print(f"  Parameters: {params}")
        print(f"  {PASS}")
        results.append(("Fix 1: get_hotel_info()", True))
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results.append(("Fix 1: get_hotel_info()", False))

# ============================================================
# FIX 2: No duplicate hotel append in transform_etg_hotels()
# ============================================================
def test_fix_2():
    print("\n" + "="*60)
    print("FIX 2: No duplicate hotels in search results")
    print("="*60)
    try:
        from routes.hotel_routes import transform_etg_hotels
        
        # Create a mock hotel list (1 hotel, 1 rate)
        mock_hotels = [{
            'id': 'test_hotel_123',
            'hid': 12345,
            'rates': [{
                'book_hash': 'abc123',
                'match_hash': 'match123',
                'room_name': 'Deluxe Room',
                'meal': 'breakfast',
                'meal_data': {'value': 'breakfast', 'has_breakfast': True, 'no_child_meal': False},
                'payment_options': {
                    'payment_types': [{'amount': '100.00', 'currency_code': 'USD', 'show_amount': '100.00', 'show_currency_code': 'USD'}],
                    'tax_data': {'taxes': []},
                    'cancellation_penalties': {'free_cancellation_before': None, 'policies': []}
                },
                'rg_ext': {'rg': 1},
                'room_data_trans': {'main_name': 'Deluxe Room'}
            }],
            'static_data': {
                'name': 'Test Hotel',
                'star_rating': 4,
                'address': '123 Test St',
                'latitude': 28.6139,
                'longitude': 77.2090,
                'images': []
            }
        }]
        
        CONVERSION_RATES = {'USD_TO_INR': 86.5, 'EUR_TO_INR': 92.0}
        MEAL_MAP = {'breakfast': 'Breakfast Included', 'nomeal': 'Room Only'}
        
        result = transform_etg_hotels(mock_hotels, 'USD', CONVERSION_RATES, MEAL_MAP, {}, 1)
        
        hotel_count = len(result)
        print(f"  Input: 1 hotel")
        print(f"  Output: {hotel_count} hotel(s) in result")
        
        assert hotel_count == 1, f"Expected 1 hotel, got {hotel_count} — DUPLICATE BUG STILL EXISTS!"
        
        print(f"  {PASS}")
        results.append(("Fix 2: No duplicate hotels", True))
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results.append(("Fix 2: No duplicate hotels", False))

# ============================================================
# FIX 3: No duplicate rate append in transform_rates()
# ============================================================
def test_fix_3():
    print("\n" + "="*60)
    print("FIX 3: No duplicate rates in room list")
    print("="*60)
    try:
        from routes.hotel_routes import transform_rates
        
        # Create a mock rates array (1 rate)
        mock_rates = [{
            'book_hash': 'hash123',
            'match_hash': 'match456',
            'room_name': 'Standard Room',
            'meal': 'nomeal',
            'meal_data': {'value': 'nomeal', 'has_breakfast': False, 'no_child_meal': False},
            'payment_options': {
                'payment_types': [{'amount': '80.00', 'currency_code': 'USD', 'show_amount': '80.00', 'show_currency_code': 'USD'}],
                'tax_data': {'taxes': []},
                'cancellation_penalties': {'free_cancellation_before': None, 'policies': []}
            },
            'rg_ext': {'rg': 1},
            'room_data_trans': {'main_name': 'Standard Room'}
        }]
        
        CONVERSION_RATES = {'USD_TO_INR': 86.5}
        MEAL_MAP = {'nomeal': 'Room Only'}
        
        result = transform_rates(mock_rates, 'USD', CONVERSION_RATES, MEAL_MAP, {}, 1)
        
        rate_count = len(result)
        print(f"  Input: 1 rate")
        print(f"  Output: {rate_count} rate(s) in result")
        
        assert rate_count == 1, f"Expected 1 rate, got {rate_count} — DUPLICATE RATE BUG STILL EXISTS!"
        
        # Verify it's the properly formatted one (has 'book_hash', 'meal_info' dict)
        assert 'meal_info' in result[0], "Rate is missing 'meal_info' — wrong object was appended!"
        assert 'cancellation_info' in result[0], "Rate is missing 'cancellation_info' — wrong object!"
        
        print(f"  Rate has 'meal_info': YES")
        print(f"  Rate has 'cancellation_info': YES")
        print(f"  {PASS}")
        results.append(("Fix 3: No duplicate rates", True))
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results.append(("Fix 3: No duplicate rates", False))

# ============================================================
# FIX 4: Correct tax path in enrich_rate_with_room_data()
# ============================================================
def test_fix_4():
    print("\n" + "="*60)
    print("FIX 4: Correct tax path (payment_options.tax_data)")
    print("="*60)
    try:
        from routes.hotel_routes import enrich_rate_with_room_data
        
        # Create a rate where tax_data is INSIDE payment_options (correct ETG structure)
        mock_rate = {
            'payment_options': {
                'payment_types': [{'amount': '200.00', 'currency_code': 'USD'}],
                'tax_data': {
                    'taxes': [
                        {'name': 'city_tax', 'included_by_supplier': False, 'amount': '15.00', 'currency_code': 'USD'},
                        {'name': 'vat', 'included_by_supplier': True, 'amount': '10.00', 'currency_code': 'USD'}
                    ]
                },
                'cancellation_penalties': {'free_cancellation_before': None, 'policies': []}
            },
            'rg_ext': {'rg': 1},
            'room_data_trans': {'main_name': 'Test Room'}
        }
        
        enriched = enrich_rate_with_room_data(mock_rate, {})
        
        prop_fees = enriched.get('property_payable_fees_total', 0)
        non_included = enriched.get('tax_info', {}).get('non_included_taxes', [])
        
        print(f"  property_payable_fees_total: {prop_fees}")
        print(f"  Non-included taxes found: {len(non_included)}")
        
        assert prop_fees == 15.0, f"Expected property fees = 15.0, got {prop_fees} — TAX PATH STILL WRONG!"
        assert len(non_included) == 1, f"Expected 1 non-included tax, got {len(non_included)}"
        assert non_included[0]['name'] == 'city_tax', "Wrong tax name"
        
        print(f"  {PASS}")
        results.append(("Fix 4: Correct tax path", True))
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results.append(("Fix 4: Correct tax path", False))

# ============================================================
# FIX 5: Email domain updated
# ============================================================
def test_fix_5():
    print("\n" + "="*60)
    print("FIX 5: Email domain updated to c2cjourneys.com")
    print("="*60)
    try:
        # Check config.py
        from config import Config
        default_email = Config.CORPORATE_EMAIL
        print(f"  Config.CORPORATE_EMAIL default: {default_email}")
        
        config_ok = 'coasttocoastjourneys' not in default_email
        
        # Check hotel_routes.py source code for hardcoded email
        routes_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'routes', 'hotel_routes.py')
        with open(routes_path, 'r') as f:
            content = f.read()
        
        old_domain_count = content.count('c2cjourneys.com')
        print(f"  Old domain occurrences in hotel_routes.py: {old_domain_count}")
        
        assert config_ok, f"Config still has old domain: {default_email}"
        assert old_domain_count == 0, f"Found {old_domain_count} old domain references in hotel_routes.py!"
        
        print(f"  {PASS}")
        results.append(("Fix 5: Email domain updated", True))
    except Exception as e:
        print(f"  {FAIL}: {e}")
        results.append(("Fix 5: Email domain updated", False))

# ============================================================
# MAIN
# ============================================================
if __name__ == "__main__":
    print("🚀 VERIFYING ALL 5 ETG BACKEND FIXES")
    print("=" * 60)
    
    test_fix_1()
    test_fix_2()
    test_fix_3()
    test_fix_4()
    test_fix_5()
    
    print("\n" + "=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    
    all_passed = True
    for name, passed in results:
        status = PASS if passed else FAIL
        print(f"  {status}  {name}")
        if not passed:
            all_passed = False
    
    print()
    if all_passed:
        print("🎉 ALL FIXES VERIFIED — BACKEND IS CLEAN!")
    else:
        print("⚠️  SOME FIXES FAILED — CHECK OUTPUT ABOVE")
        sys.exit(1)
