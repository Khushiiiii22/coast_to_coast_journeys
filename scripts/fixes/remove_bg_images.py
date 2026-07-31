import os
import re

html_dir = 'templates'
for filename in os.listdir(html_dir):
    if filename.endswith('.html'):
        filepath = os.path.join(html_dir, filename)
        with open(filepath, 'r') as f:
            content = f.read()
        
        # Remove footer background images
        content = re.sub(r'<img[^>]*class="footer-video-bg"[^>]*>', '', content)
        # Remove hero background images
        content = re.sub(r'<img[^>]*class="hero-video-bg"[^>]*>', '', content)
        
        with open(filepath, 'w') as f:
            f.write(content)
print("Removed background images from HTML files.")
