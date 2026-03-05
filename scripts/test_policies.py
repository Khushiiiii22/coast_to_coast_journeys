import sys
import os

# Add backend dir to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

def test_policy_logic():
    from routes.hotel_routes import format_hotel_policies
    
    # Test case 1: Parking with text and price
    dummy_policies = {
        'metapolicy_struct': {
            'parking': [
                {
                    'text': 'Private parking available on site',
                    'price': '30.00',
                    'currency': 'EUR',
                    'type': 'garage'
                }
            ],
            'pets': {
                'allowed': True,
                'price': '25',
                'currency': 'USD',
                'type': 'only_dogs'
            }
        }
    }
    
    formatted = format_hotel_policies(dummy_policies)
    
    print("--- PARKING ---")
    for item in formatted['parking']:
        print(f"Value: {item['value']}")
        
    print("\n--- PETS ---")
    for item in formatted['pets']:
        print(f"Label: {item['label']}, Value: {item['value']}")

    # Test case 2: Parking with different keys
    dummy_policies_2 = {
        'metapolicy_struct': {
            'parking': [
                {
                    'description': 'Public parking nearby',
                    'fee': '15',
                    'currency': 'GBP'
                }
            ],
            'pets': [
                {
                    'pets_allowed': True,
                    'amount': '20',
                    'currency_code': 'EUR'
                }
            ]
        }
    }
    
    formatted_2 = format_hotel_policies(dummy_policies_2)
    print("\n--- TEST CASE 2 ---")
    print("--- PARKING 2 ---")
    for item in formatted_2['parking']:
        print(f"Value: {item['value']}")
    print("\n--- PETS 2 ---")
    for item in formatted_2['pets']:
        print(f"Label: {item['label']}, Value: {item['value']}")

if __name__ == "__main__":
    test_policy_logic()
