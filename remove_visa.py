import os
import re

about_path = 'templates/about.html'
with open(about_path, 'r') as f:
    about = f.read()

about = about.replace('flight, hotel, and visa booking services', 'flight and hotel booking services')
about = about.replace('Search Hotels & Flights & Visa', 'Search Hotels & Flights')

with open(about_path, 'w') as f:
    f.write(about)
print("Updated about.html")

not_found_path = 'templates/404.html'
with open(not_found_path, 'r') as f:
    not_found = f.read()

visa_block = """                <a href="visa.html" class="quick-link">
                    <i class="fas fa-passport"></i> Visa Services
                </a>"""

not_found = not_found.replace(visa_block, '')

with open(not_found_path, 'w') as f:
    f.write(not_found)
print("Updated 404.html")
