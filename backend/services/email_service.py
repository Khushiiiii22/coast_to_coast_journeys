
import resend
import os
from datetime import datetime

class EmailService:
    """
    Email Service using Resend API (HTTPS-based)
    
    Resend sends emails over HTTPS (Port 443), which works on Render
    unlike traditional SMTP which uses blocked ports (25, 465, 587).
    """
    
    def __init__(self, app=None):
        self.api_key = None
        self.default_sender = None
        if app:
            self.init_app(app)

    def init_app(self, app):
<<<<<<< HEAD
        self.smtp_server = app.config.get('MAIL_SERVER', 'smtpout.secureserver.net')
        # Use Port 587 by default for cloud hosting to avoid Port 465 blocking
        self.smtp_port = int(app.config.get('MAIL_PORT', 587))
        self.use_tls = app.config.get('MAIL_USE_TLS', True)
        self.use_ssl = app.config.get('MAIL_USE_SSL', False)
        self.username = app.config.get('MAIL_USERNAME')
        self.password = app.config.get('MAIL_PASSWORD')
        self.default_sender = app.config.get('MAIL_DEFAULT_SENDER')
        self.resend_api_key = app.config.get('RESEND_API_KEY')
        
        # Log email configuration status for debugging
        if self.resend_api_key:
            print(f"✅ Email service configured: Resend API")
            print(f"   📧 Sender: {self.default_sender}")
        elif self.username and self.password:
            print(f"✅ Email service configured: SMTP {self.smtp_server}:{self.smtp_port} (SSL={self.use_ssl})")
            print(f"   📧 Sender: {self.default_sender}")
        else:
            print(f"⚠️  Email service NOT configured - missing MAIL_USERNAME or RESEND_API_KEY")
            print(f"   Set RESEND_API_KEY in Render Environment Variables for production.")
        
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """Send an email"""
        # Try Resend API first
        if self.resend_api_key:
            return self._send_with_resend(to_email, subject, body, html_body, attachments)
            
        # Fallback to SMTP
        if not self.username or not self.password:
            print("⚠️ Email credentials not configured. Skipping email.")
=======
        # Resend API Configuration
        self.api_key = app.config.get('RESEND_API_KEY') or os.getenv('RESEND_API_KEY')
        self.default_sender = app.config.get('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_DEFAULT_SENDER', 'onboarding@resend.dev')
        
        # Set the API key for resend
        if self.api_key:
            resend.api_key = self.api_key
            print(f"✅ Email service configured with Resend API")
            print(f"   📧 Sender: {self.default_sender}")
        else:
            print(f"⚠️  Email service NOT configured - missing RESEND_API_KEY")
            print(f"   Set RESEND_API_KEY in Render Environment Variables")
            print(f"   Get your API key from: https://resend.com/api-keys")
        
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """Send an email using Resend API (HTTPS)"""
        if not self.api_key:
            print("⚠️ Resend API key not configured. Skipping email.")
            print("   Set RESEND_API_KEY environment variable")
>>>>>>> 0a7885b (resend)
            return False

        try:
            # Ensure API key is set
            resend.api_key = self.api_key
            
            # Build the email params
            params = {
                "from": self.default_sender,
                "to": [to_email] if isinstance(to_email, str) else to_email,
                "subject": subject,
                "text": body
            }
            
            # Add HTML body if provided
            if html_body:
                params["html"] = html_body
            
            # Add attachments if provided
            if attachments:
                attachment_list = []
                import base64
                for filename, content in attachments.items():
                    attachment_list.append({
                        "filename": filename,
                        "content": base64.b64encode(content).decode('utf-8')
                    })
                params["attachments"] = attachment_list
            
            # Send the email
            result = resend.Emails.send(params)
            
<<<<<<< HEAD
            print(f"✅ SMTP Email sent to {to_email}")
=======
            print(f"✅ Email sent to {to_email} (ID: {result.get('id', 'N/A')})")
>>>>>>> 0a7885b (resend)
            return True
            
        except Exception as e:
            print(f"❌ Failed to send SMTP email: {str(e)}")
            return False

    def _send_with_resend(self, to_email, subject, body, html_body=None, attachments=None):
        """Send an email using Resend API"""
        try:
            import resend
            resend.api_key = self.resend_api_key
            
            params = {
                "from": f"C2C Journeys <{self.default_sender}>",
                "to": to_email,
                "subject": subject,
                "text": body,
            }
            
            if html_body:
                params["html"] = html_body
                
            if attachments:
                resend_attachments = []
                for filename, content in attachments.items():
                    import base64
                    resend_attachments.append({
                        "filename": filename,
                        "content": base64.b64encode(content).decode()
                    })
                params["attachments"] = resend_attachments
                
            r = resend.Emails.send(params)
            print(f"✅ Resend API Email sent to {to_email} (ID: {r.get('id')})")
            return True
        except Exception as e:
            print(f"❌ Failed to send Resend API email: {str(e)}")
            # If Resend fails, we don't fallback to SMTP here to avoid confusing timeouts
            return False

    def send_booking_confirmation(self, to_email, booking_details):
        """Send booking confirmation with invoice"""
        subject = f"Booking Confirmation - {booking_details.get('hotel_name')}"
        
        # Generate Invoice HTML
        invoice_html = self._generate_invoice_html(booking_details)
        
        body = f"""
Dear {booking_details.get('customer_name', 'Customer')},

Thank you for booking with C2C Journeys!

Your booking for {booking_details.get('hotel_name')} has been confirmed.

Check-in: {booking_details.get('checkin')}
Check-out: {booking_details.get('checkout')}
Total Amount: {booking_details.get('amount')} {booking_details.get('currency', 'INR')}

Your invoice is attached below.

Safe Travels,
C2C Journeys Team
        """
        
        # Send email to customer
        customer_email_sent = self.send_email(to_email, subject, body, html_body=invoice_html)
        
        # Send copy to owner (from .env MAIL_DEFAULT_SENDER)
        self._send_owner_notification(to_email, booking_details)
        
        return customer_email_sent

    def _send_owner_notification(self, guest_email, booking_details):
        """Send booking notification to owner/admin"""
        owner_email = self.default_sender
        
        if not owner_email:
            print("⚠️ Owner email not configured. Skipping owner notification.")
            return
        
        subject = f"🎉 New Booking - {booking_details.get('hotel_name')} | {booking_details.get('booking_id', 'N/A')}"
        
        body = f"""
New Booking Confirmed!

══════════════════════════════════════
BOOKING DETAILS
══════════════════════════════════════

Booking ID: {booking_details.get('booking_id', 'N/A')}

GUEST INFORMATION:
• Name: {booking_details.get('customer_name', 'N/A')}
• Email: {guest_email}

HOTEL DETAILS:
• Hotel: {booking_details.get('hotel_name', 'N/A')}
• Check-in: {booking_details.get('checkin', 'N/A')}
• Check-out: {booking_details.get('checkout', 'N/A')}

PAYMENT:
• Amount: ₹{booking_details.get('amount', 'N/A')}

══════════════════════════════════════

This is an automated notification from C2C Journeys.
        """
        
        print(f"📧 Sending owner notification to {owner_email}")
        self.send_email(owner_email, subject, body)

    def _send_sales_notification(self, booking_details):
        """Send notification to sales team"""
        sales_email = self.default_sender
        subject = f"New Booking Alert - {booking_details.get('booking_id', 'N/A')}"
        
        body = f"""
New Booking Confirmed!

Booking ID: {booking_details.get('booking_id', 'N/A')}
Customer: {booking_details.get('customer_name', 'N/A')}
Email: {booking_details.get('customer_email', 'N/A')}
Hotel: {booking_details.get('hotel_name', 'N/A')}
Check-in: {booking_details.get('checkin', 'N/A')}
Check-out: {booking_details.get('checkout', 'N/A')}
Amount: {booking_details.get('amount', 'N/A')} {booking_details.get('currency', 'INR')}
        """
        
        print(f"📧 Sending sales notification to {sales_email}")
        self.send_email(sales_email, subject, body)

    def _generate_invoice_html(self, booking):
        """Generate HTML invoice"""
        date_str = datetime.now().strftime("%d %B %Y")
        
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body {{ font-family: Arial, sans-serif; color: #333; }}
                .invoice-box {{ max-width: 800px; margin: auto; padding: 30px; border: 1px solid #eee; box-shadow: 0 0 10px rgba(0, 0, 0, .15); }}
                .header {{ display: flex; justify-content: space-between; margin-bottom: 20px; }}
                .company-details {{ text-align: right; }}
                .invoice-title {{ color: #0066cc; font-size: 24px; font-weight: bold; }}
                .table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
                .table th, .table td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
                .total {{ font-weight: bold; font-size: 18px; color: #0066cc; text-align: right; margin-top: 20px; }}
                .footer {{ margin-top: 40px; text-align: center; font-size: 12px; color: #777; }}
            </style>
        </head>
        <body>
            <div class="invoice-box">
                <div class="header">
                    <div>
                        <h2 style="margin: 0;">C2C Journeys</h2>
                        <p>Booking ID: {booking.get('booking_id', 'N/A')}</p>
                        <p>Date: {date_str}</p>
                    </div>
                    <div class="company-details">
                        <p>123 Travel Lane<br>Mumbai, India<br>support@coasttocoastjourneys.com</p>
                    </div>
                </div>
                
                <div class="invoice-title">INVOICE</div>
                
                <p><strong>Bill To:</strong><br>{booking.get('customer_name', 'Valued Customer')}<br>{booking.get('customer_email', '')}</p>
                
                <table class="table">
                    <thead>
                        <tr>
                            <th>Description</th>
                            <th>Details</th>
                            <th style="text-align: right;">Amount</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td>Hotel Booking</td>
                            <td>{booking.get('hotel_name')}</td>
                            <td style="text-align: right;">{booking.get('amount')} {booking.get('currency', 'INR')}</td>
                        </tr>
                        <tr>
                            <td>Stay Duration</td>
                            <td>{booking.get('checkin')} to {booking.get('checkout')}</td>
                            <td style="text-align: right;">-</td>
                        </tr>
                    </tbody>
                </table>
                
                <div class="total">
                    Total: {booking.get('amount')} {booking.get('currency', 'INR')}
                </div>
                
                <div class="footer">
                    <p>Thank you for choosing C2C Journeys!</p>
                </div>
            </div>
        </body>
        </html>
        """

# Singleton
email_service = EmailService()
