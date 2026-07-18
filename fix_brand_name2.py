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
            
            # Remove "Journeys" from the capitalized string
            new_content = new_content.replace('Coast To Coast Journeys', 'Coast To Coast')
            
            # Also catch any "Coast to Coast Journeys" just in case
            new_content = new_content.replace('Coast to Coast Journeys', 'Coast To Coast')
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
