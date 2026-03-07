import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

try:
    from routes.hotel_routes import format_hotel_policies
except Exception as e:
    print(e)
    sys.exit(1)

# Dummy payload matching ETG structure from the screenshot
policies = {
    'metapolicy_extra_info': 'SANDBOX DEMO PROPERTY (no real bookings).\\nThere may be maintenance work around the property; some noise is possible from 08:30 AM to 09:00 PM. The property makes every effort to minimize delays and noise, and apologizes in advance for any inconvenience.',
    'metapolicy_struct': {
        'internet': [
            {
                'internet_type': 'wifi',
                'work_area': 'public_areas',
                'included_in_price': True
            }
        ],
        'pets': [
            {
                'pets_allowed': True,
                'price': '50',
                'currency': 'USD',
                'type': 'dogs_only'
            }
        ],
        'parking': [
            {
                'inclusion': 'not_included',
                'price': '20',
                'currency': 'USD',
                'price_unit': 'per_day'
            }
        ]
    }
}

print("=== EXPECTED UI OUTPUT ===")
print(json.dumps(format_hotel_policies(policies), indent=2))
