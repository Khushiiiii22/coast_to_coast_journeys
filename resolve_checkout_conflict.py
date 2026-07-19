import re

with open('templates/payment-checkout.html', 'r', encoding='utf-8') as f:
    content = f.read()

conflict_pattern = re.compile(
    r'<<<<<<< HEAD\n\s*<div class="checkout-grid">\n\s*<div class="left-column">.*?<!-- Booking Summary -->\n=======\n\s*<div class="checkout-grid" id="mainCheckoutGrid">\n\s*<!-- 1\. Booking Summary -->\n\s*<!-- Booking Summary -->\n>>>>>>> [a-z0-9]+ \(frontend changes\)\n',
    re.DOTALL
)

def replacer(match):
    head_content = match.group(0)
    
    # Extract the stuff inside HEAD
    head_inner = re.search(r'<<<<<<< HEAD\n\s*<div class="checkout-grid">\n(.*?)=======', head_content, re.DOTALL).group(1)
    
    # Clean it up, combine with the id="mainCheckoutGrid"
    resolved = f'        <div class="checkout-grid" id="mainCheckoutGrid">\n{head_inner}'
    
    return resolved

new_content = conflict_pattern.sub(replacer, content)

if new_content != content:
    with open('templates/payment-checkout.html', 'w', encoding='utf-8') as f:
        f.write(new_content)
    print("Conflict resolved successfully.")
else:
    print("Conflict pattern not found or not matched perfectly.")

