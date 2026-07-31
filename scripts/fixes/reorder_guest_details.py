import re

with open('templates/guest-details.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the Contact Information block
contact_match = re.search(r'(\s*<!-- Contact Information -->.*?)(?=\s*<!-- Booking Cut-off Warning -->)', content, re.DOTALL)
cutoff_match = re.search(r'(\s*<!-- Booking Cut-off Warning -->.*?)(?=\s*<!-- Booking Summary -->)', content, re.DOTALL)
summary_match = re.search(r'(\s*<!-- Booking Summary -->\s*<div class="booking-summary">.*?</div>\s*</div>\s*</div>\s*<!-- Price Details -->)', content, re.DOTALL)

# Wait, the summary_match regex is tricky because of nested divs.
# Let's just find indices using string searches.
contact_start = content.find('<!-- Contact Information -->')
cutoff_start = content.find('<!-- Booking Cut-off Warning -->')
summary_start = content.find('<!-- Booking Summary -->')
price_start = content.find('<!-- Price Details -->')

if contact_start != -1 and cutoff_start != -1 and summary_start != -1 and price_start != -1:
    contact_block = content[contact_start:cutoff_start]
    cutoff_block = content[cutoff_start:summary_start]
    
    # We need to find the end of the booking-summary div which is right before "<!-- Price Details -->"
    # But there's a </div> for .left-column there too.
    # The structure is:
    #                 </div>
    #             </div>
    #             <!-- Price Details -->
    #
    # Let's extract the summary block carefully.
    summary_block = content[summary_start:price_start]
    
    # The summary block currently includes the closing </div> for .left-column if it's right before <!-- Price Details -->
    # Actually, in the HTML:
    # 383:                     </div>
    # 384:                 </div>
    # 385:             </div>
    # 386: 
    # 387:             <!-- Price Details -->
    
    # Let's reconstruct the left-column content.
    left_column_start = content.find('<div class="left-column">') + len('<div class="left-column">')
    left_column_end = price_start
    
    left_content = content[left_column_start:left_column_end]
    
    c_start = left_content.find('<!-- Contact Information -->')
    s_start = left_content.find('<!-- Booking Summary -->')
    
    contact_and_cutoff = left_content[c_start:s_start]
    
    # The summary block is from s_start up to the last </div> which closes left-column.
    # Let's find the last </div> before the end.
    last_div_idx = left_content.rfind('</div>')
    
    summary = left_content[s_start:last_div_idx]
    closing_divs = left_content[last_div_idx:]
    
    # Let's add some bottom margin to the summary block since it's now at the top
    # The summary starts with <!-- Booking Summary -->\n                <div class="booking-summary">
    summary = summary.replace('<div class="booking-summary">', '<div class="booking-summary" style="margin-bottom: 30px;">', 1)
    
    new_left_content = '\n                ' + summary.strip() + '\n                ' + contact_and_cutoff.strip() + '\n            ' + closing_divs.strip() + '\n\n            '
    
    new_content = content[:left_column_start] + new_left_content + content[left_column_end:]
    
    with open('templates/guest-details.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Successfully reordered!")
else:
    print("Could not find all sections.")
