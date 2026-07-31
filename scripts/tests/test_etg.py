import os
import requests
import base64

key_id = "17793"
key_secret = "5e5559f1-be7d-4757-8d39-0fb48f5bf054"
base_url = "https://api.worldota.net/api/b2b/v3"

auth_string = f"{key_id}:{key_secret}"
b64_auth = base64.b64encode(auth_string.encode()).decode()

headers = {
    'Authorization': f'Basic {b64_auth}',
    'Content-Type': 'application/json'
}

response = requests.post(f"{base_url}/search/multicomplete/", headers=headers, json={"query": "London", "language": "en"})
print(response.status_code)
print(response.json())
