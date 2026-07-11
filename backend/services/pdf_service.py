import os
from playwright.sync_api import sync_playwright
import tempfile

class PDFService:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir
        
    def _generate_pdf_from_html(self, html_content):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until='networkidle')
            
            # Save to temporary file first to get bytes
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                temp_path = tmp.name
                
            page.pdf(path=temp_path, format="A4", print_background=True)
            browser.close()
            
            with open(temp_path, 'rb') as f:
                pdf_bytes = f.read()
                
            os.remove(temp_path)
            return pdf_bytes
        
    def generate_invoice(self, booking_data):
        """Generate PDF Invoice from HTML template"""
        # Try to load from file if we have one
        template_path = os.path.join(self.templates_dir, 'pdf', 'invoice.html')
        
        # Load logo
        logo_uri = ""
        logo_path = os.path.join(self.templates_dir, '..', 'assets', 'images', 'c2c-logo.png')
        if os.path.exists(logo_path):
            import base64
            with open(logo_path, 'rb') as lf:
                b64 = base64.b64encode(lf.read()).decode()
                logo_uri = f"data:image/png;base64,{b64}"

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                html_content = f.read()
                html_content = html_content.replace('{{logo_data_uri}}', logo_uri)
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
        else:
            html_content = "<html><body><h1>Invoice not found</h1></body></html>"

        return self._generate_pdf_from_html(html_content)

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
        
        # Load logo for both
        logo_uri = ""
        logo_path = os.path.join(self.templates_dir, '..', 'assets', 'images', 'c2c-logo.png')
        if os.path.exists(logo_path):
            import base64
            with open(logo_path, 'rb') as lf:
                b64 = base64.b64encode(lf.read()).decode()
                logo_uri = f"data:image/png;base64,{b64}"

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                html_content = f.read()
                # Basic replacements
                html_content = html_content.replace('{{logo_data_uri}}', logo_uri)
                html_content = html_content.replace('{{booking_id}}', str(booking_data.get('booking_id', '')))
                html_content = html_content.replace('{{guest_name}}', str(booking_data.get('guest_name', '')))
                html_content = html_content.replace('{{hotel_name}}', str(booking_data.get('hotel_name', '')))
                html_content = html_content.replace('{{checkin}}', str(booking_data.get('checkin', '')))
                html_content = html_content.replace('{{checkout}}', str(booking_data.get('checkout', '')))
                html_content = html_content.replace('{{currency}}', str(booking_data.get('currency', 'USD')))
                html_content = html_content.replace('{{amount}}', str(booking_data.get('amount', '')))
                html_content = html_content.replace('{{adults}}', str(booking_data.get('adults', '2')))
                html_content = html_content.replace('{{destination}}', str(booking_data.get('destination', '')))
        else:
            html_content = "<html><body><h1>Ticket not found</h1></body></html>"

        return self._generate_pdf_from_html(html_content)
