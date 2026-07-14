import os
from playwright.sync_api import sync_playwright
import tempfile
from datetime import datetime

class PDFService:
    def __init__(self, templates_dir):
        self.templates_dir = templates_dir
        
    def _generate_pdf_from_html(self, html_content):
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.set_content(html_content, wait_until='networkidle')
            
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp:
                temp_path = tmp.name
                
            page.pdf(path=temp_path, format="A4", print_background=True)
            browser.close()
            
            with open(temp_path, 'rb') as f:
                pdf_bytes = f.read()
                
            os.remove(temp_path)
            return pdf_bytes
            
    def _calculate_nights(self, checkin, checkout):
        try:
            d1 = datetime.strptime(checkin, "%Y-%m-%d")
            d2 = datetime.strptime(checkout, "%Y-%m-%d")
            nights = (d2 - d1).days
            return max(1, nights)
        except:
            return 1

    def _get_logo_uri(self):
        logo_uri = ""
        # templates_dir is backend/templates
        # We need to go up twice: backend/templates -> backend -> root -> assets/images/logo.jpg
        logo_path = os.path.join(self.templates_dir, '..', '..', 'assets', 'images', 'logo.jpg')
        if os.path.exists(logo_path):
            import base64
            with open(logo_path, 'rb') as lf:
                b64 = base64.b64encode(lf.read()).decode()
                logo_uri = f"data:image/jpeg;base64,{b64}"
        return logo_uri

    def generate_invoice(self, booking_data):
        template_path = os.path.join(self.templates_dir, 'pdf', 'invoice.html')
        logo_uri = self._get_logo_uri()

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                html_content = f.read()
                
                guest_name = str(booking_data.get('customer_name', booking_data.get('guest_name', 'Valued Customer')))
                guest_email = str(booking_data.get('customer_email', booking_data.get('guest_email', '')))
                booking_id = str(booking_data.get('booking_id', 'N/A'))
                hotel_name = str(booking_data.get('hotel_name', 'N/A'))
                amount = str(booking_data.get('amount', '0.00'))
                currency = str(booking_data.get('currency', 'USD'))
                city = str(booking_data.get('destination', booking_data.get('city', 'Not Specified')))
                checkin = str(booking_data.get('checkin', 'N/A'))
                checkout = str(booking_data.get('checkout', 'N/A'))
                nights = str(self._calculate_nights(checkin, checkout))
                room_name = str(booking_data.get('room_name', 'Standard Room'))
                today = datetime.now().strftime("%d %b %Y")
                
                html_content = html_content.replace('{{logo_data_uri}}', logo_uri)
                html_content = html_content.replace('{{invoice_number}}', f"INV-{booking_id[-8:]}" if len(booking_id)>8 else booking_id)
                html_content = html_content.replace('{{issue_date}}', today)
                html_content = html_content.replace('{{due_date}}', today)
                html_content = html_content.replace('{{booking_id}}', booking_id)
                html_content = html_content.replace('{{transaction_id}}', booking_id)
                html_content = html_content.replace('{{payment_status}}', "PAID")
                html_content = html_content.replace('{{guest_name}}', guest_name)
                html_content = html_content.replace('{{customer_name}}', guest_name)
                html_content = html_content.replace('{{guest_email}}', guest_email)
                html_content = html_content.replace('{{customer_email}}', guest_email)
                html_content = html_content.replace('{{billing_address}}', city)
                html_content = html_content.replace('{{hotel_name}}', hotel_name)
                html_content = html_content.replace('{{hotel_address}}', str(booking_data.get('hotel_address', city)))
                html_content = html_content.replace('{{checkin}}', checkin)
                html_content = html_content.replace('{{check-in}}', checkin)
                html_content = html_content.replace('{{checkout}}', checkout)
                html_content = html_content.replace('{{check-out}}', checkout)
                html_content = html_content.replace('{{nights}}', nights)
                html_content = html_content.replace('{{adults}}', str(booking_data.get('adults', '2')))
                html_content = html_content.replace('{{children}}', "0")
                html_content = html_content.replace('{{room_type}}', room_name)
                html_content = html_content.replace('{{meal_plan}}', "Room Only")
                html_content = html_content.replace('{{supplier_ref}}', "N/A")
                html_content = html_content.replace('{{rate_per_night}}', "See Total")
                html_content = html_content.replace('{{room_charges}}', amount)
                html_content = html_content.replace('{{taxes_fees}}', "0.00")
                html_content = html_content.replace('{{service_fee}}', "0.00")
                html_content = html_content.replace('{{discount}}', "0.00")
                html_content = html_content.replace('{{total_amount}}', amount)
                html_content = html_content.replace('{{currency}}', currency)
                html_content = html_content.replace('{{amount}}', amount)
                html_content = html_content.replace('{{guest_phone}}', str(booking_data.get('phone', booking_data.get('customer_phone', 'Not Specified'))))
                html_content = html_content.replace('{{payment_method}}', "Online Payment")
                html_content = html_content.replace('{{card_type}}', "Credit/Debit/Netbanking")
                html_content = html_content.replace('{{paid_date}}', today)
                html_content = html_content.replace('{{ein}}', "N/A")
                html_content = html_content.replace('{{sales_tax}}', "Included")
                html_content = html_content.replace('{{qr_code_html}}', "")
                html_content = html_content.replace('{{date}}', today)
                html_content = html_content.replace('{{city}}', city)
        else:
            html_content = "<html><body><h1>Invoice not found</h1></body></html>"

        return self._generate_pdf_from_html(html_content)

    def generate_ticket(self, booking_data):
        template_path = os.path.join(self.templates_dir, 'pdf', 'ticket.html')
        logo_uri = self._get_logo_uri()

        if os.path.exists(template_path):
            with open(template_path, 'r') as f:
                html_content = f.read()
                
                guest_name = str(booking_data.get('customer_name', booking_data.get('guest_name', 'Valued Customer')))
                booking_id = str(booking_data.get('booking_id', 'N/A'))
                amount = str(booking_data.get('amount', '0.00'))
                currency = str(booking_data.get('currency', 'USD'))
                city = str(booking_data.get('destination', booking_data.get('city', 'Not Specified')))
                checkin = str(booking_data.get('checkin', 'N/A'))
                checkout = str(booking_data.get('checkout', 'N/A'))
                nights = str(self._calculate_nights(checkin, checkout))
                room_name = str(booking_data.get('room_name', 'Standard Room'))
                today = datetime.now().strftime("%d %b %Y")
                
                html_content = html_content.replace('{{logo_data_uri}}', logo_uri)
                html_content = html_content.replace('{{voucher_number}}', f"VCH-{booking_id[-8:]}" if len(booking_id)>8 else booking_id)
                html_content = html_content.replace('{{booking_id}}', booking_id)
                html_content = html_content.replace('{{supplier_ref}}', "N/A")
                html_content = html_content.replace('{{issue_date}}', today)
                html_content = html_content.replace('{{amount_paid}}', amount)
                html_content = html_content.replace('{{star_rating}}', "")
                html_content = html_content.replace('{{hotel_address}}', city)
                html_content = html_content.replace('{{hotel_phone}}', "Contact Hotel")
                html_content = html_content.replace('{{hotel_email}}', "N/A")
                html_content = html_content.replace('{{currency}}', currency)
                html_content = html_content.replace('{{guest_name}}', guest_name)
                html_content = html_content.replace('{{customer_name}}', guest_name)
                html_content = html_content.replace('{{additional_guests}}', "None")
                html_content = html_content.replace('{{adults}}', str(booking_data.get('adults', '2')))
                html_content = html_content.replace('{{children}}', "0")
                html_content = html_content.replace('{{room_count}}', "1")
                html_content = html_content.replace('{{checkin}}', checkin)
                html_content = html_content.replace('{{check-in}}', checkin)
                html_content = html_content.replace('{{checkout}}', checkout)
                html_content = html_content.replace('{{check-out}}', checkout)
                html_content = html_content.replace('{{checkin_time}}', "14:00")
                html_content = html_content.replace('{{checkout_time}}', "12:00")
                html_content = html_content.replace('{{nights}}', nights)
                html_content = html_content.replace('{{room_type}}', room_name)
                html_content = html_content.replace('{{meal_plan}}', "Room Only")
                html_content = html_content.replace('{{payment_status}}', "CONFIRMED")
                html_content = html_content.replace('{{balance_due}}', "0.00")
                html_content = html_content.replace('{{included_services}}', "Accommodation")
                html_content = html_content.replace('{{not_included_services}}', "Personal Expenses")
                html_content = html_content.replace('{{cancellation_policy}}', "As per hotel policy")
                html_content = html_content.replace('{{city_tax_policy}}', "Payable at hotel if applicable")
                html_content = html_content.replace('{{transaction_id}}', booking_id)
                html_content = html_content.replace('{{payment_method}}', "Online")
                html_content = html_content.replace('{{qr_code_html}}', "")
                html_content = html_content.replace('{{hotel_name}}', str(booking_data.get('hotel_name', 'N/A')))
        else:
            html_content = "<html><body><h1>Ticket not found</h1></body></html>"

        return self._generate_pdf_from_html(html_content)
