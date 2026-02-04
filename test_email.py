#!/usr/bin/env python3
"""Quick test for Resend API"""
import resend

resend.api_key = "re_dZ2Ynj9r_7YsEAMUj22KevpxjWjkJ5hXV"

try:
    r = resend.Emails.send({
        "from": "onboarding@resend.dev",
        "to": "khushikumari62406@gmail.com",
        "subject": "C2C Journeys - Email Test",
        "html": "<h1>Success!</h1><p>Your Resend email is working!</p>"
    })
    print(f"✅ Email sent! ID: {r}")
except Exception as e:
    print(f"❌ Error: {e}")
