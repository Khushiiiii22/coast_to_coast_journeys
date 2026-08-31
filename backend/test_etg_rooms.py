import asyncio
from services.etg_service import ETGApiService

async def main():
    service = ETGApiService()
    # Search for a hotel (e.g. Bellagio in Vegas)
    res = await service.search_by_hotels(
        hotel_ids=["test_hotel"], # Need a real ETG hotel id
        checkin="2026-09-01",
        checkout="2026-09-02",
        guests=[{"adults": 2}],
        currency="USD",
        residency="us"
    )
    print(res)

asyncio.run(main())
