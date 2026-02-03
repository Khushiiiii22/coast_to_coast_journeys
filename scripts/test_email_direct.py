#!/usr/bin/env python3
"""
Test sending email to specific address
"""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get SMTP settings
SMTP_SERVER = os.getenv('MAIL_SERVER', 'smtpout.secureserver.net')
SMTP_PORT = int(os.getenv('MAIL_PORT', 465))
SMTP_USERNAME = os.getenv('MAIL_USERNAME')
SMTP_PASSWORD = os.getenv('MAIL_PASSWORD')
SENDER_EMAIL = os.getenv('MAIL_DEFAULT_SENDER')

# Test recipient
TEST_RECIPIENT = "Vkvishal1022@gmail.com"

print(f"Testing email to: {TEST_RECIPIENT}")
print(f"From: {SENDER_EMAIL}")
print(f"Server: {SMTP_SERVER}:{SMTP_PORT}")

try:
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = TEST_RECIPIENT
    msg['Subject'] = '🧪 C2C Journeys - Test Email'
    
    body = """
    Hello!
    
    This is a test email from C2C Journeys.
    
    If you received this email, the email system is working correctly! ✅
    
    Best regards,
    C2C Journeys System
    """
    
    msg.attach(MIMEText(body, 'plain'))
    
    print("🔌 Connecting to SMTP server...")
    server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=30)
    
    print("🔑 Logging in...")
    server.login(SMTP_USERNAME, SMTP_PASSWORD)
    
    print(f"📤 Sending test email to {TEST_RECIPIENT}...")
    server.send_message(msg)
    
    print("🔚 Closing connection...")
    server.quit()
    
    print("\n✅ SUCCESS! Test email sent!")
    print(f"📬 Check inbox of: {TEST_RECIPIENT}")
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
