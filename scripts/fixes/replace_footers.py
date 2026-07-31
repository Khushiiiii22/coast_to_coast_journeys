import glob
import re

with open('master_footer.html', 'r', encoding='utf-8') as f:
    master_footer = f.read()

html_files = glob.glob('templates/**/*.html', recursive=True)

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Skip files that don't have a footer tag
    if '<footer' not in content:
        print(f"Skipped {file_path} (no footer found)")
        continue

    # Replace the entire footer block
    new_content, count = re.subn(r'(<footer[^>]*>.*?</footer>)', lambda m: master_footer, content, flags=re.DOTALL)
    
    if count > 0:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Replaced footer in {file_path}")
    else:
        print(f"Could not match footer block in {file_path}")

