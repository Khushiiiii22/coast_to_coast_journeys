import os
import sys
import base64
from datetime import datetime
from playwright.sync_api import sync_playwright

LOGO_PATH = '/Users/priyeshsrivastava/Travel production/assets/images/c2c-logo.png'
TEMPLATES_DIR = '/Users/priyeshsrivastava/Travel production/backend/templates'
OUTPUT_DIR = '/Users/priyeshsrivastava/Travel production/backend/output_test'
ARTIFACT_DIR = '/Users/priyeshsrivastava/.gemini/antigravity-ide/brain/5b1df49b-ad62-43f5-81c3-b25802dde9a7'

def create_qr_code(text):
    try:
        import qrcode
        from io import BytesIO
        qr = qrcode.QRCode(version=1, box_size=5, border=1)
        qr.add_data(text)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0a2540", back_color="white")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        return f'<img src="data:image/png;base64,{img_str}" style="width:75px;height:75px;">'
    except ImportError:
        return '<div style="width:75px;height:75px;background:#eee;text-align:center;line-height:75px;font-size:9px;border-radius:4px;">[QR]</div>'

def get_logo_data_uri():
    with open(LOGO_PATH, 'rb') as f:
        logo_b64 = base64.b64encode(f.read()).decode()
    return f'data:image/png;base64,{logo_b64}'

def generate():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    logo_uri = get_logo_data_uri()
    qr_html = create_qr_code('https://coasttocoastjourneys.com/verify/CTC-20260710-XYZ123')

    data = {
        'logo_data_uri': logo_uri,
        'qr_code_html': qr_html,
        'ein': 'XX-XXXXXXX',
        'invoice_number': 'INV-2026-00987',
        'booking_id': 'CTC-20260710-XYZ123',
        'issue_date': 'July 10, 2026',
        'due_date': 'July 10, 2026',
        'transaction_id': 'txn_3M9a7bZ123456',
        'payment_status': 'PAID',
        'guest_name': 'Priyesh Srivastava',
        'guest_email': 'priyesh@example.com',
        'guest_phone': '+1 234 567 8900',
        'billing_address': '456 Tech Avenue, San Francisco, CA 94105, USA',
        'supplier_ref': 'EXP-99887766',
        'voucher_number': 'VCH-2026-88332211',
        'hotel_name': 'The Ritz-Carlton, Los Angeles',
        'star_rating': '★★★★★',
        'hotel_address': '900 W Olympic Blvd, Los Angeles, CA 90015, USA',
        'hotel_phone': '+1 213-743-8800',
        'hotel_email': 'reservations.la@ritzcarlton.com',
        'checkin': 'July 20, 2026',
        'checkout': 'July 25, 2026',
        'checkin_time': '3:00 PM',
        'checkout_time': '11:00 AM',
        'nights': '5',
        'room_type': 'Deluxe King Room',
        'meal_plan': 'Breakfast Included',
        'preferences': '1 King Bed, Non-smoking',
        'adults': '2',
        'children': '0',
        'room_count': '1',
        'additional_guests': 'Jane Doe',
        'currency': 'USD',
        'rate_per_night': '220.00',
        'room_charges': '1,100.00',
        'taxes_fees': '150.00',
        'service_fee': '50.00',
        'discount': '50.00',
        'total_amount': '1,250.00',
        'amount_paid': '1,250.00',
        'balance_due': '$0.00 (Fully Prepaid)',
        'payment_method': 'Credit Card',
        'card_type': 'Visa ending in 4242',
        'paid_date': 'July 10, 2026',
        'included_services': 'Daily Breakfast, High-Speed WiFi, Fitness Center & Pool Access',
        'not_included_services': 'Valet Parking ($45/night), Spa Services, Mini-bar',
        'cancellation_policy': "Free cancellation up to 48 hours before check-in. Late cancellations or no-shows will be charged the first night's rate.",
        'city_tax_policy': 'A local city tax of $4.50/night is not included and must be paid directly at the hotel.',
        'sales_tax': 'Included in Taxes & Fees',
    }

    # Process Invoice
    with open(os.path.join(TEMPLATES_DIR, 'pdf', 'invoice.html'), 'r') as f:
        invoice_html = f.read()
    for key, value in data.items():
        invoice_html = invoice_html.replace('{{' + key + '}}', str(value))

    invoice_temp = os.path.join(OUTPUT_DIR, 'final_invoice.html')
    with open(invoice_temp, 'w') as f:
        f.write(invoice_html)

    # Process Voucher
    with open(os.path.join(TEMPLATES_DIR, 'pdf', 'ticket.html'), 'r') as f:
        ticket_html = f.read()
    for key, value in data.items():
        ticket_html = ticket_html.replace('{{' + key + '}}', str(value))

    ticket_temp = os.path.join(OUTPUT_DIR, 'final_voucher.html')
    with open(ticket_temp, 'w') as f:
        f.write(ticket_html)

    # Verify logo is embedded
    if 'iVBORw0KGgo' in invoice_html:
        print("✅ Logo base64 data is embedded in Invoice HTML")
    else:
        print("❌ Logo NOT embedded in Invoice HTML!")
    if 'iVBORw0KGgo' in ticket_html:
        print("✅ Logo base64 data is embedded in Voucher HTML")
    else:
        print("❌ Logo NOT embedded in Voucher HTML!")

    # Generate PDFs
    print("\n🚀 Generating PDFs with Playwright...")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Invoice PDF
        page.goto('file://' + os.path.abspath(invoice_temp))
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)  # Extra wait for images to render
        
        invoice_pdf = os.path.join(OUTPUT_DIR, 'C2C_Invoice.pdf')
        page.pdf(path=invoice_pdf, format='A4', print_background=True,
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        print(f"✅ Invoice PDF: {invoice_pdf}")

        # Invoice Screenshot
        page.screenshot(path=os.path.join(ARTIFACT_DIR, 'invoice_final.png'), full_page=True)
        print("✅ Invoice screenshot saved")

        # Voucher PDF
        page.goto('file://' + os.path.abspath(ticket_temp))
        page.wait_for_load_state('networkidle')
        page.wait_for_timeout(1000)

        voucher_pdf = os.path.join(OUTPUT_DIR, 'C2C_Voucher.pdf')
        page.pdf(path=voucher_pdf, format='A4', print_background=True,
                 margin={'top': '0', 'right': '0', 'bottom': '0', 'left': '0'})
        print(f"✅ Voucher PDF: {voucher_pdf}")

        # Voucher Screenshot
        page.screenshot(path=os.path.join(ARTIFACT_DIR, 'voucher_final.png'), full_page=True)
        print("✅ Voucher screenshot saved")

        browser.close()

    print("\n🎉 All done! PDFs and screenshots generated.")

if __name__ == '__main__':
    generate()
