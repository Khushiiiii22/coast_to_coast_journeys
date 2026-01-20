"""
HotelBeds API Service
Handles HotelBeds API authentication and requests
"""
import hashlib
import time
import requests
from datetime import datetime

class HotelBedsAPI:
    def __init__(self, api_key, secret, environment='test'):
        """
        Initialize HotelBeds API client
        
        Args:
            api_key: Your API key
            secret: Your API secret
            environment: 'test' or 'live'
        """
        self.api_key = api_key
        self.secret = secret
        
        # Base URLs
        if environment == 'test':
            self.base_url = "https://api.test.hotelbeds.com"
        else:
            self.base_url = "https://api.hotelbeds.com"
    
    def generate_signature(self):
        """
        Generate X-Signature header
        Formula: SHA256(ApiKey + Secret + UnixTimestamp)
        
        Returns:
            tuple: (signature, timestamp)
        """
        # Get current Unix timestamp (in seconds)
        timestamp = str(int(time.time()))
        
        # Concatenate: ApiKey + Secret + Timestamp
        signature_string = self.api_key + self.secret + timestamp
        
        # Generate SHA256 hash
        signature = hashlib.sha256(signature_string.encode('utf-8')).hexdigest()
        
        return signature, timestamp
    
    def _get_headers(self):
        """Get request headers with authentication"""
        signature, timestamp = self.generate_signature()
        
        return {
            'Api-Key': self.api_key,
            'X-Signature': signature,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
            'Accept-Encoding': 'gzip'
        }
    
    def search_hotels(self, destination_code, checkin, checkout, rooms=1, adults=2, children=0):
        """
        Search for hotels
        
        Args:
            destination_code: Destination code (e.g., 'PMI' for Palma de Mallorca)
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            rooms: Number of rooms
            adults: Number of adults
            children: Number of children
        
        Returns:
            dict: API response
        """
        url = f"{self.base_url}/hotel-api/1.0/hotels"
        
        payload = {
            "stay": {
                "checkIn": checkin,
                "checkOut": checkout
            },
            "occupancies": [
                {
                    "rooms": rooms,
                    "adults": adults,
                    "children": children
                }
            ],
            "destination": {
                "code": destination_code
            }
        }
        
        try:
            response = requests.post(
                url,
                headers=self._get_headers(),
                json=payload,
                timeout=30
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_hotel_details(self, hotel_code, language='ENG'):
        """
        Get hotel details
        
        Args:
            hotel_code: Hotel code
            language: Language code (ENG, SPA, etc.)
        
        Returns:
            dict: Hotel details
        """
        url = f"{self.base_url}/hotel-content-api/1.0/hotels/{hotel_code}/details"
        
        try:
            response = requests.get(
                url,
                headers=self._get_headers(),
                params={'language': language},
                timeout=30
            )
            
            return {
                'success': response.status_code == 200,
                'status_code': response.status_code,
                'data': response.json() if response.status_code == 200 else None,
                'error': response.text if response.status_code != 200 else None
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def test_connection(self):
        """
        Test API connection with a simple status check
        
        Returns:
            dict: Connection test result
        """
        # Test with a simple hotel availability search (Palma de Mallorca)
        # Using dates far in the future to avoid availability issues
        checkin = datetime.now().strftime('%Y-%m-%d')
        from datetime import timedelta
        checkout = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        result = self.search_hotels(
            destination_code='PMI',  # Palma de Mallorca
            checkin=checkin,
            checkout=checkout,
            rooms=1,
            adults=2
        )
        
        return result


# Example usage and testing
if __name__ == "__main__":
    print("🧪 Testing HotelBeds API Credentials\n")
    
    # All 3 API key sets
    credentials = [
        {
            'name': 'API Key #1 (High Quota)',
            'api_key': 'c79416829cc345633d1de38a1d968173',
            'secret': '07207637d1'
        },
        {
            'name': 'API Key #2 (Fast Rate)',
            'api_key': 'da6cfe9d8f23fe4589b3139ffadba034',
            'secret': 'c06b649871'
        },
        {
            'name': 'API Key #3 (Low Quota)',
            'api_key': 'd51bdc80bdf8f8e610882e137baa4bad',
            'secret': '3c297e5613'
        }
    ]
    
    for cred in credentials:
        print(f"Testing {cred['name']}...")
        print(f"API Key: {cred['api_key'][:20]}...")
        
        api = HotelBedsAPI(cred['api_key'], cred['secret'])
        
        # Generate signature to show how it works
        sig, ts = api.generate_signature()
        print(f"✓ Generated Signature: {sig[:40]}...")
        print(f"✓ Timestamp: {ts}")
        
        # Test connection
        result = api.test_connection()
        
        if result['success']:
            print(f"✅ Status: WORKING")
            hotels_count = len(result['data'].get('hotels', {}).get('hotels', [])) if result.get('data') else 0
            print(f"✓ Hotels Found: {hotels_count}")
        else:
            print(f"❌ Status: FAILED")
            print(f"✗ Error: {result.get('error', 'Unknown error')[:100]}")
        
        print("-" * 60)
        print()
