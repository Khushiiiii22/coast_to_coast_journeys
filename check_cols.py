import sys
import os
sys.path.append('backend')
from services.supabase_service import supabase_service

try:
    res = supabase_service.client.table('hotel_bookings').select('hotel_address, hotel_city').limit(1).execute()
    print("Columns exist:", res)
except Exception as e:
    print("Error:", e)
