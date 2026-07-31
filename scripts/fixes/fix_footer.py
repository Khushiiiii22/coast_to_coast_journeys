import os

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # Part 1: Replace videos for specific pages
            if file.startswith('flight'):
                new_content = new_content.replace('footer-background.mp4', 'flight-footer-bg.mp4')
            elif file.startswith('hotel'):
                new_content = new_content.replace('footer-background.mp4', 'hotel-footer-bg.mp4')
            
            # Part 2: Replace "Coast To Coast" with "Coast To Coast Journeys" in the footer sections
            
            # 1. The footer-bottom brand line
            new_content = new_content.replace('<p>Coast To Coast is a premium travel brand</p>', '<p>Coast To Coast Journeys is a premium travel brand</p>')
            # If they used small c
            new_content = new_content.replace('<p>Coast to Coast is a premium travel brand</p>', '<p>Coast To Coast Journeys is a premium travel brand</p>')
            
            # 2. The footer-bottom copyright line
            new_content = new_content.replace('&copy; 2026 Coast To Coast. All Rights Reserved.', '&copy; 2026 Coast To Coast Journeys. All Rights Reserved.')
            new_content = new_content.replace('&copy; 2026 Coast to Coast. All Rights Reserved.', '&copy; 2026 Coast To Coast Journeys. All Rights Reserved.')
            
            # 3. The sidebar-footer copyright line
            new_content = new_content.replace('&copy; 2026 Coast To Coast</p>', '&copy; 2026 Coast To Coast Journeys</p>')
            new_content = new_content.replace('&copy; 2026 Coast to Coast</p>', '&copy; 2026 Coast To Coast Journeys</p>')
            
            # 4. The footer-logo span
            old_footer_logo = """<div class="footer-logo">
                        <img src="../assets/images/c2c-logo.png" alt="Coast To Coast">
                        <span>Coast To Coast</span>
                    </div>"""
            new_footer_logo = """<div class="footer-logo">
                        <img src="../assets/images/c2c-logo.png" alt="Coast To Coast">
                        <span>Coast To Coast Journeys</span>
                    </div>"""
            new_content = new_content.replace(old_footer_logo, new_footer_logo)
            
            # Alternate spacing
            old_footer_logo2 = """<div class="footer-logo">
                    <img src="../assets/images/c2c-logo.png" alt="Coast To Coast">
                    <span>Coast to Coast</span>
                </div>"""
            new_footer_logo2 = """<div class="footer-logo">
                    <img src="../assets/images/c2c-logo.png" alt="Coast To Coast">
                    <span>Coast To Coast Journeys</span>
                </div>"""
            new_content = new_content.replace(old_footer_logo2, new_footer_logo2)
            
            # 5. The sidebar-header span (maybe user considers sidebar part of footer?)
            # Actually, "in all pages in mobile as well as the desktop view".
            # The user explicitly said "only in the footer part". I shouldn't change the main header. 
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Updated {filepath}")

print("Done updating footer text and videos.")

