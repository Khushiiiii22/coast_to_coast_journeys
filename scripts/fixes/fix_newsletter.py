import os

html_dir = 'templates'
for filename in os.listdir(html_dir):
    if filename.endswith('.html'):
        fp = os.path.join(html_dir, filename)
        with open(fp, 'r') as f:
            content = f.read()
            
        if 'Get Exclusive Travel Deals' not in content:
            continue
            
        # Fix the newsletter container background
        content = content.replace(
            'style="background: linear-gradient(135deg, rgba(5,108,185,0.15), rgba(3,75,133,0.1)); border-radius: 16px; padding: 30px; margin: 30px 0; text-align: center;"',
            'style="background: #eef2ff; border-radius: 16px; padding: 30px; margin: 30px 0; text-align: center; border: 1px solid #e0e7ff;"'
        )
        
        # Fix heading
        content = content.replace(
            '<h4 style="color: white; font-size: 1.2rem; margin-bottom: 6px;">',
            '<h4 style="color: #1e3a8a; font-size: 1.2rem; margin-bottom: 6px; font-weight: 600;">'
        )
        
        # Fix subtitle
        content = content.replace(
            '<p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 16px;">',
            '<p style="color: #475569; font-size: 0.9rem; margin-bottom: 16px;">'
        )
        
        # Fix input field
        content = content.replace(
            'style="flex: 1; min-width: 220px; padding: 12px 18px; border: 2px solid rgba(255,255,255,0.2); border-radius: 10px; background: rgba(255,255,255,0.1); color: white; font-size: 0.95rem; outline: none; transition: border-color 0.2s;"',
            'style="flex: 1; min-width: 220px; padding: 12px 18px; border: 1px solid #cbd5e1; border-radius: 10px; background: #ffffff; color: #1e293b; font-size: 0.95rem; outline: none; transition: border-color 0.2s; box-shadow: inset 0 1px 2px rgba(0,0,0,0.05);"'
        )
        content = content.replace("this.style.borderColor='rgba(255,255,255,0.2)'", "this.style.borderColor='#cbd5e1'")
        
        # Fix bottom text
        content = content.replace(
            '<p style="color: rgba(255,255,255,0.4); font-size: 0.75rem; margin-top: 10px;">',
            '<p style="color: #94a3b8; font-size: 0.75rem; margin-top: 10px;">'
        )
        
        with open(fp, 'w') as f:
            f.write(content)

print("Fixed newsletter styles.")
