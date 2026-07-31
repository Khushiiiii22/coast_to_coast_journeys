with open('css/main.css', 'r', encoding='utf-8') as f:
    content = f.read()

nav_menu_old = """    .nav-menu.active {
        display: flex;
    }"""
nav_menu_new = """    .nav-menu.active {
        display: flex !important;
    }"""

content = content.replace(nav_menu_old, nav_menu_new)

with open('css/main.css', 'w', encoding='utf-8') as f:
    f.write(content)

print("Fixed css/main.css")

