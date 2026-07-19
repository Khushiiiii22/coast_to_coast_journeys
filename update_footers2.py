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
            
            # Replace footer-bottom content
            footer_bottom_pattern = r'<div class="footer-bottom">\s*<p>.*?</p>\s*<p>.*?</p>\s*</div>'
            new_footer_bottom = """<div class="footer-bottom">
                <p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>
                <p>Your journey begins with us.</p>
                <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>
            </div>"""
            new_content = re.sub(footer_bottom_pattern, new_footer_bottom, new_content, flags=re.DOTALL)
            
            # Replace sidebar-footer content
            sidebar_footer_pattern = r'(<div class="sidebar-footer">\s*<div class="sidebar-social">.*?</div>)\s*<p>.*?</p>\s*<p>.*?</p>'
            new_sidebar_footer = r'\1\n            <p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>\n            <p>Your journey begins with us.</p>\n            <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>'
            new_content = re.sub(sidebar_footer_pattern, new_sidebar_footer, new_content, flags=re.DOTALL)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

print("Footer update complete.")
