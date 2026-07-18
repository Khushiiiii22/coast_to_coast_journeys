import os
import re

directory = 'templates'

legal_re = re.compile(r'(<div class="footer-col">\s*<h4>Legal</h4>\s*<ul>\s*<li><a href="privacy-policy\.html">Privacy Policy</a></li>\s*<li><a href="terms\.html">Terms & Conditions</a></li>\s*<li><a href="refund-policy\.html">Refund Policy</a></li>\s*<li><a href="cancellation-policy\.html">Cancellation Policy</a></li>\s*</ul>\s*</div>)', re.DOTALL)

services_html = """\\1

                <div class="footer-col">
                    <h4>Services</h4>
                    <ul>
                        <li><a href="flight-booking.html">Flight Booking</a></li>
                        <li><a href="hotel-booking.html">Hotel Booking</a></li>
                    </ul>
                </div>"""

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it has a footer
            if '<footer' in content and '<h4>Legal</h4>' in content:
                # Check if Services is already there
                if '<h4>Services</h4>' not in content:
                    new_content = legal_re.sub(services_html, content)
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f'Updated {filepath}')

print('Done!')
