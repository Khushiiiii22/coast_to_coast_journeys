import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))
from services.etg_service import ETGApiService
import asyncio

async def test():
    svc = ETGApiService()
    res = svc.get_hotel_info("test_hotel")
    print(res)

asyncio.run(test())
