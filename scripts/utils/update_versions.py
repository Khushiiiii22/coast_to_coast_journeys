import os
import re

html_dir = 'templates'
for filename in os.listdir(html_dir):
    if filename.endswith('.html'):
        fp = os.path.join(html_dir, filename)
        with open(fp, 'r') as f:
            content = f.read()
            
        # Bump ?v=5.0 to ?v=6.0 for css and js
        content = re.sub(r'\?v=\d+\.\d+', '?v=6.0', content)
        
        with open(fp, 'w') as f:
            f.write(content)

print("Bumped cache versions.")
