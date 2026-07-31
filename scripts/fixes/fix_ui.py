import os
import re

# 1. Add hotel-card styles to hotel-booking.html
filepath = 'templates/hotel-booking.html'
with open(filepath, 'r') as f:
    content = f.read()

styles = """
        /* Hotel Card Grid Styles */
        .hotel-results-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        .hotel-card {
            background: #fff;
            border-radius: 12px;
            overflow: hidden;
            box-shadow: 0 4px 12px rgba(0,0,0,0.05);
            border: 1px solid #e2e8f0;
            display: flex;
            flex-direction: column;
            transition: transform 0.2s;
        }
        .hotel-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 16px rgba(0,0,0,0.08);
        }
        .hotel-image {
            height: 180px;
            width: 100%;
            overflow: hidden;
        }
        .hotel-image img {
            width: 100%;
            height: 100%;
            object-fit: cover;
        }
        .hotel-info {
            padding: 16px;
            flex: 1;
        }
        .hotel-name {
            font-size: 1.1rem;
            font-weight: 600;
            margin-bottom: 8px;
            color: #1e293b;
        }
        .hotel-location {
            font-size: 0.85rem;
            color: #64748b;
            margin-bottom: 10px;
        }
        .hotel-stars {
            color: #f59e0b;
            font-size: 0.8rem;
            margin-bottom: 10px;
        }
        .hotel-amenities {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            font-size: 0.75rem;
            color: #475569;
        }
        .hotel-price-section {
            padding: 12px 16px;
            border-top: 1px solid #e2e8f0;
            display: flex;
            justify-content: space-between;
            align-items: center;
            background: #f8fafc;
        }
        .price-label { font-size: 0.75rem; color: #64748b; }
        .price-amount { font-size: 1.15rem; font-weight: 700; color: #0e64a6; margin: 2px 0; }
        .price-per-night { font-size: 0.7rem; color: #94a3b8; }
        /* Destination Autocomplete */
"""

content = content.replace('/* Destination Autocomplete */', styles)
with open(filepath, 'w') as f:
    f.write(content)

# 2. Bump CSS version in all HTML files to bypass cache
html_dir = 'templates'
for filename in os.listdir(html_dir):
    if filename.endswith('.html'):
        fp = os.path.join(html_dir, filename)
        with open(fp, 'r') as f:
            html = f.read()
        
        # Replace ?v=4.0 or similar with ?v=5.1
        html = re.sub(r'href="\.\./css/main\.css\?v=[0-9.]+"', 'href="../css/main.css?v=5.1"', html)
        html = re.sub(r'href="\.\./css/hotel-booking\.css(\?v=[0-9.]+)?\"', 'href="../css/hotel-booking.css?v=5.1"', html)
        
        with open(fp, 'w') as f:
            f.write(html)
            
print("Fixed card styles and bumped CSS versions.")
