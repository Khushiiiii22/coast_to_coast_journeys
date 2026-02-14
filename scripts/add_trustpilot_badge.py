#!/usr/bin/env python3
"""
Script to add Trustpilot badge to all footer sections in HTML files.
"""

import os
import re

TRUSTPILOT_BADGE_HTML = '''            <!-- Trustpilot Review Badge -->
            <div class="trustpilot-badge" style="margin: 20px 0; text-align: center;">
                <a href="https://www.trustpilot.com/review/coasttocoastjourneys.com" target="_blank"
                    rel="noopener noreferrer"
                    style="display: inline-flex; align-items: center; gap: 8px; background: #fff; color: #191919; padding: 8px 16px; border-radius: 6px; text-decoration: none; font-size: 0.85rem; font-weight: 600; transition: transform 0.2s, box-shadow 0.2s;"
                    onmouseover="this.style.transform='translateY(-2px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)';"
                    onmouseout="this.style.transform=''; this.style.boxShadow='';">
                    Review us on
                    <img src="https://cdn.trustpilot.net/brand-assets/4.1.0/logo-black.svg" alt="Trustpilot"
                        style="height: 18px; width: auto;">
                   <span style="color: #00b67a; font-size: 1rem;">★</span>
                </a>
            </div>
'''

FILES_TO_UPDATE = [
    'index.html',
    'flight-booking.html',
    'hotel-booking.html',
    'visa.html',
    'hotel-results.html',
    'payment.html',
    'booking-confirmation.html',
    'terms.html',
    'privacy-policy.html',
    'refund-policy.html',
    'cancellation-policy.html',
    'faqs.html',
    'payment-checkout.html',
    'my-bookings.html',
    'wishlist.html',
    'profile.html',
]

def add_trustpilot_badge(file_path):
    """Add Trustpilot badge to a single HTML file"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if already has trustpilot
    if 'trustpilot' in content.lower():
        print(f"  ✅ {os.path.basename(file_path)} - Already has Trustpilot badge")
        return False
    
    # Try to find the footer-bottom div and insert before it
    pattern = r'(\s*)(<div class="footer-bottom">)'
    
    if re.search(pattern, content):
        # Add the badge before footer-bottom
        new_content = re.sub(
            pattern,
            r'\1' + TRUSTPILOT_BADGE_HTML + '\n\1' + r'\2',
            content,
            count=1
        )
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"  ✅ {os.path.basename(file_path)} - Added Trustpilot badge")
        return True
    else:
        print(f"  ⚠️  {os.path.basename(file_path)} - No footer-bottom div found")
        return False

def main():
    templates_dir = '/Users/priyeshsrivastava/Travel production/coast_to_coast_journeys/templates'
    
    print("Adding Trustpilot badge to HTML files...")
    print("=" * 60)
    
    updated_count = 0
    skipped_count = 0
    
    for filename in FILES_TO_UPDATE:
        file_path = os.path.join(templates_dir, filename)
        
        if not os.path.exists(file_path):
            print(f"  ⚠️  {filename} - File not found")
            skipped_count += 1
            continue
        
        if add_trustpilot_badge(file_path):
            updated_count += 1
        else:
            skipped_count += 1
    
    print("=" * 60)
    print(f"Summary: {updated_count} files updated, {skipped_count} files skipped")

if __name__ == '__main__':
    main()
