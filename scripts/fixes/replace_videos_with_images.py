import os
import re
import glob

templates_dir = "/Users/khushi22/coasttocoast/templates"
html_files = glob.glob(os.path.join(templates_dir, "*.html"))

for filepath in html_files:
    filename = os.path.basename(filepath)
    with open(filepath, 'r') as f:
        content = f.read()

    # Determine which images to use based on filename
    hero_img = "../assets/images/hero-bg.png"
    footer_img = "../assets/images/footer-bg.png"

    if filename.startswith("flight"):
        hero_img = "../assets/images/flight-hero-bg.png"
        footer_img = "../assets/images/flight-footer-bg.png"
    elif filename.startswith("hotel") or filename in ["guest-details.html", "payment.html", "payment-checkout.html", "booking-confirmation.html", "cancellation-policy.html"]:
        # All these pages are related to hotel booking flow
        footer_img = "../assets/images/hotel-footer-bg.jpg"

    original_content = content

    # Replace Hero Video
    hero_pattern = re.compile(r'<video[^>]*class="hero-video-bg"[^>]*>[\s\S]*?</video>', re.IGNORECASE)
    hero_replacement = f'<img src="{hero_img}" alt="Background" class="hero-video-bg" style="pointer-events: none;">'
    content = hero_pattern.sub(hero_replacement, content)

    # Replace Footer Video
    footer_pattern = re.compile(r'<video[^>]*class="footer-video-bg"[^>]*>[\s\S]*?</video>', re.IGNORECASE)
    footer_replacement = f'<img src="{footer_img}" alt="Footer Background" class="footer-video-bg" style="pointer-events: none;">'
    content = footer_pattern.sub(footer_replacement, content)

    if content != original_content:
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"Updated {filename}")

print("Done replacing videos with static images.")
