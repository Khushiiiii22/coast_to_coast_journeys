from config import Config
from supabase import create_client
import requests

def test():
    # Use postgrest api directly to get swagger schema
    r = requests.get(Config.SUPABASE_URL + '/rest/v1/', headers={'apikey': Config.SUPABASE_ANON_KEY})
    if r.status_code == 200:
        schema = r.json()
        print("Hotel Bookings columns:")
        print(schema['definitions']['hotel_bookings']['properties'].keys())
    else:
        print("Error fetching schema")

if __name__ == '__main__':
    test()
