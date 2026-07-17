import os
import re

directory = 'templates'

# Regex to match the 'Our Office' contact item
# Matches from <div class="contact-item"> to the closing </div> of that item
# only if it contains 'Our Office'
office_re = re.compile(r'<div class="contact-item">\s*<div class="contact-icon">\s*<i class="[^"]*map-marker-alt[^"]*"></i>\s*</div>\s*<h4>Our Office</h4>\s*<p>.*?</p>\s*</div>', re.DOTALL)

# Regex to match the social-links div (in the contact section)
social_links_re = re.compile(r'<div class="social-links">.*?</div>', re.DOTALL)

# Regex to match the footer-section containing "Connect With Us"
connect_with_us_re = re.compile(r'<div class="footer-section">\s*<h4>Connect With Us</h4>\s*<div class="footer-social">.*?</div>\s*</div>', re.DOTALL)

# We might also have a simpler structure for connect with us, let's catch anything with Connect With Us
# But wait, let's just make it broad enough for the footer block.
connect_broad_re = re.compile(r'<div class="footer-[a-zA-Z0-9_-]*">\s*<h[1-6]>Connect With Us</h[1-6]>.*?</div>\s*</div>', re.DOTALL)

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            new_content = content
            
            # Remove "Our Office" block
            new_content = office_re.sub('', new_content)
            
            # Remove "social-links" block (from contact section)
            new_content = social_links_re.sub('', new_content)
            
            # Remove "Connect With Us" footer section
            new_content = connect_with_us_re.sub('', new_content)
            new_content = connect_broad_re.sub('', new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
