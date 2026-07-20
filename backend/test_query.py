from config import Config
from supabase import create_client

def test():
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_ANON_KEY)
    try:
        q = supabase.table('hotel_bookings').select('*').not_.is_('razorpay_payment_id', 'null').limit(1).execute()
        print("Success! data length:", len(q.data))
    except Exception as e:
        print("ERROR:", e)

if __name__ == '__main__':
    test()
