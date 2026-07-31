import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from services.supabase_service import SupabaseService

db = SupabaseService()
data = {
    'partner_order_id': 'test_mobile_rls_123',
    'user_id': None,  # Empty string as might be sent from mobile
    'hotel_id': 'test_hotel',
    'hotel_name': 'Test Hotel',
    'check_in': '2027-01-01',
    'check_out': '2027-01-02',
    'rooms': 1,
    'guests': [],
    'customer_email': 'test@test.com',
    'customer_phone': '1234567890',
    'total_amount': 100.0,
    'currency': 'USD',
    'status': 'created'
}

res = db.create_booking(data)
print(res)
