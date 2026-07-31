import os
import re

directory = 'templates'

analytics_tags = """
    <!-- Google tag (gtag.js) - Google Analytics -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-XXXXXXXXXX');
    </script>

    <!-- Google tag (gtag.js) - Google Ads: AW-XXXXXXXXXX -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=AW-XXXXXXXXXX"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'AW-XXXXXXXXXX');
    </script>
</head>"""

for root, _, files in os.walk(directory):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if tags already exist
            if 'G-XXXXXXXXXX' not in content:
                # Replace </head> with the tags + </head>
                new_content = re.sub(r'</head>', analytics_tags, content, flags=re.IGNORECASE)
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f'Updated {filepath}')

print('Done adding analytics!')
