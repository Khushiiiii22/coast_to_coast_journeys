from config import Config
from supabase import create_client

def test():
    supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
    try:
        q = supabase.table('payments').select('*').limit(1).execute()
        if q.data:
            print("Columns:", list(q.data[0].keys()))
        else:
            supabase.table('payments').insert({'status': 'test'}).execute()
            q = supabase.table('payments').select('*').limit(1).execute()
            print("Columns:", list(q.data[0].keys()))
            supabase.table('payments').delete().eq('status', 'test').execute()
    except Exception as e:
        print("ERROR:", e)

if __name__ == '__main__':
    test()
