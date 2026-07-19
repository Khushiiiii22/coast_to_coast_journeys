import re

with open('templates/flight-quote.html', 'r', encoding='utf-8') as f:
    html = f.read()

classes = set()
for match in re.finditer(r'class="([^"]+)"', html):
    for cls in match.group(1).split():
        classes.add(cls)

print("Classes in flight-quote.html:")
print(sorted(list(classes)))

with open('css/main.css', 'r', encoding='utf-8') as f:
    css = f.read()

hidden_classes = set()
blocks = re.findall(r'([^{}]+)\s*{[^}]*display\s*:\s*none[^}]*}', css)
for block in blocks:
    for cls in re.findall(r'\.([a-zA-Z0-9_-]+)', block):
        hidden_classes.add(cls)

print("\nHidden classes in main.css:")
print(sorted(list(hidden_classes)))

intersection = classes.intersection(hidden_classes)
print("\nIntersection:")
print(intersection)

