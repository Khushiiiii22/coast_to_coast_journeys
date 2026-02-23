"""
Email Service using Brevo (Sendinblue) API

Brevo sends emails over HTTPS (Port 443), which works on Cloud Run / Render
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
        # Verified sender in Brevo
        self.default_sender = os.getenv('MAIL_DEFAULT_SENDER', 'info@coasttocoastjourneys.com')
        
        if self.api_key:
            print(f"✅ Email service configured with Brevo API")
            print(f"   📧 Sender: {self.default_sender}")
        else:
            print(f"⚠️  Email service NOT configured - missing BREVO_API_KEY")
        
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
        """Send booking confirmation with professional invoice"""
        hotel_name = booking_details.get('hotel_name', 'Hotel')
        subject = f"Booking Confirmed ✅ — {hotel_name} | C2C Journeys"
        
        # Generate professional HTML email
        invoice_html = self._generate_invoice_html(booking_details)
        
        # Plain text fallback
        amount = booking_details.get('amount', 0)
        currency = booking_details.get('currency', 'INR')
        body = f"""
Dear {booking_details.get('customer_name', 'Guest')},

Your booking at {hotel_name} has been confirmed!

Booking ID: {booking_details.get('booking_id', 'N/A')}
Check-in: {self._format_date(booking_details.get('checkin', ''))}
Check-out: {self._format_date(booking_details.get('checkout', ''))}
Total Amount: {self._format_amount(amount, currency)}

Thank you for choosing C2C Journeys!
        """
        
        # Send email to customer
        customer_email_sent = self.send_email(to_email, subject, body, html_body=invoice_html)
        
        # Send copy to owner
        self._send_owner_notification(to_email, booking_details)
        
        return customer_email_sent

    def _send_owner_notification(self, guest_email, booking_details):
        """Send booking notification to owner/admin"""
        owner_email = os.getenv('CORPORATE_EMAIL', os.getenv('OWNER_EMAIL', 'info@coasttocoastjourneys.com'))
        
        subject = f"🎉 New Booking — {booking_details.get('hotel_name')} | {booking_details.get('booking_id', 'N/A')}"
        
        amount = booking_details.get('amount', 0)
        currency = booking_details.get('currency', 'INR')
        
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
• Room: {booking_details.get('room_name', 'N/A')}
• Check-in: {booking_details.get('checkin', 'N/A')}
• Check-out: {booking_details.get('checkout', 'N/A')}

PAYMENT:
• Amount: {self._format_amount(amount, currency)}

══════════════════════════════════════

This is an automated notification from C2C Journeys.
        """
        
        print(f"📧 Sending owner notification to {owner_email}")
        self.send_email(owner_email, subject, body)

    def _format_date(self, date_str):
        """Format date string nicely"""
        if not date_str:
            return 'N/A'
        try:
            d = datetime.strptime(str(date_str), '%Y-%m-%d')
            return d.strftime('%d %B %Y')
        except (ValueError, TypeError):
            return str(date_str)

    def _format_amount(self, amount, currency='INR'):
        """Format amount with currency symbol"""
        try:
            num = float(amount or 0)
            if currency == 'INR':
                return f"₹{num:,.0f}"
            elif currency == 'USD':
                return f"${num:,.2f}"
            elif currency == 'EUR':
                return f"€{num:,.2f}"
            elif currency == 'GBP':
                return f"£{num:,.2f}"
            else:
                return f"{num:,.0f} {currency}"
        except (ValueError, TypeError):
            return f"{amount} {currency}"

    def _generate_invoice_html(self, booking):
        """Generate professional HTML invoice email"""
        date_str = datetime.now().strftime("%d %B %Y")
        booking_id = booking.get('booking_id', 'N/A')
        customer_name = booking.get('customer_name', 'Valued Guest')
        customer_email = booking.get('customer_email', '')
        hotel_name = booking.get('hotel_name', 'Hotel')
        room_name = booking.get('room_name', '')
        checkin = self._format_date(booking.get('checkin', ''))
        checkout = self._format_date(booking.get('checkout', ''))
        nights = booking.get('nights', '')
        guests_info = booking.get('guests_info', '')
        amount = booking.get('amount', 0)
        currency = booking.get('currency', 'INR')
        formatted_amount = self._format_amount(amount, currency)
        
        # Calculate nights if not provided
        if not nights:
            try:
                ci = datetime.strptime(str(booking.get('checkin', '')), '%Y-%m-%d')
                co = datetime.strptime(str(booking.get('checkout', '')), '%Y-%m-%d')
                nights = (co - ci).days
            except (ValueError, TypeError):
                nights = ''
        
        nights_text = f"{nights} Night{'s' if nights != 1 else ''}" if nights else ''
        
        # Room name row (only if available)
        room_row = ''
        if room_name:
            room_row = f"""
            <tr>
                <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Room Type</td>
                <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">{room_name}</td>
            </tr>"""
        
        # Guests info row (only if available)
        guests_row = ''
        if guests_info:
            guests_row = f"""
            <tr>
                <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Guests</td>
                <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">{guests_info}</td>
            </tr>"""
        
        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    
    <!-- Wrapper -->
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 30px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);">
                    
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 24px; margin: 0 0 4px; font-weight: 700; letter-spacing: -0.5px;">C2C Journeys</h1>
                            <p style="color: rgba(255, 255, 255, 0.8); font-size: 13px; margin: 0;">Your Travel Partner</p>
                        </td>
                    </tr>
                    
                    <!-- Success Banner -->
                    <tr>
                        <td style="padding: 30px 40px 20px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%); border-radius: 12px; border: 1px solid #a7f3d0;">
                                <tr>
                                    <td style="padding: 20px 24px; text-align: center;">
                                        <div style="font-size: 36px; margin-bottom: 8px;">✅</div>
                                        <h2 style="color: #065f46; font-size: 18px; margin: 0 0 4px; font-weight: 700;">Booking Confirmed!</h2>
                                        <p style="color: #047857; font-size: 13px; margin: 0;">Your reservation has been successfully confirmed</p>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Greeting -->
                    <tr>
                        <td style="padding: 10px 40px 20px;">
                            <p style="color: #334155; font-size: 15px; line-height: 1.6; margin: 0;">
                                Dear <strong>{customer_name}</strong>,<br>
                                Thank you for booking with C2C Journeys! Here are your reservation details:
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Booking Reference -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f8fafc; border-radius: 10px; border: 1px solid #e2e8f0;">
                                <tr>
                                    <td style="padding: 16px 20px;">
                                        <table width="100%">
                                            <tr>
                                                <td style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600;">Booking Reference</td>
                                                <td style="color: #1e293b; font-size: 15px; font-weight: 700; text-align: right; font-family: 'Courier New', monospace;">{booking_id}</td>
                                            </tr>
                                            <tr>
                                                <td style="color: #64748b; font-size: 12px; text-transform: uppercase; letter-spacing: 1px; font-weight: 600; padding-top: 8px;">Booking Date</td>
                                                <td style="color: #475569; font-size: 13px; text-align: right; padding-top: 8px;">{date_str}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Hotel Details -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <h3 style="color: #1e3a5f; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px; border-bottom: 2px solid #2563eb; padding-bottom: 8px;">🏨 Hotel Details</h3>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Hotel</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 600; text-align: right; border-bottom: 1px solid #f1f5f9; font-size: 15px;">{hotel_name}</td>
                                </tr>{room_row}
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Check-in</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">📅 {checkin}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Check-out</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">📅 {checkout}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Duration</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">🌙 {nights_text}</td>
                                </tr>{guests_row}
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Amount -->
                    <tr>
                        <td style="padding: 0 40px 25px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #1e3a5f 0%, #1e40af 100%); border-radius: 12px;">
                                <tr>
                                    <td style="padding: 20px 24px;">
                                        <table width="100%">
                                            <tr>
                                                <td style="color: rgba(255, 255, 255, 0.8); font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">Total Amount Paid</td>
                                                <td style="color: #ffffff; font-size: 26px; font-weight: 700; text-align: right; letter-spacing: -0.5px;">{formatted_amount}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Important Info -->
                    <tr>
                        <td style="padding: 0 40px 25px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #fffbeb; border-radius: 10px; border: 1px solid #fde68a;">
                                <tr>
                                    <td style="padding: 16px 20px;">
                                        <h4 style="color: #92400e; font-size: 13px; margin: 0 0 8px; font-weight: 600;">⚠️ Important Information</h4>
                                        <ul style="color: #78350f; font-size: 12px; line-height: 1.8; margin: 0; padding-left: 16px;">
                                            <li>Please carry a valid government-issued photo ID at check-in</li>
                                            <li>Standard check-in time is 2:00 PM and check-out is 12:00 PM</li>
                                            <li>Any non-included taxes will be payable directly at the property</li>
                                        </ul>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    
                    <!-- Support -->
                    <tr>
                        <td style="padding: 0 40px 30px; text-align: center;">
                            <p style="color: #64748b; font-size: 13px; line-height: 1.6; margin: 0;">
                                Need help? Contact us at<br>
                                <a href="mailto:info@coasttocoastjourneys.com" style="color: #2563eb; text-decoration: none; font-weight: 600;">info@coasttocoastjourneys.com</a>
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="background-color: #f8fafc; padding: 20px 40px; text-align: center; border-top: 1px solid #e2e8f0;">
                            <p style="color: #94a3b8; font-size: 11px; margin: 0 0 4px;">
                                © 2026 Coast to Coast Journeys. All Rights Reserved.
                            </p>
                            <p style="color: #cbd5e1; font-size: 10px; margin: 0;">
                                c2cjourneys.com
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
    
</body>
</html>
"""


# Singleton
email_service = EmailService()
