import os
from weasyprint import HTML

class PDFService:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir
        
    def generate_invoice(self, booking_data):
        """Generate PDF Invoice from HTML template"""
        # A basic template if file doesn't exist
        html_content = f"""
        <html>
        <head><style>body {{ font-family: sans-serif; padding: 40px; }} h1 {{ color: #2e7d32; }}</style></head>
        <body>
            <h1>C2C Journeys - Invoice</h1>
            <p><strong>Booking ID:</strong> {booking_data.get('booking_id', 'N/A')}</p>
            <p><strong>Guest Name:</strong> {booking_data.get('guest_name', 'Valued Customer')}</p>
            <p><strong>Hotel:</strong> {booking_data.get('hotel_name', 'N/A')}</p>
            <p><strong>Amount Paid:</strong> {booking_data.get('currency', 'USD')} {booking_data.get('amount', 0)}</p>
        </body>
        </html>
        """
        # Try to load from file if we have one
        template_path = os.path.join(self.templates_dir, 'pdf', 'invoice.html')
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                # Naive replace - in production use Jinja2
                html_content = f.read()
                html_content = html_content.replace('{{booking_id}}', str(booking_data.get('booking_id', '')))
                html_content = html_content.replace('{{guest_name}}', str(booking_data.get('guest_name', '')))
                html_content = html_content.replace('{{hotel_name}}', str(booking_data.get('hotel_name', '')))
                html_content = html_content.replace('{{amount}}', str(booking_data.get('amount', '')))
                html_content = html_content.replace('{{currency}}', str(booking_data.get('currency', 'USD')))
                html_content = html_content.replace('{{date}}', str(booking_data.get('date', '')))
                html_content = html_content.replace('{{destination}}', str(booking_data.get('destination', '')))
                html_content = html_content.replace('{{guest_email}}', str(booking_data.get('guest_email', '')))
                html_content = html_content.replace('{{guest_phone}}', str(booking_data.get('guest_phone', '')))
                html_content = html_content.replace('{{checkin}}', str(booking_data.get('checkin', '')))
                html_content = html_content.replace('{{checkout}}', str(booking_data.get('checkout', '')))

        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes

    def generate_ticket(self, booking_data):
        """Generate PDF Ticket/Voucher from HTML template"""
        html_content = f"""
        <html>
        <head><style>body {{ font-family: sans-serif; padding: 40px; border: 2px dashed #000; margin: 20px; }}</style></head>
        <body>
            <h1>Hotel Booking Voucher</h1>
            <p><strong>Booking ID:</strong> {booking_data.get('booking_id', 'N/A')}</p>
            <p><strong>Guest Name:</strong> {booking_data.get('guest_name', 'Valued Customer')}</p>
            <p><strong>Hotel:</strong> {booking_data.get('hotel_name', 'N/A')}</p>
            <p><strong>Check-in:</strong> {booking_data.get('checkin', 'N/A')} &nbsp;&nbsp; <strong>Check-out:</strong> {booking_data.get('checkout', 'N/A')}</p>
            <p><em>Please present this voucher upon arrival.</em></p>
        </body>
        </html>
        """
        
        template_path = os.path.join(self.templates_dir, 'pdf', 'ticket.html')
        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                html_content = f.read()
                # Basic replacements
                html_content = html_content.replace('{{booking_id}}', str(booking_data.get('booking_id', '')))
                html_content = html_content.replace('{{guest_name}}', str(booking_data.get('guest_name', '')))
                html_content = html_content.replace('{{hotel_name}}', str(booking_data.get('hotel_name', '')))
                html_content = html_content.replace('{{checkin}}', str(booking_data.get('checkin', '')))
                html_content = html_content.replace('{{checkout}}', str(booking_data.get('checkout', '')))
                html_content = html_content.replace('{{currency}}', str(booking_data.get('currency', 'USD')))
                html_content = html_content.replace('{{amount}}', str(booking_data.get('amount', '')))
                html_content = html_content.replace('{{adults}}', str(booking_data.get('adults', '2')))
                html_content = html_content.replace('{{destination}}', str(booking_data.get('destination', '')))

        pdf_bytes = HTML(string=html_content).write_pdf()
        return pdf_bytes
