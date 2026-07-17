import os
import re

directory = 'templates'
replacements = {
    '+91 99345 47108': '+1-888-315-9768',
    '+919934547108': '+18883159768',
    '919934547108': '18883159768',
    'sales@coasttocoastjourneys.com': 'Sales@c2cjourneys.com'
}

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
                
            new_content = content
            for old, new in replacements.items():
                # Case insensitive replace for the email
                if old == 'sales@coasttocoastjourneys.com':
                    new_content = re.sub(old, new, new_content, flags=re.IGNORECASE)
                else:
                    new_content = new_content.replace(old, new)
                    
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
