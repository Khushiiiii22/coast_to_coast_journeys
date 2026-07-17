import os
import re

directory = 'templates'

messy_phone_re = re.compile(r'\s*<a href="tel:\+18883159768" class="phone-link" style="text-decoration: none; display: flex; align-items: center; gap: 8px; color: var\(--primary\); font-weight: 600; margin-right: 15px;">\s*<i class="fas fa-phone"></i>\s*<span>\+1-888-315-9768</span>\s*</a>', re.DOTALL)

clean_phone_html = """
                    <a href="tel:+18883159768" class="phone-link">
                        <i class="fas fa-phone"></i>
                        <span>+1-888-315-9768</span>
                    </a>"""

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Remove the messy phone link
            new_content = messy_phone_re.sub('', content)
            
            # Now, if the file doesn't have ANY phone-link, we add the clean one
            if 'class="phone-link"' not in new_content and '<div class="header-actions">' in new_content:
                # Add it before the btn-outline
                new_content = re.sub(r'(<a href="[^"]*" class="btn btn-outline">)', clean_phone_html + r'\n                    \1', new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
