import os
import re

files_to_seo = {
    'templates/index.html': {
        'title': 'Coast to Coast Journeys | Book Premium Flights & Hotels',
        'desc': 'Coast to Coast Journeys - Your trusted US travel partner. Book premium flights, luxury hotels, and exclusive travel deals.'
    },
    'templates/flight-booking.html': {
        'title': 'Cheap Flight Tickets & Bookings | Coast to Coast Journeys',
        'desc': 'Compare and book cheap flight tickets worldwide. Find exclusive deals and fly with premium airlines using Coast to Coast Journeys.'
    },
    'templates/hotel-booking.html': {
        'title': 'Luxury Hotels & Cheap Stays | Coast to Coast Journeys',
        'desc': 'Find your perfect stay. Book luxury hotels, cheap stays, and exclusive accommodations across the US and worldwide.'
    }
}

for filepath, meta in files_to_seo.items():
    if not os.path.exists(filepath): continue
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Update Title
    content = re.sub(r'<title>.*?</title>', f'<title>{meta["title"]}</title>', content, flags=re.IGNORECASE)

    # Update Description
    content = re.sub(r'<meta\s+name="description"\s+content="[^"]*">', f'<meta name="description" content="{meta["desc"]}">', content, flags=re.IGNORECASE)

    # Add JSON-LD and OG tags right before </head> if not exists
    if 'application/ld+json' not in content:
        seo_injection = f"""
    <meta property="og:title" content="{meta['title']}">
    <meta property="og:description" content="{meta['desc']}">
    <meta property="og:type" content="website">
    <script type="application/ld+json">
    {{
      "@context": "https://schema.org",
      "@type": "TravelAgency",
      "name": "Coast to Coast Journeys",
      "telephone": "+1-888-315-9768",
      "email": "Sales@c2cjourneys.com",
      "url": "https://c2cjourneys.com"
    }}
    </script>
</head>"""
        # Replace </head> with seo_injection
        content = re.sub(r'</head>', seo_injection, content, flags=re.IGNORECASE)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Updated SEO for {filepath}')

print('Done updating SEO!')
