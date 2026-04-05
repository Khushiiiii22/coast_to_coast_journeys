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
        # Resend API Configuration
        self.resend_api_key = app.config.get('RESEND_API_KEY') or os.getenv('RESEND_API_KEY')
        
        # Verified sender
        self.default_sender = os.getenv('MAIL_DEFAULT_SENDER', 'info@coasttocoastjourneys.com')
        
        if self.api_key:
            print(f"✅ Email service configured with Brevo API")
        elif self.resend_api_key:
            print(f"✅ Email service configured with Resend API (as fallback)")
        else:
            print(f"⚠️ Email service NOT configured - missing API keys")
        
        print(f"   📧 Sender: {self.default_sender}")
        
    def send_email(self, to_email, subject, body, html_body=None, attachments=None):
        """Send an email using Brevo (primary) or Resend (fallback)"""
        # 1. Try Brevo first if configured
        if self.api_key:
            success = self._send_via_brevo(to_email, subject, body, html_body)
            if success:
                return True
            print("⚠️ Brevo failed. Attempting Resend fallback...")
            
        # 2. Try Resend if Brevo failed or is not configured
        if self.resend_api_key:
            return self._send_via_resend(to_email, subject, body, html_body)
            
        print("⚠️ No working email provider configured. Skipping email.")
        return False

    def _send_via_brevo(self, to_email, subject, body, html_body=None):
        """Internal helper for Brevo API"""
        try:
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": self.api_key
            }
            payload = {
                "sender": {"name": self.sender_name, "email": self.default_sender},
                "to": [{"email": to_email}],
                "subject": subject,
                "textContent": body
            }
            if html_body:
                payload["htmlContent"] = html_body
            
            response = requests.post(self.BREVO_API_URL, json=payload, headers=headers, timeout=10)
            if response.status_code in [200, 201, 202]:
                print(f"✅ Email sent via Brevo to {to_email}")
                return True
            print(f"❌ Brevo error: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Brevo failure: {str(e)}")
            return False

    def _send_via_resend(self, to_email, subject, body, html_body=None):
        """Internal helper for Resend API.
        
        Strategy (for environments where the sending domain is not verified):
        1. Always try onboarding@resend.dev first (Resend's built-in test sender).
        2. If the *recipient* is also not verified, redirect to OWNER_EMAIL.
        This guarantees at least one email arrives during testing.
        """
        try:
            url = "https://api.resend.com/emails"
            resend_headers = {
                "Authorization": f"Bearer {self.resend_api_key}",
                "Content-Type": "application/json"
            }
            owner_email = os.getenv('OWNER_EMAIL', 'khushikumari62406@gmail.com')
            
            # Always use onboarding@resend.dev to bypass domain verification in test mode
            sender = f"{self.sender_name} <onboarding@resend.dev>"

            payload = {
                "from": sender,
                "to": [to_email],
                "subject": subject,
                "text": body
            }
            if html_body:
                payload["html"] = html_body

            response = requests.post(url, json=payload, headers=resend_headers, timeout=10)

            if response.status_code in [200, 201]:
                print(f"✅ Email sent via Resend to {to_email}")
                return True

            # If recipient is not the verified owner, redirect to them
            if response.status_code == 403 and to_email != owner_email:
                print(f"⚠️ Resend blocked {to_email}. Redirecting to verified owner {owner_email} ...")
                redirect_notice = (
                    f"\n\n[TEST MODE] Original recipient: {to_email}\n"
                    f"Redirected to owner because Resend API is in Test Mode.\n"
                )
                redirect_html_banner = (
                    f"<div style='background:#fff4ed;border:1px solid #fdba74;"
                    f"border-radius:8px;padding:12px 16px;margin-bottom:20px;'>"
                    f"<strong style='color:#9a3412;'>⚠️ Test Mode Redirect</strong><br>"
                    f"Original recipient: <strong>{to_email}</strong><br>"
                    f"Showing to owner because Resend is in Test Mode.</div>"
                )
                payload["to"] = [owner_email]
                payload["subject"] = f"[REDIRECT → {to_email}] {subject}"
                payload["text"] = redirect_notice + payload.get("text", body)
                if "html" in payload:
                    payload["html"] = redirect_html_banner + payload["html"]

                r2 = requests.post(url, json=payload, headers=resend_headers, timeout=10)
                if r2.status_code in [200, 201]:
                    print(f"✅ Redirected email delivered to {owner_email} (was for {to_email})")
                    return True
                print(f"❌ Redirect also failed: {r2.status_code} - {r2.text}")
                return False

            print(f"❌ Resend error: {response.status_code} - {response.text}")
            return False
        except Exception as e:
            print(f"❌ Resend failure: {str(e)}")
            return False

    def send_flight_confirmation(self, to_email, booking_details):
        """Send flight booking confirmation with professional invoice"""
        airline = booking_details.get('airline', 'Airline')
        flight_number = booking_details.get('flight_number', '')
        subject = f"Flight Booking Confirmed ✅ — {airline} {flight_number} | C2C Journeys"

        invoice_html = self._generate_flight_invoice_html(booking_details)

        amount = booking_details.get('amount', 0)
        currency = booking_details.get('currency', 'INR')
        body = f"""
Dear {booking_details.get('customer_name', 'Passenger')},

Your flight booking has been confirmed!

Booking ID: {booking_details.get('booking_id', 'N/A')}
Flight: {airline} {flight_number}
Route: {booking_details.get('origin', '')} → {booking_details.get('destination', '')}
Date: {self._format_date(booking_details.get('date', ''))}
Total Amount: {self._format_amount(amount, currency)}

Thank you for choosing C2C Journeys!
        """

        customer_email_sent = self.send_email(to_email, subject, body, html_body=invoice_html)
        self._send_flight_owner_notification(to_email, booking_details)
        return customer_email_sent

    def _send_flight_owner_notification(self, guest_email, booking_details):
        """Send flight booking notification to owner/admin"""
        owner_email = os.getenv('CORPORATE_EMAIL', os.getenv('OWNER_EMAIL', 'info@coasttocoastjourneys.com'))
        subject = f"✈️ New Flight Booking — {booking_details.get('airline')} {booking_details.get('flight_number', '')} | {booking_details.get('booking_id', 'N/A')}"
        amount = booking_details.get('amount', 0)
        currency = booking_details.get('currency', 'INR')
        body = f"""
New Flight Booking Confirmed!

══════════════════════════════════════
BOOKING DETAILS
══════════════════════════════════════

Booking ID: {booking_details.get('booking_id', 'N/A')}

PASSENGER INFORMATION:
• Name: {booking_details.get('customer_name', 'N/A')}
• Email: {guest_email}
• Phone: {booking_details.get('customer_phone', 'N/A')}

FLIGHT DETAILS:
• Airline: {booking_details.get('airline', 'N/A')} {booking_details.get('flight_number', '')}
• Route: {booking_details.get('origin', '')} → {booking_details.get('destination', '')}
• Date: {booking_details.get('date', 'N/A')}
• Departure: {booking_details.get('depart_time', 'N/A')} | Arrival: {booking_details.get('arrive_time', 'N/A')}
• Class: {booking_details.get('flight_class', 'Economy')}
• Travelers: {booking_details.get('travelers', 1)}

PAYMENT:
• Amount: {self._format_amount(amount, currency)}

══════════════════════════════════════

This is an automated notification from C2C Journeys.
        """
        print(f"📧 Sending flight owner notification to {owner_email}")
        self.send_email(owner_email, subject, body)

    def _generate_flight_invoice_html(self, booking):
        """Generate professional HTML invoice email for flight bookings"""
        date_str = datetime.now().strftime("%d %B %Y")
        booking_id = booking.get('booking_id', 'N/A')
        customer_name = booking.get('customer_name', 'Valued Passenger')
        airline = booking.get('airline', 'Airline')
        flight_number = booking.get('flight_number', '')
        origin = booking.get('origin', '')
        destination = booking.get('destination', '')
        depart_time = booking.get('depart_time', '')
        arrive_time = booking.get('arrive_time', '')
        duration = booking.get('duration', '')
        flight_class = booking.get('flight_class', 'Economy').capitalize()
        travelers = booking.get('travelers', 1)
        flight_date = self._format_date(booking.get('date', ''))
        amount = booking.get('amount', 0)
        currency = booking.get('currency', 'INR')
        formatted_amount = self._format_amount(amount, currency)

        return f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f1f5f9; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;">
    <table width="100%" cellpadding="0" cellspacing="0" style="background-color: #f1f5f9; padding: 30px 0;">
        <tr>
            <td align="center">
                <table width="600" cellpadding="0" cellspacing="0" style="background-color: #ffffff; border-radius: 16px; overflow: hidden; box-shadow: 0 4px 24px rgba(0,0,0,0.08);">
                    <!-- Header -->
                    <tr>
                        <td style="background: linear-gradient(135deg, #1e3a5f 0%, #2563eb 100%); padding: 32px 40px; text-align: center;">
                            <h1 style="color: #ffffff; font-size: 24px; margin: 0 0 4px; font-weight: 700;">C2C Journeys</h1>
                            <p style="color: rgba(255,255,255,0.8); font-size: 13px; margin: 0;">✈️ Flight Booking Confirmation</p>
                        </td>
                    </tr>
                    <!-- Success Banner -->
                    <tr>
                        <td style="padding: 30px 40px 20px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #ecfdf5, #d1fae5); border-radius: 12px; border: 1px solid #a7f3d0;">
                                <tr>
                                    <td style="padding: 20px 24px; text-align: center;">
                                        <div style="font-size: 36px; margin-bottom: 8px;">✅</div>
                                        <h2 style="color: #065f46; font-size: 18px; margin: 0 0 4px; font-weight: 700;">Flight Booking Confirmed!</h2>
                                        <p style="color: #047857; font-size: 13px; margin: 0;">Your flight has been successfully booked</p>
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
                                Thank you for choosing C2C Journeys! Your flight booking details are below:
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
                    <!-- Route Visual -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <table width="100%" cellpadding="0" cellspacing="0" style="background: linear-gradient(135deg, #eff6ff, #dbeafe); border-radius: 12px; border: 1px solid #bfdbfe; padding: 20px;">
                                <tr>
                                    <td style="padding: 20px;">
                                        <div style="text-align: center; margin-bottom: 8px; font-size: 12px; font-weight: 600; color: #1e40af; text-transform: uppercase; letter-spacing: 1px;">{airline} · {flight_number}</div>
                                        <table width="100%" cellpadding="0" cellspacing="0">
                                            <tr>
                                                <td style="text-align: center; width: 35%;">
                                                    <div style="font-size: 28px; font-weight: 800; color: #0f172a;">{depart_time}</div>
                                                    <div style="font-size: 20px; font-weight: 700; color: #1e40af;">{origin}</div>
                                                </td>
                                                <td style="text-align: center; width: 30%;">
                                                    <div style="font-size: 11px; color: #64748b; margin-bottom: 6px;">{duration}</div>
                                                    <div style="height: 2px; background: linear-gradient(to right, #2563eb, #7c3aed); border-radius: 2px; position: relative;">
                                                        <span style="position: absolute; top: -8px; left: 50%; transform: translateX(-50%); font-size: 14px;">✈️</span>
                                                    </div>
                                                    <div style="font-size: 11px; color: #10b981; font-weight: 600; margin-top: 8px;">Non-stop</div>
                                                </td>
                                                <td style="text-align: center; width: 35%;">
                                                    <div style="font-size: 28px; font-weight: 800; color: #0f172a;">{arrive_time}</div>
                                                    <div style="font-size: 20px; font-weight: 700; color: #1e40af;">{destination}</div>
                                                </td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                        </td>
                    </tr>
                    <!-- Flight Details -->
                    <tr>
                        <td style="padding: 0 40px 20px;">
                            <h3 style="color: #1e3a5f; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; margin: 0 0 12px; border-bottom: 2px solid #2563eb; padding-bottom: 8px;">✈️ Flight Details</h3>
                            <table width="100%" cellpadding="0" cellspacing="0">
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Travel Date</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 600; text-align: right; border-bottom: 1px solid #f1f5f9;">📅 {flight_date}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Class</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">🪑 {flight_class}</td>
                                </tr>
                                <tr>
                                    <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Travelers</td>
                                    <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">👥 {travelers} Passenger(s)</td>
                                </tr>
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
                                                <td style="color: rgba(255,255,255,0.8); font-size: 13px; text-transform: uppercase; letter-spacing: 1px;">Total Amount Paid</td>
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
                                            <li>Please arrive at the airport at least 2 hours before departure</li>
                                            <li>Carry a valid government-issued photo ID / Passport</li>
                                            <li>Our team will call you shortly to confirm your booking</li>
                                            <li>Check airline website for baggage policy and web check-in</li>
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
                            <p style="color: #94a3b8; font-size: 11px; margin: 0 0 4px;">© 2026 Coast to Coast Journeys. All Rights Reserved.</p>
                            <p style="color: #cbd5e1; font-size: 10px; margin: 0;">coasttocoastjourneys.com</p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""

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
        # Priority: OWNER_EMAIL (verified for Resend test) > CORPORATE_EMAIL > default
        owner_email = os.getenv('OWNER_EMAIL', os.getenv('CORPORATE_EMAIL', 'info@coasttocoastjourneys.com'))
        
        hotel_name = booking_details.get('hotel_name', 'Hotel')
        subject = f"🔔 NEW BOOKING: {hotel_name} | {booking_details.get('booking_id', 'N/A')}"
        
        # We send the same professional invoice to the owner so they see exactly what the guest sees
        invoice_html = self._generate_invoice_html(booking_details)
        
        # Add a small admin header to the HTML if it exists
        admin_header = f"""
        <div style="background: #fef3c7; padding: 15px; text-align: center; border-bottom: 2px solid #fde68a; font-family: sans-serif;">
            <strong style="color: #92400e;">ADMIN NOTIFICATION</strong><br>
            <span style="color: #d97706; font-size: 13px;">New booking received from <strong>{guest_email}</strong></span>
        </div>
        """
        invoice_html = admin_header + invoice_html

        print(f"📧 Sending owner notification to {owner_email}")
        self.send_email(owner_email, subject, "New booking received. See HTML version for details.", html_body=invoice_html)

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
        customer_phone = booking.get('customer_phone', '')
        hotel_name = booking.get('hotel_name', 'Hotel')
        room_name = booking.get('room_name', '')
        meal_plan = booking.get('meal_plan', '') or booking.get('meal_info', '')
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

        # Meal plan row (only if not nomeal)
        meal_row = ''
        if meal_plan and meal_plan.lower() not in ('nomeal', 'room only', 'no meal', 'none', ''):
            meal_row = f"""
            <tr>
                <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Meal Plan</td>
                <td style="padding: 12px 0; color: #065f46; font-weight: 600; text-align: right; border-bottom: 1px solid #f1f5f9;">🍽️ {meal_plan}</td>
            </tr>"""
        
        # Guests info row (only if available)
        guests_row = ''
        if guests_info:
            guests_row = f"""
            <tr>
                <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Guests</td>
                <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">{guests_info}</td>
            </tr>"""
            
        # Phone row (only if available)
        phone_row = ''
        if customer_phone:
            phone_row = f"""
            <tr>
                <td style="padding: 12px 0; color: #64748b; border-bottom: 1px solid #f1f5f9;">Contact Phone</td>
                <td style="padding: 12px 0; color: #1e293b; font-weight: 500; text-align: right; border-bottom: 1px solid #f1f5f9;">{customer_phone}</td>
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
                                </tr>{room_row}{meal_row}
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
                                </tr>{guests_row}{phone_row}
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
