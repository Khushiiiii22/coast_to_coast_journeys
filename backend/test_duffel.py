import os
from duffel_api import Duffel

access_token = os.getenv('DUFFEL_ACCESS_TOKEN')

client = Duffel(access_token=access_token, api_version="v2")
try:
    offer_request = client.offer_requests.create() \
        .slices([{"origin": "LHR", "destination": "JFK", "departure_date": "2026-06-15"}]) \
        .passengers([{"type": "adult"}]) \
        .cabin_class("economy") \
        .execute()
    print("Success:", offer_request.id)
except Exception as e:
    print(f"Error: {e}")
