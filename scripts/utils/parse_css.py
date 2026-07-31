import re

with open('css/main.css', 'r', encoding='utf-8') as f:
    css = f.read()

# very basic parsing to find blocks with display: none
blocks = re.findall(r'([^{}]+)\s*{[^}]*display\s*:\s*none[^}]*}', css)
for b in blocks:
    print(b.strip())
