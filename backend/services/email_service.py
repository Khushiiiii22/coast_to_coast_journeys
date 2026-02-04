
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import os
from datetime import datetime

class EmailService:
    def __init__(self, app=None):
        if app:
            self.init_app(app)

    def init_app(self, app):
        self.smtp_server = app.config.get('MAIL_SERVER', 'smtpout.secureserver.net')
        # Use Port 587 by default for cloud hosting to avoid Port 465 blocking
        self.smtp_port = int(app.config.get('MAIL_PORT', 587))
        self.use_tls = app.config.get('MAIL_USE_TLS', True)
        self.use_ssl = app.config.get('MAIL_USE_SSL', False)
        self.username = app.config.get('MAIL_USERNAME')
        self.password = app.config.get('MAIL_PASSWORD')
        self.default_sender = app.config.get('MAIL_DEFAULT_SENDER')
        
        # Log email configuration status for debugging
        if self.username and self.password:
            print(f"✅ Email service configured: {self.smtp_server}:{self.smtp_port} (SSL={self.use_ssl})")
            print(f"   📧 Sender: {self.default_sender}")
        else:
            print(f"⚠️  Email service NOT configured - missing MAIL_USERNAME or MAIL_PASSWORD")
            print(f"   Set these in Render Environment Variables:")
            print(f"   MAIL_SERVER, MAIL_PORT, MAIL_USERNAME, MAIL_PASSWORD, MAIL_DEFAULT_SENDER")
        
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """Send an email"""
        if not self.username or not self.password:
            print("⚠️ Email credentials not configured. Skipping email.")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.default_sender
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))

            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))

            # Add attachments
            if attachments:
                for filename, content in attachments.items():
                    part = MIMEApplication(content)
                    part.add_header('Content-Disposition', 'attachment', filename=filename)
                    msg.attach(part)

            # Connect to SMTP server (SSL or TLS)
            if self.use_ssl:
                # Use SSL (port 465)
                server = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, timeout=30)
            else:
                # Use TLS (port 587)
                server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=30)
                if self.use_tls:
                    server.starttls()
            
            server.set_debuglevel(0)  # Set to 1 for debug output
            server.login(self.username, self.password)
            server.send_message(msg)
            server.quit()
            
            print(f"✅ Email sent to {to_email}")
            return True
            
            print(f"✅ Email sent to {to_email}")
            return True
            
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
        
        # Send copy to owner (from .env MAIL_DEFAULT_SENDER)
        self._send_owner_notification(to_email, booking_details)
        
        return customer_email_sent

    def _send_owner_notification(self, guest_email, booking_details):
        """Send booking notification to owner/admin (from MAIL_DEFAULT_SENDER in .env)"""
        # Owner email is the default sender from .env
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
        sales_email = self.default_sender  # Use owner email from .env
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
