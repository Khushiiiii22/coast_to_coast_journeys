import os

directory = 'templates'
old_sidebar_text1 = '<p>Coast To Coast Journeys is a premium travel brand</p>\n            <p>© 2026 Coast To Coast</p>'
old_sidebar_text2 = '<p>Coast To Coast Journeys is a premium travel brand</p>\n            <p>&copy; 2026 Coast To Coast</p>'
old_sidebar_text3 = '<p>Coast to Coast Journeys is a premium travel brand</p>\n            <p>© 2026 Coast To Coast</p>'

new_sidebar_text = '''<p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>
            <p>Your journey begins with us.</p>
            <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>'''


old_footer_text1 = '<p>Coast To Coast Journeys is a premium travel brand</p>\n                <p>&copy; 2026 Coast To Coast Journeys. All Rights Reserved.</p>'
old_footer_text2 = '<p>Coast To Coast is a customer-facing\n                    brand operated by Coast To Coast</p>\n                <p style="color: #94a3b8; font-size: 0.9rem;">&copy; 2026 Coast To Coast Journeys. All Rights Reserved.</p>'
old_footer_text3 = '<p style="color: #94a3b8; font-size: 0.9rem; margin-bottom: 5px;">Coast To Coast is a customer-facing\n                    brand operated by Coast To Coast</p>\n                <p style="color: #94a3b8; font-size: 0.9rem;">&copy; 2026 Coast To Coast Journeys. All Rights Reserved.</p>'
old_footer_text4 = '<p>Coast To Coast Journeys is a premium travel brand</p>\n            <p>&copy; 2026 Coast To Coast Journeys. All Rights Reserved.</p>'


new_footer_text = '''<p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>
                <p>Your journey begins with us.</p>
                <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>'''

# Read index.html to see exactly what we need to replace if the above aren't quite right.
for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            # The sidebar footer usually follows: <div class="sidebar-footer"> ... <p>...</p> <p>...</p> </div>
            import re
            
            # Use a safer regex that doesn't use .*? across the whole file
            # [^<]* matches anything except a '<' character, which is safer
            sidebar_pattern = r'(<div class="sidebar-footer">.*?<div class="sidebar-social">.*?</div>)\s*<p>[^<]*</p>\s*<p>[^<]*</p>'
            new_content = re.sub(sidebar_pattern, r'\1\n            <p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>\n            <p>Your journey begins with us.</p>\n            <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>', new_content, flags=re.DOTALL)
            
            footer_pattern = r'<div class="footer-bottom">\s*<p[^>]*>[^<]*</p>\s*<p[^>]*>[^<]*</p>\s*</div>'
            new_content = re.sub(footer_pattern, f'<div class="footer-bottom">\n                <p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>\n                <p>Your journey begins with us.</p>\n                <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>\n            </div>', new_content, flags=re.DOTALL)
            
            # Special case for some files that have styles inside the <p> tags
            footer_pattern_styled = r'<div class="footer-bottom">\s*<p[^>]*>Coast To Coast is a customer-facing[^<]*brand operated by Coast To Coast</p>\s*<p[^>]*>&copy; 2026 Coast To Coast Journeys\. All Rights Reserved\.</p>\s*</div>'
            new_content = re.sub(footer_pattern_styled, f'<div class="footer-bottom">\n                <p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>\n                <p>Your journey begins with us.</p>\n                <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>\n            </div>', new_content, flags=re.DOTALL)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

