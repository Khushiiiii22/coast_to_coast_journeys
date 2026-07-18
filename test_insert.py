import sys
import os
sys.path.append('backend')
from services.supabase_service import supabase_service

test_booking = {
    'partner_order_id': 'TEST-RLS-12345',
    'hotel_id': 'test',
    'hotel_name': 'test',
    'total_amount': 0,
    'status': 'created'
}

print("Executing insert...")
res = supabase_service.create_booking(test_booking)
print("Result:", res)
