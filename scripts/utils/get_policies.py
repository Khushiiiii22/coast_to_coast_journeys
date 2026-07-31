import os
from dotenv import load_dotenv
load_dotenv()
from supabase import create_client

client = create_client(os.getenv('SUPABASE_URL'), os.getenv('SUPABASE_SERVICE_ROLE_KEY'))
res = client.rpc('get_policies', {}).execute()
print(res)
