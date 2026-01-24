#!/usr/bin/env python3
"""
Test PayPal Credentials
Verify that PayPal API credentials are working
"""
import requests
import base64

# Your credentials from .env
CLIENT_ID = "AWENm1iOqiuWw9I06eBvkfbGrFHrfy_z17v9luYkqW9WKaNtckFT_XaiMskICFNridYk_FepZBI0QErA"
CLIENT_SECRET = "EKcJQkD203_l6syR8H5GkBcC1NAGwGhos_v4e4-DSi1vKZITb_iBes_y0ZqMIw0KWn2W2iuayfXY-veB"

# Sandbox URL
url = "https://api-m.sandbox.paypal.com/v1/oauth2/token"

# Create Basic Auth
credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
encoded = base64.b64encode(credentials.encode()).decode()

headers = {
    "Authorization": f"Basic {encoded}",
    "Content-Type": "application/x-www-form-urlencoded"
}

data = {"grant_type": "client_credentials"}

print("Testing PayPal Authentication...")
print(f"URL: {url}")
print(f"Client ID: {CLIENT_ID[:20]}...")
print(f"Client Secret: {CLIENT_SECRET[:20]}...")

try:
    response = requests.post(url, headers=headers, data=data)
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        token_data = response.json()
        print("✅ SUCCESS! PayPal authentication working!")
        print(f"Access Token: {token_data['access_token'][:50]}...")
        print(f"Expires in: {token_data.get('expires_in')} seconds")
    else:
        print("❌ FAILED! PayPal authentication error")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"❌ ERROR: {e}")
