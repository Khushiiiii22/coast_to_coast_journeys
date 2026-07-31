import os
import re

hamburger_html = """                <!-- Hamburger Menu Button -->
                <button class="hamburger-menu" id="hamburgerMenu" aria-label="Open navigation menu">
                    <span></span>
                    <span></span>
                    <span></span>
                </button>
"""

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if it already has the hamburger menu
            if 'id="hamburgerMenu"' not in content:
                # Find where to inject it. Usually right after <div class="header-content">
                # We'll use regex to find <div class="header-content">\s*<a href="index.html" class="logo">
                # or just <div class="header-content">
                
                # Try to find header-content
                match = re.search(r'(<div\s+class="header-content"\s*>)\s*(<a\s+href="[^"]*"\s+class="logo"\s*>)', content, re.IGNORECASE)
                if match:
                    new_content = content[:match.start(2)] + hamburger_html + content[match.start(2):]
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"Injected hamburger menu into {filepath}")
                else:
                    print(f"Could not find injection point in {filepath}")

