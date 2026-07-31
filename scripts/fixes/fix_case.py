import os

directory = 'templates'

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            new_content = content
            
            # Replace logo text
            new_content = new_content.replace('<span class="logo-text">Coast to Coast</span>', '<span class="logo-text">Coast To Coast</span>')
            
            # Replace titles and meta
            new_content = new_content.replace('Coast to Coast Journeys', 'Coast To Coast Journeys')
            new_content = new_content.replace('Coast to Coast |', 'Coast To Coast |')
            
            # Additional places where "Coast to Coast" might be standalone
            new_content = new_content.replace('with Coast to Coast.', 'with Coast To Coast.')
            new_content = new_content.replace('with Coast to Coast', 'with Coast To Coast')
            
            if new_content != content:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                print(f'Updated {filepath}')

print('Done!')
