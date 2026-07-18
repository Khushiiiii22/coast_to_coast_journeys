import json
from services.etg_service import etg_service

def test():
    # Force bypass cache
    res = etg_service.search_by_region(
        region_id=6308862, # Mumbai
        checkin="2026-07-21",
        checkout="2026-07-22",
        rooms=[{"adults": 2, "children": []}],
        currency="USD",
        residency="in"
    )
    print("RES:")
    print(json.dumps(res, indent=2))

if __name__ == '__main__':
    test()
