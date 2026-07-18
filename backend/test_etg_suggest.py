import sys
import os

# Add backend to path
sys.path.append('/Users/priyeshsrivastava/Travel production/backend')

from services.etg_service import etg_service

result = etg_service.suggest("Conrad Los Angeles")
import json
print(json.dumps(result, indent=2))
