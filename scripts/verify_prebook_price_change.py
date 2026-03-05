import sys
import os
import json
from unittest.mock import MagicMock, patch

# Add backend dir to path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

def test_prebook_price_change():
    from app import create_app
    app = create_app()
    client = app.test_client()
    
    # Mocking etg_service.prebook to return a price_changed response
    # This simulates the ETG API behavior described by the auditor
    with patch('routes.hotel_routes.etg_service.prebook') as mock_prebook:
        mock_prebook.return_value = {
            'success': True,
            'data': {
                'data': {
                    'price_changed': True,
                    'payment_options': {
                        'payment_types': [{'amount': '105.00'}],
                        'currency_code': 'USD'
                    }
                }
            }
        }
        
        response = client.post('/api/hotels/prebook', 
                              data=json.dumps({'book_hash': 'test_hash_123', 'price_increase_percent': 5}),
                              content_type='application/json')
        
        data = json.loads(response.data)
        
        print("--- PREBOOK PRICE CHANGE RESPONSE ---")
        print(json.dumps(data, indent=2))
        
        # Assertions
        assert data['price_changed'] is True, "price_changed flag missing from API response"
        assert data['new_total'] == 105.0, "Updated total (105.0) not found in response"
        assert data['new_currency'] == 'USD', "Currency code not found in response"

    print("\n✅ PREBOOK PRICE CHANGE LOGIC VERIFIED!")

if __name__ == "__main__":
    test_prebook_price_change()
