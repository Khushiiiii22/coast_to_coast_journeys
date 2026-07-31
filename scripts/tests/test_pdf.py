import sys
import os

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

from services.pdf_service import PDFService

pdf_service = PDFService('backend/templates')

booking_details = {
    'customer_name': 'Test User',
    'customer_email': 'test@example.com',
    'booking_id': 'TEST-12345',
    'hotel_name': 'Test Hotel',
    'amount': 1000,
    'currency': 'USD',
    'checkin': '2026-08-01',
    'checkout': '2026-08-05'
}

print("Generating invoice PDF...")
pdf = pdf_service.generate_invoice(booking_details)
print(f"Generated PDF of size: {len(pdf)} bytes")

