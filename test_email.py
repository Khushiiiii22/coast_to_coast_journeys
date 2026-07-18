import sys
import os
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from app import app
from services.email_service import email_service

with app.app_context():
    email_service.init_app(app)
    
    booking_details = {
        'booking_id': 'TEST-123',
        'customer_name': 'Test User',
        'customer_email': 'info@coasttocoastjourneys.com',
        'hotel_name': 'Conrad Los Angeles',
        'checkin': '2026-07-13',
        'checkout': '2026-07-15',
        'amount': 325,
        'currency': 'USD',
        'room_name': 'Standard Room'
    }
    
    # Try sending to user's email
    print("Testing email send...")
    success = email_service.send_booking_confirmation('info@coasttocoastjourneys.com', booking_details)
    print(f"Success: {success}")
