import re

with open('templates/flight-quote.html', 'r', encoding='utf-8') as f:
    content = f.read()

style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)
if style_match:
    style_content = style_match.group(1)
    # find all display: none
    for line in style_content.splitlines():
        if 'display' in line and 'none' in line:
            print(line.strip())
