import sys
import os

# Add backend dir to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

def test_policy_formatting():
    from routes.hotel_routes import format_hotel_policies
    
    # Simulated payload for Hotel 10004834 based on ETG audit feedback
    # Specifically testing:
    # 1. pets with price/currency (metapolicy_struct)
    # 2. Raw string in metapolicy_extra_info
    dummy_data = {
        'metapolicy_struct': {
            'pets': {
                'allowed': True,
                'price': '50',
                'currency': 'USD',
                'type': 'dogs_only'
            },
            'internet': [
                {'type': 'wifi', 'inclusion': 'surcharge', 'price': '10', 'currency': 'USD', 'price_unit': 'per_day'}
            ]
        },
        'metapolicy_extra_info': "This is a critical important information string that the auditor said was missing."
    }
    
    formatted = format_hotel_policies(dummy_data)
    
    print("--- PET POLICIES ---")
    for p in formatted.get('pets', []):
        print(f"[{p.get('label')}]: {p.get('value')}")
        
    print("\n--- INTERNET POLICIES ---")
    for i in formatted.get('internet', []):
        print(f"[{i.get('label')}]: {i.get('value')}")
        
    print("\n--- SPECIAL/EXTRA INFO ---")
    for s in formatted.get('special', []):
        print(f"[{s.get('label')}]: {s.get('value')}")

    # Assertions to ensure logic is correct
    pet_vals = [p['value'] for p in formatted.get('pets', [])]
    assert any("50 USD" in v for v in pet_vals), "Pet fee 50 USD not found in formatted results"
    
    special_vals = [s['value'] for s in formatted.get('special', [])]
    assert dummy_data['metapolicy_extra_info'] in special_vals, "Extra info string not found in formatted results"

    print("\n✅ ALL POLICY TESTS PASSED!")

if __name__ == "__main__":
    test_policy_formatting()
