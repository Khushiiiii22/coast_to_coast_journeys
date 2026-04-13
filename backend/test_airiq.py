import requests
import json
import os

BASE_URL = "https://omairiq.azurewebsites.net"
LOGIN_ID = "9555202202"
PASSWORD = "112233344"
API_KEY = "NTMzNDUwMDpBSVJJUSBURVNUIEFQSToxODkxOTMwMDM1OTk2OlBvTjE2NGNkLy9heE53WC9hM00rS1ZrcnJSa2Q0S05adHl3Q0NHZmU4Uzg9"

def test_login():
    url = f"{BASE_URL}/login"
    payload = {
        "Username": LOGIN_ID,
        "Password": PASSWORD
    }
    headers = {
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    
    print(f"Testing Login API: {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.ok:
            data = response.json()
            token = data.get("token")
            return token
    except Exception as e:
        print(f"Error testing login: {e}")
    return None

def test_search(token):
    if not token:
        print("No token provided, skipping search")
        return
        
    url = f"{BASE_URL}/search"
    payload = {
        "origin": "AMD",
        "destination": "BOM",
        "departure_date": "2026/05/17",
        "adult": 1,
        "child": 0,
        "infant": 0
    }
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    
    print(f"\\nTesting Search API: {url}")
    print(f"Payload: {payload}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        print(f"Status Code: {response.status_code}")
        if response.text:
            data = response.json()
            if isinstance(data, dict) and 'data' in data and data['data']:
                flight_data = data['data']
                if isinstance(flight_data, list) and len(flight_data) > 0:
                     print(f"Successfully retrieved {len(flight_data)} flight options (showing first option):")
                     print(json.dumps(flight_data[0], indent=2))
                else:
                    print("Response JSON:", json.dumps(data, indent=2))
            else:
                 print("Response JSON:", json.dumps(data, indent=2))
    except Exception as e:
        print(f"Error testing search: {e}")

def test_availability(token):
    if not token: return
    url = f"{BASE_URL}/availability"
    payload = {
        "origin": "AMD",
        "destination": "BOM"
    }
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "api-key": API_KEY
    }
    print(f"\\nTesting Availability API: {url}")
    try:
        response = requests.post(url, json=payload, headers=headers, timeout=15)
        if response.text:
            print("Response:", json.dumps(response.json(), indent=2))
    except Exception as e:
        print(f"Error testing availability: {e}")

if __name__ == "__main__":
    token = test_login()
    test_availability(token)
    test_search(token)

