import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from config import Config
from supabase import create_client

client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
data = {
    'partner_order_id': 'test_str_null_123',
    'hotel_id': 'test',
    'hotel_name': 'Test',
    'check_in': '2027-01-01',
    'check_out': '2027-01-02',
    'rooms': 1,
    'guests': [],
    'user_id': 'null',
    'total_amount': 100,
    'currency': 'USD',
    'status': 'created'
}
try:
    res = client.table('hotel_bookings').insert(data).execute()
    print("insert success:", res.data)
except Exception as e:
    print("insert failed:", str(e))
