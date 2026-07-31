import re

with open('js/main.js', 'r', encoding='utf-8') as f:
    content = f.read()

# Add hamburgerMenu to DOM
dom_old = "    mobileMenuToggle: document.getElementById('mobileMenuToggle'),"
dom_new = "    mobileMenuToggle: document.getElementById('mobileMenuToggle'),\n    hamburgerMenu: document.getElementById('hamburgerMenu'),"
content = content.replace(dom_old, dom_new)

# Update toggleMobileMenu
toggle_old = """function toggleMobileMenu() {
    DOM.navMenu.classList.toggle('active');
    DOM.mobileMenuToggle.classList.toggle('active');
}"""
toggle_new = """function toggleMobileMenu() {
    if (DOM.navMenu) DOM.navMenu.classList.toggle('active');
    if (DOM.mobileMenuToggle) DOM.mobileMenuToggle.classList.toggle('active');
    if (DOM.hamburgerMenu) DOM.hamburgerMenu.classList.toggle('active');
}"""
content = content.replace(toggle_old, toggle_new)

# Update initEventListeners
init_old = """    // Mobile Menu
    if (DOM.mobileMenuToggle) {
        DOM.mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }"""
init_new = """    // Mobile Menu
    if (DOM.mobileMenuToggle) {
        DOM.mobileMenuToggle.addEventListener('click', toggleMobileMenu);
    }
    if (DOM.hamburgerMenu) {
        DOM.hamburgerMenu.addEventListener('click', toggleMobileMenu);
    }"""
content = content.replace(init_old, init_new)

with open('js/main.js', 'w', encoding='utf-8') as f:
    f.write(content)

print("Updated main.js for hamburgerMenu")
