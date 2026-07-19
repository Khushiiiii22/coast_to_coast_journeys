import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True)

def check(pattern):
    found = 0
    for f in html_files:
        with open(f, 'r') as file:
            content = file.read()
            if re.search(pattern, content, re.IGNORECASE):
                found += 1
    return found

print("Guest Nationality:", check(r'guest nationality'))
print("Travel Executive:", check(r'travel executive'))
