import os
import sys
from dotenv import load_dotenv

load_dotenv()
sys.path.append(os.path.abspath('backend'))
from config import Config
from supabase import create_client

client = create_client(Config.SUPABASE_URL, Config.SUPABASE_SERVICE_ROLE_KEY)
# We can execute raw SQL using the RPC method if available, or just use postgres connection.
# Actually, I can just use the Supabase MCP to execute SQL!
