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

    # Find the logo block
    # We look for <a href="index.html" class="logo"> ... </a>
    pattern_alt = re.compile(r'<a[^>]*href="index\.html"[^>]*class="logo"[^>]*>.*?</a>', re.DOTALL | re.IGNORECASE)
    
    # Check if we find it
    if pattern_alt.search(content):
        # We need to ensure we don't accidentally replace the FOOTER logo!
        # Since footer logo was recently updated to exactly match the index.html footer block
        # we know the footer doesn't have `<a href="index.html" class="logo">`.
        # It has `<div class="footer-logo">`.
        
        new_content = pattern_alt.sub(new_logo_html, content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated logo in {file_path}")
