filepath = 'templates/hotel-booking.html'
with open(filepath, 'r') as f:
    content = f.read()

import re

# Remove the aside block
new_content = re.sub(r'<!-- Filters Sidebar -->\s*<aside class="filters-sidebar">.*?</aside>', '', content, flags=re.DOTALL)

with open(filepath, 'w') as f:
    f.write(new_content)
