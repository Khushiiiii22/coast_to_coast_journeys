import os
import sys
# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from services.supabase_service import SupabaseService
supabase = SupabaseService()
try:
    response = supabase.client.table('admin_users').select('*').execute()
    print("Admin Users:", response.data)
except Exception as e:
    print("Error:", e)
