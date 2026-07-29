import sys
sys.path.append('/Users/khushi22/coasttocoast/backend')
from routes.hotel_routes import process_etg_image_url

url = "https://cdn.worldota.net/t/{size}/content/c0/de/c0dea9e5760f33c2b101ed14577e168b3f36c74f.jpeg"
print("Result:", process_etg_image_url(url))
