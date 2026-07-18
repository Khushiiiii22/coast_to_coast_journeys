import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import app
from services.email_service import email_service

with app.app_context():
    email_service.init_app(app)
    
    booking_details = {
        'booking_id': 'TEST-124',
        'customer_name': 'Test User',
        'customer_email': 'priyesh71sri@gmail.com',  # Using the user's email explicitly
        'hotel_name': 'Conrad Los Angeles',
        'checkin': '2026-07-13',
        'checkout': '2026-07-15',
        'amount': 325,
        'currency': 'USD',
        'room_name': 'Standard Room'
    }
    
    print("Testing email send to priyesh71sri@gmail.com...")
    success = email_service.send_booking_confirmation('priyesh71sri@gmail.com', booking_details)
    print(f"Success: {success}")
