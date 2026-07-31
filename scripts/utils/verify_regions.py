import requests, base64, json

key_id = "17793"
key_secret = "5e5559f1-be7d-4757-8d39-0fb48f5bf054"
base_url = "https://api.ratehawk.com/api/b2b/v3"

auth_string = f"{key_id}:{key_secret}"
b64_auth = base64.b64encode(auth_string.encode()).decode()
headers = {
    'Authorization': f'Basic {b64_auth}',
    'Content-Type': 'application/json'
}

cities = ["Mumbai", "Los Angeles", "Delhi", "Goa", "Dubai", "Paris", "Bangalore", "Jaipur"]

for city in cities:
    try:
        resp = requests.post(f"{base_url}/search/multicomplete/", headers=headers, json={"query": city, "language": "en"}, timeout=10)
        data = resp.json()
        if data.get('data') and data['data'].get('regions'):
            region = data['data']['regions'][0]
            print(f"✅ {city}: region_id={region.get('id')}, name={region.get('name')}, country={region.get('country')}")
        else:
            print(f"❌ {city}: No regions returned. Full response: {json.dumps(data)[:200]}")
    except Exception as e:
        print(f"❌ {city}: Error - {e}")
