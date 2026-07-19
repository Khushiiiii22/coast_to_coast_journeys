import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    js_content = f.read()

# Replace the current wrapper click logic with a robust input click logic
new_logic = """// Make date input wrappers clickable to open the date picker
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.form-field-improved, .search-box-field, .date-field, .form-group').forEach(wrapper => {
        const dateInput = wrapper.querySelector('input[type="date"]');
        if (dateInput) {
            wrapper.style.cursor = 'pointer';
            
            const openPicker = () => {
                try {
                    if (typeof dateInput.showPicker === 'function') {
                        dateInput.showPicker();
                    }
                } catch (err) {
                    // Ignore DOMException if picker is already shown
                }
            };

            // If user clicks the input itself (like the text area in Chrome)
            dateInput.addEventListener('click', (e) => {
                openPicker();
            });

            // If user clicks the wrapper (label, padding, etc.)
            wrapper.addEventListener('click', (e) => {
                if (e.target !== dateInput) {
                    openPicker();
                }
            });
        }
    });
});
"""

# Regex to replace the whole DOMContentLoaded block for date pickers
js_content = re.sub(
    r'// Make date input wrappers clickable to open the date picker\ndocument\.addEventListener\(\'DOMContentLoaded\', \(\) => \{.*?\n\}\);\n',
    new_logic,
    js_content,
    flags=re.DOTALL
)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(js_content)
    
print("Updated js/main.js")
