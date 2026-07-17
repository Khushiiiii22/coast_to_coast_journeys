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
            
            # Nav bar
            new_content = new_content.replace('<span class="logo-text">Coast To Coast</span>', '<span class="logo-text">Coast To Coast Journeys</span>')
            new_content = new_content.replace('<span class="logo-text">Coast to Coast</span>', '<span class="logo-text">Coast To Coast Journeys</span>')
            
            # Footer logo
            new_content = new_content.replace('<span>C2C Journeys</span>', '<span>Coast To Coast Journeys</span>')
            
            # Copyright
            new_content = new_content.replace('&copy; 2026 C2C Journeys.', '&copy; 2026 Coast To Coast Journeys.')
            
            # C2C Journeys brand text (the "C2C Journeys is a customer-facing brand operated by Coast To Coast Journeys" line)
            new_content = new_content.replace('C2C Journeys is a customer-facing brand operated by Coast To Coast Journeys', 'Coast To Coast Journeys is a premium travel brand')
            
            # Other C2C Journeys text
            new_content = new_content.replace('alt="C2C Journeys"', 'alt="Coast To Coast Journeys"')
            new_content = new_content.replace('<strong>C2C Journeys</strong>', '<strong>Coast To Coast Journeys</strong>')
            
            # Any stray C2C Journeys text (except email sales@c2cjourneys.com)
            new_content = re.sub(r'\bC2C Journeys\b', 'Coast To Coast Journeys', new_content)
            
            # Since email has 'c2cjourneys', we don't need to worry as regex \b matches word boundaries and the email has @ and .
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
