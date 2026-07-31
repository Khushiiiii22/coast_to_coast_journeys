import sys
import os
sys.path.append('backend')
from services.supabase_service import supabase_service
import json

booking = supabase_service.get_booking_by_partner_order_id('CTC-20260714144940-56C9DE27')
print(type(booking))
print(booking.keys())
print(type(booking.get('data')))
