import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from config import Config
from supabase import create_client

client_anon = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
client_admin = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)

data = {
    'partner_order_id': 'test_rollback_123',
    'hotel_id': 'test',
    'hotel_name': 'Test',
    'check_in': '2027-01-01',
    'check_out': '2027-01-02',
    'rooms': 1,
    'guests': [],
    'total_amount': 100,
    'currency': 'USD',
    'status': 'created'
}

try:
    client_anon.table('hotel_bookings').insert(data).execute()
except Exception as e:
    print("Anon insert failed:", str(e))

res = client_admin.table('hotel_bookings').select('*').eq('partner_order_id', 'test_rollback_123').execute()
print("Rows found:", len(res.data))
