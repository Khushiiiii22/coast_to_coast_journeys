import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from config import Config
from services.supabase_service import SupabaseService
from supabase import create_client

db = SupabaseService()
# Force anon key for testing
db._client = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
db._is_healthy = True

data = {
    'partner_order_id': 'test_rpc_123',
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

res = db.create_booking(data)
print(res)
