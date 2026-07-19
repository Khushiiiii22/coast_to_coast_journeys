import re

with open('css/main.css', 'r', encoding='utf-8') as f:
    css = f.read()

# match @media blocks
# This is a bit tricky with nested braces, but we can do a simple stack based parser
media_queries = []
in_media = False
current_mq = ""
brace_count = 0

for line in css.splitlines():
    if not in_media:
        if "@media" in line:
            in_media = True
            current_mq = line + "\n"
            brace_count = line.count('{') - line.count('}')
    else:
        current_mq += line + "\n"
        brace_count += line.count('{') - line.count('}')
        if brace_count == 0:
            media_queries.append(current_mq)
            in_media = False
            current_mq = ""

for i, mq in enumerate(media_queries):
    print(f"--- Media Query {i} ---")
    print(mq)

