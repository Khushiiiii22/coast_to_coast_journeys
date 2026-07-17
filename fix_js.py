import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix flatpickr error by checking if it exists
init_date_pickers_old = "function initDatePickers() {\n    const commonConfig = {"
init_date_pickers_new = "function initDatePickers() {\n    if (typeof flatpickr === 'undefined') return;\n    const commonConfig = {"
content = content.replace(init_date_pickers_old, init_date_pickers_new)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed main.js")

# Fix flight-booking.html by removing the undefined function call
with open('templates/flight-booking.html', 'r', encoding='utf-8') as f:
    fb_content = f.read()

fb_old = """            // Populate passenger details
            populatePassengerDetails();
            populateAddons();"""
fb_new = """            // Populate passenger details (Moved to appropriate page)
            // populatePassengerDetails();
            // populateAddons();"""
fb_content = fb_content.replace(fb_old, fb_new)

with open('templates/flight-booking.html', 'w', encoding='utf-8') as f:
    f.write(fb_content)

print("Fixed flight-booking.html")

