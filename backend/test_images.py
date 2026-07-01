import sys, json
sys.path.append('/Users/priyeshsrivastava/Travel production/backend')
from services.etg_service import ETGService
etg = ETGService()
response = etg.search_by_hotels(
    checkin="2026-05-28", 
    checkout="2026-05-30", 
    guests=[{"adults": 2, "children": []}], 
    hotel_ids=["conrad_los_angeles"]
)
if response.get("success"):
    rates = response["data"]["data"]["hotels"][0]["rates"]
    for r in rates[:3]:
        print(r.get("room_name"))
        print(len(r.get("room_data_trans", {}).get("images", [])))
