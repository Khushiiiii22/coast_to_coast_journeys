import os
import re

directories = ['.']
exclude_dirs = {'.git', '__pycache__', 'node_modules', '.venv', 'venv', 'env', '.gemini', 'coast_to_coast_journeys'}

def replace_in_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return False
        
    new_content = re.sub(r'(?i)@c2cjourneys\.com', '@coasttocoastjourneys.com', content)
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        return True
    return False

modified_count = 0
for root, dirs, files in os.walk(directories[0]):
    dirs[:] = [d for d in dirs if d not in exclude_dirs]
    for file in files:
        if file.endswith(('.html', '.py', '.js', '.css', '.md', '.txt', '.sql', '.json')):
            filepath = os.path.join(root, file)
            if replace_in_file(filepath):
                modified_count += 1
                print(f"Modified: {filepath}")

print(f"Total files modified: {modified_count}")
