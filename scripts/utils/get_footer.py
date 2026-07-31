import re

with open('templates/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the footer block
match = re.search(r'(<footer class="footer".*?</footer>)', content, re.DOTALL)
if match:
    footer_html = match.group(1)
    
    # Let's replace the footer-bottom content
    footer_bottom_match = re.search(r'(<div class="footer-bottom">.*?</div>)', footer_html, re.DOTALL)
    
    new_footer_bottom = """<div class="footer-bottom">
                <p>C2C Journeys is the official customer-facing brand operated by Coast to Coast Journeys.</p>
                <p>Your journey begins with us.</p>
                <p>&copy; 2026 Coast to Coast Journeys. All Rights Reserved.</p>
            </div>"""
            
    if footer_bottom_match:
        footer_html = footer_html.replace(footer_bottom_match.group(1), new_footer_bottom)
        
    with open('master_footer.html', 'w', encoding='utf-8') as f:
        f.write(footer_html)
    print("Extracted footer and saved to master_footer.html")
else:
    print("Could not find footer in index.html")
