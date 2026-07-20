import sys
sys.path.insert(0, '/Users/priyeshsrivastava/Travel production/coast_to_coast_journeys/backend')
from services.supabase_service import supabase_service

try:
    res = supabase_service.client.table('hotel_search_logs').select('*').limit(1).execute()
    print("Table exists!")
except Exception as e:
    print(f"Error: {e}")
