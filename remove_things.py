import os
import glob
import re

template_dir = 'templates'
html_files = glob.glob(os.path.join(template_dir, '*.html'))

tawk_regex = re.compile(r'<!--Start of Tawk\.to Script-->.*?<!--End of Tawk\.to Script-->', re.DOTALL | re.IGNORECASE)
whatsapp_regex = re.compile(r'<a[^>]*href="https://wa\.me/[^>]*>.*?WhatsApp.*?</a>', re.DOTALL | re.IGNORECASE)
whatsapp_link_regex = re.compile(r'<a[^>]*href="whatsapp://[^>]*>.*?WhatsApp.*?</a>', re.DOTALL | re.IGNORECASE)

join_club_regex = re.compile(r'<!-- Signup Promo Modal -->.*?</div>\s*</div>\s*</div>', re.DOTALL)

for filepath in html_files:
    with open(filepath, 'r') as f:
        content = f.read()

    original_content = content
    
    # 1. Remove tawk.to from all pages EXCEPT index.html
    if not filepath.endswith('index.html'):
        content = tawk_regex.sub('', content)

    # 2. Remove whatsapp links from everywhere
    content = whatsapp_regex.sub('', content)
    content = whatsapp_link_regex.sub('', content)
    
    # Also remove any list item with WhatsApp text
    content = re.compile(r'<li[^>]*>\s*<strong>WhatsApp:</strong>.*?</li>', re.DOTALL | re.IGNORECASE).sub('', content)

    # 3. Remove "join the club" from everywhere (it's mainly in index.html)
    content = join_club_regex.sub('', content)

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filepath}")
