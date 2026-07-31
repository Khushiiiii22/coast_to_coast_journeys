import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.services.etg_service import ETGApiService
import json

etg = ETGApiService()
# Taj Mahal New Delhi hotel ID is usually 'hotel_id' format. We can just test any string, if it's unauthorized it will say 403.
res = etg._make_request("/hotel/info/", {"id": "test"})
print("INFO:", res.get("status_code"), res.get("error"))

res2 = etg._make_request("/search/multicomplete/", {"query": "texas", "language": "en"})
print("SUGGEST:", res2.get("status_code"), res2.get("error"))
