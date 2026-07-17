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
            
            # Replace footer videos
            new_content = re.sub(r'src="../assets/videos/[a-zA-Z0-9_-]+footer-bg\.mp4"', 'src="../assets/videos/footer-background.mp4"', new_content)
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated footer video in {filepath}')

print('Done!')
