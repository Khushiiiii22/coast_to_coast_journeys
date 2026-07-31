with open('js/main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Replace the specific block of code
target = """            wrapper.addEventListener('click', (e) => {
                // Don't trigger if they clicked on the input itself (it handles its own click)
                if (e.target === dateInput) return;
                
                try {"""

replacement = """            wrapper.addEventListener('click', (e) => {
                // Prevent default so focus doesn't override showPicker
                e.preventDefault();
                try {"""

if target in js_content:
    js_content = js_content.replace(target, replacement)
    with open('js/main.js', 'w', encoding='utf-8') as f:
        f.write(js_content)
    print("Fixed js/main.js")
else:
    print("Target block not found in js/main.js")
