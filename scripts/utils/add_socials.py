import os
import re

directory = 'templates'

services_re = re.compile(r'(<div class="footer-col">\s*<h4>Services</h4>\s*<ul>\s*<li><a href="flight-booking\.html">Flight Booking</a></li>\s*<li><a href="hotel-booking\.html">Hotel Booking</a></li>\s*</ul>\s*</div>)', re.DOTALL)

socials_html = """\\1

                <div class="footer-col">
                    <h4>Follow Us</h4>
                    <div style="display: flex; gap: 15px; margin-top: 10px;">
                        <a href="https://www.facebook.com/profile.php?id=61594212966141" target="_blank" rel="noopener noreferrer" style="font-size: 1.5rem; transition: transform 0.3s; color: #1877F2;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                            <i class="fab fa-facebook"></i>
                        </a>
                        <a href="https://www.instagram.com/c2cjourneys/" target="_blank" rel="noopener noreferrer" style="font-size: 1.5rem; transition: transform 0.3s; color: #E4405F;" onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                            <i class="fab fa-instagram"></i>
                        </a>
                    </div>
                </div>"""

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            # Skip master_footer.html as we already modified it (or we can let regex run over it)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it has Services
            if '<h4>Services</h4>' in content:
                # Check if Follow Us is not already there
                if '<h4>Follow Us</h4>' not in content:
                    new_content = services_re.sub(socials_html, content)
                    if new_content != content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(new_content)
                        print(f'Updated {filepath}')

print('Done!')
