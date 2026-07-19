import os

with open('css/main.css', 'r') as f:
    css = f.read()

# Add a CSS rule to make sure date input is fully covering the container for older browsers if showPicker fails
# We don't want opacity 0 because it hides the date text, but we can make it block and 100% width/height.
css_patch = """
/* Date Picker Full Box Clickable Fix */
.form-field-improved.date-field input[type="date"],
.search-box-field input[type="date"],
.form-group input[type="date"] {
    width: 100%;
    box-sizing: border-box;
    cursor: pointer;
}
"""

if "Date Picker Full Box Clickable Fix" not in css:
    with open('css/main.css', 'a') as f:
        f.write(css_patch)
    print("Added CSS patch")
else:
    print("CSS patch already exists")
