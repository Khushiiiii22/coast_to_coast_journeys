import sys
import os
import json

sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'backend'))

try:
    from services.etg_service import etg_service
except Exception as e:
    print(e)
    sys.exit(1)

res = etg_service.get_hotel_static('10004834')
if not res.get('success'):
    print(res)
    sys.exit(1)

print(json.dumps(res, indent=2))
