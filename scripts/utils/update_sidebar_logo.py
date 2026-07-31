import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True)

new_sidebar_logo_html = """<div class="sidebar-header">
            <div class="logo" style="display: flex; align-items: center; gap: 12px;">
                <img src="../assets/images/c2c-logo.png" alt="Coast To Coast" style="height: 48px;">
                <div class="logo-text-container">
                    <span class="logo-text-main">Coast To Coast</span>
                    <span class="logo-text-sub">Journeys</span>
                </div>
            </div>"""

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # We look for <div class="sidebar-header"> ... <span>...</span>
    pattern = re.compile(r'<div class="sidebar-header">\s*<img[^>]*>\s*<span>.*?</span>', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        new_content = pattern.sub(new_sidebar_logo_html, content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated sidebar logo in {file_path}")
