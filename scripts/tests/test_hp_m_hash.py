import sys
import json
import os
from dotenv import load_dotenv

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from backend.services.etg_service import ETGApiService

load_dotenv()
etg = ETGApiService()
res = etg.get_hotel_page(
    hotel_id="8473727",
    checkin="2026-06-15",
    checkout="2026-06-16",
    guests=[{"adults": 2, "children": []}],
    currency="USD"
)

if res.get('success'):
    print(json.dumps(res, indent=2))
else:
    print(res)
