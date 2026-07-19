import re

with open('css/main.css', 'r', encoding='utf-8') as f:
    css_content = f.read()

# Replace the media query for logo-text-main and logo-text-sub with a display: none for the container
old_media = """@media (max-width: 768px) {
    .logo-text-main {
        font-size: 1.1rem;
    }
    .logo-text-sub {
        font-size: 0.6rem;
        letter-spacing: 2px;
    }
}"""
new_media = """@media (max-width: 992px) {
    .logo-text-container {
        display: none !important;
    }
    .logo img {
        height: 36px; /* slightly smaller on mobile to fit nicely */
    }
}"""

if old_media in css_content:
    css_content = css_content.replace(old_media, new_media)
else:
    # Append if not found exactly
    css_content += "\n" + new_media

with open('css/main.css', 'w', encoding='utf-8') as f:
    f.write(css_content)

print("Updated mobile logo css")
