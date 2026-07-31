import glob

html_files = glob.glob('templates/**/*.html', recursive=True)

for file_path in html_files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Replace css/style.css with css/main.css
    new_content = content.replace('href="../css/style.css"', 'href="../css/main.css?v=3.1"')
    
    # Just in case some have no quotes or single quotes
    new_content = new_content.replace("href='../css/style.css'", 'href="../css/main.css?v=3.1"')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Updated CSS in {file_path}")

print("Done")
