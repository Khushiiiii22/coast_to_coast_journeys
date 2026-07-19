import glob
import re

html_files = glob.glob('templates/**/*.html', recursive=True)
js_files = glob.glob('js/**/*.js', recursive=True)

replacements = [
    (re.compile(r'What clients speak', re.IGNORECASE), 'What Our Travelers Say'),
    (re.compile(r'\b24x7\b', re.IGNORECASE), '24/7'),
    (re.compile(r'Aged 12\+', re.IGNORECASE), 'Adults (12+)'),
    (re.compile(r'Guest Nationality \(affects pricing\)', re.IGNORECASE), 'Traveler Residency / Nationality (if required for supplier pricing)'),
    (re.compile(r'Request Quote', re.IGNORECASE), 'Get My Flight Quote'),
    (re.compile(r'Book Hotels at Best Offers', re.IGNORECASE), 'Unlock Member Rates on Hotels'),
    (re.compile(r'Travel Executives', re.IGNORECASE), 'Travel Advisors'),
    (re.compile(r'Travel Executive', re.IGNORECASE), 'Travel Advisor'),
    (re.compile(r'trustpilot\.com/review/[^"\'\s<>]+'), 'trustpilot.com/review/coasttocoastjourneys.com'),
]

for file_list in [html_files, js_files]:
    for f_path in file_list:
        with open(f_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        orig_content = content
        for pattern, replacement in replacements:
            content = pattern.sub(replacement, content)
            
        # Add target="_blank" rel="noopener noreferrer" to Trustpilot links if missing
        if 'trustpilot.com' in content:
            content = re.sub(
                r'(<a\s+[^>]*href=["\']https://www\.trustpilot\.com[^>]*)(>)',
                lambda m: m.group(1) + (' target="_blank"' if 'target=' not in m.group(1) else '') + (' rel="noopener noreferrer"' if 'rel=' not in m.group(1) else '') + m.group(2),
                content
            )

        if content != orig_content:
            with open(f_path, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"Updated {f_path}")
