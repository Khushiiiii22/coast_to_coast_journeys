import os
import re

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace main.js?v=3 with main.js?v=3.1
            new_content = content.replace('main.js?v=3"', 'main.js?v=3.1"')
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f"Busted JS cache for {filepath}")

