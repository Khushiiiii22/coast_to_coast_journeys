
import os
import sys
import uuid

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from config import Config
from supabase import create_client

def test_insert():
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_ANON_KEY # Using Anon Key as currently patched
    
    print(f"URL: {url}")
    print("Testing INSERT with Anon Key...")
    
    try:
        client = create_client(url, key)
        
        # Dummy booking data matching schema (approx)
        dummy_data = {
            'id': str(uuid.uuid4()),
            'hotel_name': 'Test Hotel Debug',
            'partner_order_id': 'DEBUG-' + str(uuid.uuid4())[:8],
            'total_amount': 100,
            'currency': 'INR',
            'status': 'pending',
            'user_id': None # Anon user
            # Add other required fields if known, or let's hope this is enough
        }
        
        print(f"Attempting to insert: {dummy_data['partner_order_id']}")
        res = client.table('hotel_bookings').insert(dummy_data).execute()
        print("✅ INSERT SUCCESS!")
        print(res.data)
        
    except Exception as e:
        print(f"❌ INSERT FAILED: {e}")
        # Print full error details if available
        if hasattr(e, 'details'):
            print(f"Details: {e.details}")
        if hasattr(e, 'code'):
            print(f"Code: {e.code}")
            
if __name__ == "__main__":
    test_insert()
