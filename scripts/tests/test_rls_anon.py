import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from config import Config
from supabase import create_client

client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
data = {
    'partner_order_id': 'test_anon_rls_123',
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
try:
    res = client.table('hotel_bookings').insert(data).execute()
    print("Anon insert success:", res.data)
except Exception as e:
    print("Anon insert failed:", str(e))
