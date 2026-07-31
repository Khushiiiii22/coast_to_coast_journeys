import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True)

new_logo_html = """<a href="index.html" class="logo">
                    <img src="../assets/images/c2c-logo.png" alt="Coast To Coast">
                    <div class="logo-text-container">
                        <span class="logo-text-main">Coast To Coast</span>
                        <span class="logo-text-sub">Journeys</span>
                    </div>
                </a>"""

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Find the logo block using regex
    # Match <a href="index.html" class="logo"> ... </a>
    pattern = re.compile(r'<a href="index\.html"\s+class="logo">\s*<img[^>]*>\s*<span class="logo-text">.*?</span>\s*</a>', re.DOTALL | re.IGNORECASE)
    
    # We also might find cases without the logo-text span, or different inner contents.
    pattern_alt = re.compile(r'<a href="index\.html"\s+class="logo">.*?</a>', re.DOTALL | re.IGNORECASE)
    
    if pattern.search(content):
        new_content = pattern.sub(new_logo_html, content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated logo in {file_path}")
    elif pattern_alt.search(content):
        # We need to ensure we don't accidentally replace the FOOTER logo!
        # The footer logo usually doesn't have class="logo" directly, but let's be careful.
        pass
