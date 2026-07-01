import sys
import os
sys.path.append('/Users/priyeshsrivastava/Travel production/backend')
from services.etg_service import etg_service
import json

result = etg_service.search_by_hotels(
    hotel_ids=["conrad_los_angeles"],
    checkin="2026-05-28",
    checkout="2026-05-30",
    guests=[{"adults": 2, "children": [4]}],
    currency="USD"
)
print(json.dumps(result, indent=2))
