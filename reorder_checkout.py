import re

with open('templates/payment-checkout.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the start of left-column
left_col_start = content.find('<div class="left-column">')

# We know Contact Info comes first, then Booking Summary.
contact_start = content.find('<!-- Contact Information -->', left_col_start)
booking_start = content.find('<!-- Booking Summary -->', contact_start)
# Find the end of left-column which is just before <!-- Price Details -->
price_start = content.find('<!-- Price Details -->', booking_start)
left_col_end = content.rfind('</div>', booking_start, price_start)

contact_html = content[contact_start:booking_start].strip()
booking_html = content[booking_start:left_col_end].strip()

# Find price summary
price_summary_start = content.find('<div class="price-summary">', price_start)
# Find the end of price-summary, which is just before <div class="checkout-grid"> closes.
# Wait, the end of checkout-grid is just before </div> </div> <!-- Footer -->
# Let's find <!-- Footer -->
footer_start = content.find('<!-- Footer -->')
checkout_grid_end = content.rfind('</div>', price_summary_start, footer_start)
price_summary_end = content.rfind('</div>', price_summary_start, checkout_grid_end)
# Actually, the grid is: <div class="checkout-grid"> ... </div>
# Price summary is the last child of checkout-grid.
price_html = content[price_summary_start:price_summary_end + 6].strip()

# Now we construct the new grid HTML
new_grid = f'''        <div class="checkout-grid" id="mainCheckoutGrid">
            <!-- 1. Booking Summary -->
            {booking_html}

            <!-- 2. Price Details (Payment) -->
            {price_html.replace('<div class="price-summary">', '<div class="price-summary" id="paymentSection">')}

            <!-- 3. Contact Information -->
            {contact_html}
        </div>'''

# Replace everything from <div class="checkout-grid"> to price_summary_end + 6
grid_start = content.find('<div class="checkout-grid">')
new_content = content[:grid_start] + new_grid + content[price_summary_end + 6:]

# Add styles for the new grid layout
style_insert_idx = new_content.find('</style>')
styles = """
        #paymentSection {
            grid-column: 2;
            grid-row: 1 / span 2;
        }
        @media (max-width: 768px) {
            #paymentSection {
                grid-column: 1;
                grid-row: auto;
            }
        }
"""
new_content = new_content[:style_insert_idx] + styles + new_content[style_insert_idx:]

with open('templates/payment-checkout.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Reordered payment-checkout.html successfully.")
