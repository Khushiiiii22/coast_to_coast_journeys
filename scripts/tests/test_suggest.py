import sys
import os
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from backend.services.etg_service import ETGApiService
import json

etg_service = ETGApiService()
res = etg_service.suggest("Conrad Los Angeles")
print(json.dumps(res, indent=2))
