#!/usr/bin/env python3
"""
Test SMTP Email Configuration for GoDaddy
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get SMTP settings from .env
SMTP_SERVER = os.getenv('MAIL_SERVER', 'smtpout.secureserver.net')
SMTP_PORT = int(os.getenv('MAIL_PORT', 465))
USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
SMTP_USERNAME = os.getenv('MAIL_USERNAME')
SMTP_PASSWORD = os.getenv('MAIL_PASSWORD')
SENDER_EMAIL = os.getenv('MAIL_DEFAULT_SENDER')

print("=" * 50)
print("GoDaddy SMTP Configuration Test")
print("=" * 50)
print(f"Server: {SMTP_SERVER}")
print(f"Port: {SMTP_PORT}")
print(f"Use SSL: {USE_SSL}")
print(f"Use TLS: {USE_TLS}")
print(f"Username: {SMTP_USERNAME}")
print(f"Password: {'*' * len(SMTP_PASSWORD) if SMTP_PASSWORD else 'NOT SET'}")
print(f"Sender: {SENDER_EMAIL}")
print("=" * 50)

if not SMTP_USERNAME or not SMTP_PASSWORD:
    print("❌ ERROR: SMTP credentials not configured in .env")
    exit(1)

# Test recipient
TEST_RECIPIENT = SENDER_EMAIL

try:
    print(f"\n📧 Attempting to connect to {SMTP_SERVER}:{SMTP_PORT}...")
    
    # Create message
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = TEST_RECIPIENT
    msg['Subject'] = '🧪 C2C Journeys - SMTP Test Email'
    
    body = """
    Hello!
    
    This is a test email from C2C Journeys.
    
    If you received this email, your SMTP configuration is working correctly! ✅
    
    Settings Used:
    - Server: {}
    - Port: {}
    - SSL: {}
    
    Best regards,
    C2C Journeys System
    """.format(SMTP_SERVER, SMTP_PORT, USE_SSL)
    
    msg.attach(MIMEText(body, 'plain'))
    
    # Connect to SMTP server
    print("🔌 Connecting to SMTP server...")
    
    if USE_SSL:
        print("🔒 Using SSL connection...")
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=30)
        if USE_TLS:
            print("🔒 Starting TLS...")
            server.starttls()
    
    server.set_debuglevel(1)  # Enable debug output
    
    print("🔑 Logging in...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    
    print(f"📤 Sending test email to {TEST_RECIPIENT}...")
    server.send_message(msg)
    
    print("🔚 Closing connection...")
    server.quit()
    
    print("\n" + "=" * 50)
    print("✅ SUCCESS! Test email sent successfully!")
    print(f"📬 Check inbox of: {TEST_RECIPIENT}")
    print("=" * 50)
    
except smtplib.SMTPAuthenticationError as e:
    print(f"\n❌ AUTHENTICATION FAILED!")
    print(f"Error: {e}")
    print("\n💡 Possible fixes:")
    print("1. Check if the password in .env is correct")
    print("2. Make sure the email account allows SMTP access")
    
except smtplib.SMTPException as e:
    print(f"\n❌ SMTP ERROR!")
    print(f"Error: {e}")
    
except Exception as e:
    print(f"\n❌ ERROR!")
    print(f"Error Type: {type(e).__name__}")
    print(f"Error: {e}")
