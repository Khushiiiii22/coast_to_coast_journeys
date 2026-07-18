from backend.app import app
from flask import current_app
with app.app_context():
    supabase = current_app.config.get('SUPABASE')
    try:
        res = supabase.table('system_settings').select('*').limit(1).execute()
        print("Success:", res)
    except Exception as e:
        print("Error:", e)
