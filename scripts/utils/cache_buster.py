import os
import re

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace main.js?v=2 with main.js?v=3
            new_content = content.replace('main.js?v=2', 'main.js?v=3')
            new_content = new_content.replace('flight-booking.js?v=2', 'flight-booking.js?v=3')
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Busted cache for {filepath}")

