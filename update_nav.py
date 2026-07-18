import os
import re

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # 1. Update logo text
            new_content = re.sub(r'<span class="logo-text">.*?</span>', r'<span class="logo-text">Coast to Coast</span>', new_content)
            
            # 2. Add phone number to header-actions if not exists
            if '<div class="header-actions">' in new_content:
                # Extract the header-actions block
                match = re.search(r'<div class="header-actions">(.*?)</div>', new_content, re.DOTALL)
                if match:
                    header_actions_inner = match.group(1)
                    if 'tel:+18883159768' not in header_actions_inner and 'class="phone-link"' not in header_actions_inner:
                        phone_html = """
                    <a href="tel:+18883159768" class="phone-link" style="text-decoration: none; display: flex; align-items: center; gap: 8px; color: var(--primary); font-weight: 600; margin-right: 15px;">
                        <i class="fas fa-phone"></i>
                        <span>+1-888-315-9768</span>
                    </a>"""
                        
                        # Just insert it right after <div class="header-actions">
                        new_content = new_content.replace('<div class="header-actions">', '<div class="header-actions">' + phone_html)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
