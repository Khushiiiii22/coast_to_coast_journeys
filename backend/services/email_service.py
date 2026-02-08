"""
Email Service using Brevo (Sendinblue) API

Brevo sends emails over HTTPS (Port 443), which works on Render
unlike traditional SMTP which uses blocked ports (25, 465, 587).
"""
import os
import requests
from datetime import datetime


class EmailService:
    """Email Service using Brevo (Sendinblue) API"""
    
    BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"
    
    def __init__(self, app=None):
        self.api_key = None
        self.default_sender = None
        self.sender_name = "C2C Journeys"
        if app:
            self.init_app(app)

    def init_app(self, app):
        # Brevo API Configuration
        self.api_key = app.config.get('BREVO_API_KEY') or os.getenv('BREVO_API_KEY')
        self.default_sender = app.config.get('MAIL_DEFAULT_SENDER') or os.getenv('MAIL_DEFAULT_SENDER', 'info@coasttocoastjourneys.com')
        
        if self.api_key:
            print(f"✅ Email service configured with Brevo API")
            print(f"   📧 Sender: {self.default_sender}")
        else:
            print(f"⚠️  Email service NOT configured - missing BREVO_API_KEY")
            print(f"   Set BREVO_API_KEY in Render Environment Variables")
        
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """Send an email using Brevo API (HTTPS)"""
        if not self.api_key:
            print("⚠️ Brevo API key not configured. Skipping email.")
            return False

        try:
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": self.api_key
            }
            
            # Build email payload
            payload = {
                "sender": {
                    "name": self.sender_name,
                    "email": self.default_sender
                },
                "to": [{"email": to_email}],
                "subject": subject,
                "textContent": body
            }
            
            # Add HTML body if provided
            if html_body:
                payload["htmlContent"] = html_body
            
            # Send the email
            response = requests.post(self.BREVO_API_URL, json=payload, headers=headers)
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                print(f"✅ Email sent to {to_email} (Message ID: {result.get('messageId', 'N/A')})")
                return True
            else:
                print(f"❌ Brevo API error: {response.status_code} - {response.text}")
                return False
            
        except Exception as e:
            print(f"❌ Failed to send email: {str(e)}")
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
        
        # Send copy to owner
        self._send_owner_notification(to_email, booking_details)
        
        return customer_email_sent

    def _send_owner_notification(self, guest_email, booking_details):
        """Send booking notification to owner/admin"""
        owner_email = os.getenv('OWNER_EMAIL', 'khushikumari62406@gmail.com')
        
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
                        <p>123 Travel Lane<br>Mumbai, India<br>support@c2cjourneys.com</p>
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
