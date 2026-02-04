#!/usr/bin/env python3
"""
Test Resend Email API Configuration
Resend uses HTTPS (Port 443) which works on Render!
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get Resend API key
RESEND_API_KEY = os.getenv('RESEND_API_KEY')
DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', 'onboarding@resend.dev')

print("=" * 50)
print("Resend Email API Test")
print("=" * 50)
print(f"API Key: {'✅ Set' if RESEND_API_KEY and RESEND_API_KEY != 'YOUR_RESEND_API_KEY_HERE' else '❌ NOT SET'}")
print(f"Default Sender: {DEFAULT_SENDER}")
print("=" * 50)

if not RESEND_API_KEY or RESEND_API_KEY == 'YOUR_RESEND_API_KEY_HERE':
    print("\n❌ ERROR: RESEND_API_KEY not configured in .env")
    print("\n📋 Steps to get your Resend API key:")
    print("   1. Go to https://resend.com and sign up for FREE")
    print("   2. Verify your email address")
    print("   3. Go to https://resend.com/api-keys")
    print("   4. Click 'Create API Key'")
    print("   5. Copy the API key and add it to your .env file:")
    print("      RESEND_API_KEY=re_xxxxxxxxxxxxx")
    print("   6. Also update this key in Render Environment Variables")
    exit(1)

# Test email recipient
TEST_EMAIL = input("\n📧 Enter your email to receive test email: ").strip()

if not TEST_EMAIL:
    print("❌ No email provided. Exiting.")
    exit(1)

print(f"\n📤 Sending test email to {TEST_EMAIL}...")

try:
    url = "https://api.resend.com/emails"
    
    headers = {
        "Authorization": f"Bearer {RESEND_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "from": DEFAULT_SENDER,
        "to": [TEST_EMAIL],
        "subject": "🧪 C2C Journeys - Resend API Test Email",
        "html": """
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #0066cc;">✅ Email Test Successful!</h1>
            <p>If you received this email, your Resend API configuration is working correctly!</p>
            
            <div style="background: #f5f5f5; padding: 15px; border-radius: 8px; margin: 20px 0;">
                <h3 style="margin-top: 0;">Configuration Details:</h3>
                <ul>
                    <li>✅ Resend API is connected</li>
                    <li>✅ HTTPS (Port 443) - Works on Render!</li>
                    <li>✅ No SMTP ports needed</li>
                </ul>
            </div>
            
            <p style="color: #666;">
                This is a test email from C2C Journeys.<br>
                Powered by <a href="https://resend.com">Resend</a>
            </p>
        </div>
        """
    }
    
    response = requests.post(url, headers=headers, json=payload, timeout=30)
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✅ SUCCESS! Email sent!")
        print(f"   📧 Email ID: {result.get('id', 'N/A')}")
        print(f"   📬 Check your inbox at {TEST_EMAIL}")
        print("\n🎉 Your Resend configuration is working!")
        print("   Now update RESEND_API_KEY in Render Environment Variables.")
    else:
        error = response.json()
        print(f"\n❌ FAILED to send email")
        print(f"   Status: {response.status_code}")
        print(f"   Error: {error.get('message', response.text)}")
        
        if response.status_code == 403:
            print("\n⚠️  This might be a domain verification issue.")
            print("   For sending to any email, you need to verify your domain at:")
            print("   https://resend.com/domains")

except requests.exceptions.RequestException as e:
    print(f"\n❌ Network error: {str(e)}")
except Exception as e:
    print(f"\n❌ Unexpected error: {str(e)}")
