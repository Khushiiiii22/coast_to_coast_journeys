import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from config import Config
from supabase import create_client

print(f"URL: {Config.SUPABASE_URL}")
print(f"Key ends with: {Config.SUPABASE_SERVICE_ROLE_KEY[-5:]}")

client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
# Try to insert a dummy row without user_id
data = {
    'partner_order_id': 'test_RLS_bypass_123',
    'hotel_id': 'test_hotel',
    'check_in': '2027-01-01',
    'check_out': '2027-01-02',
    'guests': [],
}
try:
    res = client.table('hotel_bookings').insert(data).execute()
    print("Insert success:", res.data)
except Exception as e:
    print("Insert failed:", str(e))
    
# Try to delete it
try:
    client.table('hotel_bookings').delete().eq('partner_order_id', 'test_RLS_bypass_123').execute()
except:
    pass
