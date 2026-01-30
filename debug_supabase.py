
import os
import sys

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from config import Config
try:
    import supabase
    print(f"Supabase version: {supabase.__version__ if hasattr(supabase, '__version__') else 'unknown'}")
    from supabase import create_client, Client
    print("Imported create_client and Client")
    
    url = Config.SUPABASE_URL
    key = Config.SUPABASE_ANON_KEY
    
    print(f"URL: {url}")
    print(f"Key: {key[:5]}..." if key else "Key: None")
    
    print("Attempting to create client...")
    client = create_client(url, key)
    print("Client created successfully!")
    
    # Check hotel_bookings table
    print("Checking hotel_bookings table...")
    try:
        res = client.table('hotel_bookings').select('*').limit(1).execute()
        print(f"Table check success. Rows: {len(res.data)}")
    except Exception as table_err:
        print(f"Table check failed: {table_err}")

    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
