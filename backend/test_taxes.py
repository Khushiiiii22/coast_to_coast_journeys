import requests, json
url = "https://api-sandbox.worldota.net/api/b2b/v3/search/serp/hotels/"
headers = {"Content-Type": "application/json", "Authorization": "Basic Mzk1OTpnZWQxN2RjNC1kOWIzLTQ2M2EtYmIxZi0yMzNjZWM3Yzg4OWU="}
payload = {
    "checkin": "2026-05-28", "checkout": "2026-05-30",
    "residency": "in", "language": "en", "guests": [{"adults": 2}],
    "ids": ["conrad_los_angeles"], "currency": "USD"
}
res = requests.post(url, json=payload, headers=headers).json()
if res.get("data") and res["data"].get("hotels"):
    rates = res["data"]["hotels"][0]["rates"]
    rate = rates[0]
    tax_data = {}
    payment_options = rate.get('payment_options', {})
    payment_types = payment_options.get('payment_types', [])
    if payment_types and isinstance(payment_types, list) and len(payment_types) > 0:
        tax_data = payment_types[0].get('tax_data', {})
    print("Found taxes in payment_types:", len(tax_data.get('taxes', [])))
else:
    print(res)
