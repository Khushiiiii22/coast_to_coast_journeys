import sys
import json
sys.path.append('/Users/priyeshsrivastava/Travel production/backend')
from routes.hotel_routes import transform_etg_hotels
import requests

url = "https://api-sandbox.worldota.net/api/b2b/v3/search/serp/hotels/"
headers = {"Content-Type": "application/json", "Authorization": "Basic Mzk1OTpnZWQxN2RjNC1kOWIzLTQ2M2EtYmIxZi0yMzNjZWM3Yzg4OWU="}
payload = {
    "checkin": "2026-05-28", "checkout": "2026-05-30",
    "residency": "in", "language": "en", "guests": [{"adults": 2}],
    "ids": ["conrad_los_angeles"], "currency": "USD"
}
# Since we don't have the real API key, we can use the cached response or mock it
