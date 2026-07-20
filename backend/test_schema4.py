from config import Config
from supabase import create_client

def test():
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
    try:
        q = supabase.table('hotel_bookings').select('*').limit(1).execute()
        if q.data:
            print("Columns:", list(q.data[0].keys()))
        else:
            print("Still no data in hotel_bookings")
    except Exception as e:
        print("ERROR:", e)

if __name__ == '__main__':
    test()
