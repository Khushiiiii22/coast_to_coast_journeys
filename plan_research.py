import os
import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True)

# 1. Check "What clients speak"
clients_speak = [f for f in html_files if 'What clients speak' in open(f).read()]
print(f"What clients speak found in: {len(clients_speak)} files")

# 2. Check "24x7"
t24x7 = [f for f in html_files if '24x7' in open(f).read()]
print(f"24x7 found in: {len(t24x7)} files")

# 3. Check "Aged 12+"
aged_12 = [f for f in html_files if 'Aged 12+' in open(f).read()]
print(f"Aged 12+ found in: {len(aged_12)} files")

# 4. Guest Nationality
nationality = [f for f in html_files if 'Guest Nationality (affects pricing)' in open(f).read()]
print(f"Nationality found in: {len(nationality)} files")

# 5. Request Quote
quote = [f for f in html_files if 'Request Quote' in open(f).read()]
print(f"Request Quote found in: {len(quote)} files")

# 6. Book Hotels at Best Offers
hotel_cta = [f for f in html_files if 'Book Hotels at Best Offers' in open(f).read()]
print(f"Hotel CTA found in: {len(hotel_cta)} files")

# 7. Travel Executive
executives = [f for f in html_files if 'Travel Executive' in open(f).read()]
print(f"Travel Executive found in: {len(executives)} files")

