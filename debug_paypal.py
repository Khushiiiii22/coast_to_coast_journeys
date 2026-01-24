#!/usr/bin/env python3
"""
Comprehensive PayPal Debug Test
Tests all aspects of PayPal authentication
"""
import requests
import base64
import json

def test_paypal_auth(client_id, client_secret, mode='sandbox'):
    """Test PayPal authentication thoroughly"""
    
    print("=" * 60)
    print("PAYPAL AUTHENTICATION DEBUG TEST")
    print("=" * 60)
    
    # 1. Credential Validation
    print("\n1. CREDENTIAL VALIDATION")
    print(f"   Client ID: {client_id[:20]}...{client_id[-20:]}")
    print(f"   Length: {len(client_id)} characters")
    print(f"   Secret: {client_secret[:20]}...{client_secret[-20:]}")
    print(f"   Length: {len(client_secret)} characters")
    print(f"   Mode: {mode}")
    
    # 2. API Endpoint
    if mode == 'live':
        base_url = 'https://api-m.paypal.com'
    else:
        base_url = 'https://api-m.sandbox.paypal.com'
    
    url = f'{base_url}/v1/oauth2/token'
    print(f"\n2. API ENDPOINT")
    print(f"   URL: {url}")
    
    # 3. Authorization Header
    credentials = f'{client_id}:{client_secret}'
    encoded = base64.b64encode(credentials.encode()).decode()
    
    print(f"\n3. AUTHORIZATION HEADER")
    print(f"   Raw credentials length: {len(credentials)}")
    print(f"   Base64 encoded length: {len(encoded)}")
    print(f"   Encoded (first 50 chars): {encoded[:50]}...")
    
    headers = {
        'Authorization': f'Basic {encoded}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {'grant_type': 'client_credentials'}
    
    # 4. API Request
    print(f"\n4. MAKING API REQUEST...")
    try:
        response = requests.post(url, headers=headers, data=data, timeout=10)
        
        print(f"   Status Code: {response.status_code}")
        print(f"   Response Headers:")
        for key, value in response.headers.items():
            if key.lower() in ['paypal-debug-id', 'content-type', 'server']:
                print(f"     {key}: {value}")
        
        print(f"\n5. RESPONSE BODY")
        try:
            response_json = response.json()
            print(f"   {json.dumps(response_json, indent=2)}")
            
            if response.status_code == 200:
                print(f"\n✅ SUCCESS! PayPal authentication working!")
                print(f"   Access Token (first 50 chars): {response_json.get('access_token', '')[:50]}...")
                print(f"   Token Type: {response_json.get('token_type')}")
                print(f"   Expires In: {response_json.get('expires_in')} seconds")
                return True
            else:
                print(f"\n❌ FAILED! Authentication error")
                if 'error' in response_json:
                    print(f"   Error: {response_json['error']}")
                    print(f"   Description: {response_json.get('error_description', 'N/A')}")
                    
                    # Specific error guidance
                    if response_json['error'] == 'invalid_client':
                        print(f"\n💡 DIAGNOSIS:")
                        print(f"   The credentials don't match any PayPal app.")
                        print(f"   Possible causes:")
                        print(f"   1. Wrong Client ID or Secret")
                        print(f"   2. App has been deleted from dashboard")
                        print(f"   3. Credentials are from LIVE mode but using SANDBOX URL (or vice versa)")
                        print(f"   4. App needs to be activated in PayPal dashboard")
                return False
                
        except json.JSONDecodeError:
            print(f"   Raw response: {response.text}")
            return False
            
    except requests.exceptions.Timeout:
        print(f"   ❌ Request timeout - PayPal API not responding")
        return False
    except requests.exceptions.ConnectionError as e:
        print(f"   ❌ Connection error: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    # Test credentials from .env
    CLIENT_ID = "AWENm1iOqiuWw9I06eBvkfbGrFHrfy_z17v9luYkqW9WKaNtckFT_XaiMskICFNridYk_FepZBI0QErA"
    CLIENT_SECRET = "EKcJQkD203_l6syR8H5GkBcC1NAGwGhos_v4e4-DSi1vKZITb_iBes_y0ZqMIw0KWn2W2iuayfXY-veB"
    
    # Test sandbox
    print("\n🔍 Testing SANDBOX credentials...")
    sandbox_result = test_paypal_auth(CLIENT_ID, CLIENT_SECRET, mode='sandbox')
    
    # If sandbox fails, try live
    if not sandbox_result:
        print("\n\n🔍 Testing LIVE credentials (just in case)...")
        live_result = test_paypal_auth(CLIENT_ID, CLIENT_SECRET, mode='live')
        
        if live_result:
            print("\n⚠️  WARNING: These are LIVE credentials, not SANDBOX!")
            print("   Update PAYPAL_MODE=live in .env")
    
    print("\n" + "=" * 60)
    if sandbox_result:
        print("RESULT: ✅ PayPal integration is working correctly!")
    else:
        print("RESULT: ❌ PayPal credentials are invalid")
        print("\nNEXT STEPS:")
        print("1. Login to https://developer.paypal.com/dashboard/")
        print("2. Go to 'Apps & Credentials'")
        print("3. Make sure you're in the correct mode (Sandbox/Live)")
        print("4. Create a NEW app or use an existing one")
        print("5. Copy the EXACT credentials shown")
        print("6. Update your .env file")
    print("=" * 60)
