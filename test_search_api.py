import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.services.etg_service import ETGApiService
import json

etg = ETGApiService()
res = etg._make_request("/search/serp/region/", {
  "checkin": "2026-07-22",
  "checkout": "2026-07-23",
  "residency": "gb",
  "language": "en",
  "guests": [{"adults": 2, "children": []}],
  "region_id": 6308838, # New Delhi
  "currency": "USD"
})
print("SEARCH:", res.get("status_code"), res.get("error"))
