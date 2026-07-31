import os
import re

base_file = 'templates/privacy-policy.html'
with open(base_file, 'r', encoding='utf-8') as f:
    base_html = f.read()

blogs = [
    {
        'filename': 'templates/blog-beach-resorts.html',
        'title': 'The 10 Best Luxury Beach Resorts in the US',
        'icon': 'fa-umbrella-beach',
        'subtitle': 'Discover breathtaking oceanfront properties with world-class amenities.',
        'image': 'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80',
        'content': """
                    <div style="margin-bottom: 30px;">
                        <img src="{image}" alt="Beach Resort" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
                    </div>
                    <p>Finding the perfect luxury beach resort in the US can turn a simple vacation into an unforgettable escape. Whether you are looking for pristine white sands, world-class spas, or award-winning dining, the coastlines of America have something exceptional to offer.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">1. The Cloister at Sea Island, Georgia</h3>
                    <p>Located on a private island off the coast of Georgia, The Cloister is a legendary luxury resort known for its Mediterranean architecture, five miles of private beach, and impeccable Southern hospitality. Guests can enjoy three championship golf courses, a 65,000-square-foot spa, and incredible oceanfront dining.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">2. Acqualina Resort & Residences, Florida</h3>
                    <p>Situated in Sunny Isles Beach, Miami, Acqualina feels like a Mediterranean villa transported to the Atlantic Ocean. It is the only resort in South Florida built completely open to the ocean, free of barriers between the 51-story tower and its 400 feet of pristine coastline.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">3. Montage Laguna Beach, California</h3>
                    <p>Perched on a coastal bluff above the Pacific Ocean, Montage Laguna Beach offers a luxurious beachfront sanctuary. Every room boasts ocean views, and the resort's stunning mosaic pool is a masterpiece. It's the ultimate destination for barefoot luxury.</p>

                    <p style="margin-top: 40px; font-weight: bold;">Ready to experience these breathtaking properties? <a href="hotel-booking.html" style="color: var(--primary);">Book your stay with Coast to Coast Journeys today!</a></p>
        """
    },
    {
        'filename': 'templates/blog-nyc-guide.html',
        'title': "Where to Stay in New York City: First Timer's Guide",
        'icon': 'fa-city',
        'subtitle': 'Find the perfect neighborhood for your NYC adventure.',
        'image': 'https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=1200&q=80',
        'content': """
                    <div style="margin-bottom: 30px;">
                        <img src="{image}" alt="New York City" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
                    </div>
                    <p>New York City is massive, and choosing where to stay can be overwhelming for a first-time visitor. The city is composed of five distinct boroughs, but most visitors focus on Manhattan and Brooklyn. Here is our guide to the best neighborhoods.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">Midtown Manhattan: Best for Sightseeing</h3>
                    <p>If it is your first time in the Big Apple, Midtown puts you right in the center of the action. You will be walking distance to Times Square, Broadway, the Empire State Building, and MoMA. While it can be crowded, the convenience is unmatched.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">SoHo & Tribeca: Best for Shopping & Dining</h3>
                    <p>If you prefer cobblestone streets, high-end boutiques, and trendy cafes over towering skyscrapers, SoHo is your spot. It has a much more local, artistic feel while still offering incredible luxury hotels like The Crosby Street Hotel.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">Williamsburg, Brooklyn: Best for Trendy Vibes</h3>
                    <p>Just one subway stop from Manhattan, Williamsburg offers incredible skyline views, vintage shopping, and a vibrant nightlife scene. Hotels here often feature rooftop pools and bars with the best views of the Manhattan skyline.</p>
        """
    },
    {
        'filename': 'templates/blog-vegas-upgrades.html',
        'title': 'How to Score Free Room Upgrades in Las Vegas',
        'icon': 'fa-dice',
        'subtitle': 'Learn the insider secrets to getting complimentary suites.',
        'image': 'https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&w=1200&q=80',
        'content': """
                    <div style="margin-bottom: 30px;">
                        <img src="{image}" alt="Las Vegas" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
                    </div>
                    <p>Las Vegas is the city of high rollers, but you don't need to spend thousands to be treated like one. Getting a free room upgrade on the Strip is entirely possible if you know the right tricks.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">1. The Famous $20 Trick</h3>
                    <p>It is the oldest trick in the Vegas playbook. When you hand the front desk clerk your ID and credit card, discreetly place a folded $20 bill between them and politely ask, "Are there any complimentary room upgrades available?" While not guaranteed, clerks have a lot of discretion and will often find you a better view or a larger room.</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">2. Book During Off-Peak Times</h3>
                    <p>If you check in on a Tuesday in November, your chances of getting upgraded are astronomically higher than on a Friday night during a major convention. Hotels can only upgrade you if they have empty suites!</p>
                    
                    <h3 style="margin-top: 30px; color: var(--primary);">3. Mention Special Occasions</h3>
                    <p>Celebrating an anniversary, honeymoon, or birthday? Let the hotel know! Front desk agents love being part of a celebration and will often upgrade your room or send up a complimentary bottle of champagne.</p>
        """
    }
]

for blog in blogs:
    content = base_html
    
    # Replace Title
    content = re.sub(r'<title>.*?</title>', f'<title>{blog["title"]} | Coast to Coast</title>', content)
    
    # Replace Breadcrumb
    content = re.sub(r'<span>Privacy Policy</span>', f'<span>{blog["title"]}</span>', content)
    
    # Replace Hero
    content = re.sub(r'<h1><i class="fas fa-lock"></i> Privacy Policy</h1>\s*<p>How we collect, use, and protect your information</p>', f'<h1><i class="fas {blog["icon"]}"></i> {blog["title"]}</h1>\n                <p>{blog["subtitle"]}</p>', content)
    
    # Replace Content Wrapper
    blog_html = blog['content'].replace('{image}', blog['image'])
    content = re.sub(r'<div class="policy-intro">.*?(?=<section class="contact-section">)', blog_html, content, flags=re.DOTALL)
    
    # Fix the active nav link (set home active instead of whatever was active, or just keep it)
    
    with open(blog['filename'], 'w', encoding='utf-8') as f:
        f.write(content)
    print(f'Created {blog["filename"]}')

print('Done!')
