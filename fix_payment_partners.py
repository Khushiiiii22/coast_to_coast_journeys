import os
import glob

# Add flex-wrap: wrap to payment partners flex container in all HTML files
html_files = glob.glob('templates/**/*.html', recursive=True)

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the exact inline style
    if 'style="display: flex; gap: 12px; align-items: center;"' in content:
        content = content.replace(
            'style="display: flex; gap: 12px; align-items: center;"',
            'style="display: flex; gap: 12px; align-items: center; flex-wrap: wrap;"'
        )
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Updated {file_path}")

# Update pages.css
with open('css/pages.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

if '.payment-partners {\n    margin-top: 1.5rem;\n    display: flex;\n    align-items: center;\n    gap: 0.75rem;\n' in css_content:
    css_content = css_content.replace(
        '.payment-partners {\n    margin-top: 1.5rem;\n    display: flex;\n    align-items: center;\n    gap: 0.75rem;\n',
        '.payment-partners {\n    margin-top: 1.5rem;\n    display: flex;\n    align-items: center;\n    gap: 0.75rem;\n    flex-wrap: wrap;\n'
    )
    with open('css/pages.css', 'w', encoding='utf-8') as f:
        f.write(css_content)
    print("Updated css/pages.css")
