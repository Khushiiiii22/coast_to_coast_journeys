from backend.routes.hotel_routes import process_etg_image_url

url = "https://cdn.worldota.net/t/1024x768/content/123.jpg"
print("Before:", url)
print("After:", process_etg_image_url(url))
