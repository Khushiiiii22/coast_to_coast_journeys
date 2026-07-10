import os
import sys

# Ensure backend module is in path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.services.pdf_service import PDFService

def generate_test_pdfs():
    templates_dir = os.path.join(os.path.dirname(__file__), 'templates')
    
    if not os.path.exists('output_test'):
        os.makedirs('output_test')

    pdf_service = PDFService(templates_dir)

    dummy_data = {
        'booking_id': 'CTC-20260710-XYZ123',
        'guest_name': 'Priyesh Srivastava',
        'guest_email': 'priyesh@example.com',
        'guest_phone': '+1 234 567 8900',
        'hotel_name': 'The Ritz-Carlton, Los Angeles',
        'destination': 'Los Angeles, USA',
        'checkin': '2026-07-20',
        'checkout': '2026-07-25',
        'currency': 'USD',
        'amount': '1,250.00',
        'adults': 2,
        'date': '2026-07-10'
    }

    print("Generating invoice...")
    invoice_pdf = pdf_service.generate_invoice(dummy_data)
    with open('output_test/invoice.pdf', 'wb') as f:
        f.write(invoice_pdf)
    print("Saved output_test/invoice.pdf")

    print("Generating ticket...")
    ticket_pdf = pdf_service.generate_ticket(dummy_data)
    with open('output_test/ticket.pdf', 'wb') as f:
        f.write(ticket_pdf)
    print("Saved output_test/ticket.pdf")

if __name__ == '__main__':
    generate_test_pdfs()
