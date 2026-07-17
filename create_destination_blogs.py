import os
import re

base_file = 'templates/privacy-policy.html'
with open(base_file, 'r', encoding='utf-8') as f:
    base_html = f.read()

def create_blog(filename, title, subtitle, icon, content_html, image_url):
    content = base_html
    # Replace Title
    content = re.sub(r'<title>.*?</title>', f'<title>{title} | Coast To Coast</title>', content)
    # Replace Breadcrumb
    content = re.sub(r'<span>Privacy Policy</span>', f'<span>{title}</span>', content)
    # Replace Hero
    content = re.sub(r'<h1><i class="fas fa-lock"></i> Privacy Policy</h1>\s*<p>How we collect, use, and protect your information</p>', f'<h1><i class="fas {icon}"></i> {title}</h1>\n                <p>{subtitle}</p>', content)
    
    # Replace Content Wrapper
    blog_body = f"""
<div style="margin-bottom: 30px;">
    <img src="{image_url}" alt="{title}" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
</div>
{content_html}
    """
    
    start_marker = '<div class="content-wrapper policy-content">'
    end_marker = '</main>'
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx != -1 and end_idx != -1:
        before = content[:start_idx + len(start_marker)]
        after = content[end_idx:]
        new_full_content = before + "\n" + blog_body + "\n</div>\n" + after
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_full_content)
        print(f"Created {filename}")

# 1. India
india_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">Discover India, a tapestry of vibrant cultures, ancient temples, and majestic monuments. From the ethereal beauty of the Taj Mahal to the spiritual serenity of Varanasi's ghats, each corner reveals a unique story. Wander through bustling markets, savour exquisite regional cuisines, and immerse yourself in centuries-old traditions. With landscapes ranging from the snow-capped Himalayas to sun-kissed beaches in Goa, India enchants every traveller. Experience the warmth of its people and the richness of its heritage, making it an unforgettable adventure for both the curious explorer and the romantic soul.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in India</h3>
<p>In Mumbai, New Delhi, and Puri, each destination offers unique experiences. Mumbai boasts vibrant markets and a rich cultural scene, while New Delhi is known for its historical landmarks and temples. Puri captivates with its ancient ruins and spiritual significance. For first-time visitors, New Delhi is best suited, offering a blend of history, culture, and modern amenities.</p>

<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>Mumbai:</strong> Mumbai is the vibrant heart of India, known for its dynamic blend of modernity and tradition. The city boasts stunning temples and bustling markets, where shoppers can find everything from luxury goods to local crafts. Attractions like the iconic Gateway of India and the serene Marine Drive offer a perfect mix of cultural experiences and scenic beauty.</li>
    <li style="margin-bottom: 15px;"><strong>New Delhi:</strong> New Delhi stands as a testament to India's rich history and diverse culture. The capital is adorned with impressive temples and historical ruins, making it a treasure trove for history enthusiasts. Iconic sites like India Gate and Humayun's Tomb are must-see spots that reflect the city's grandeur.</li>
    <li style="margin-bottom: 15px;"><strong>Puri:</strong> Puri is a coastal gem known for its spiritual significance and stunning beaches. Renowned for the Jagannath Temple, this town attracts visitors seeking a blend of relaxation and cultural immersion. The sandy shores offer a tranquil escape, perfect for unwinding after exploring the rich heritage of the area.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in India</h3>
<p><strong>Book for the cheapest times:</strong> The most budget-friendly period to visit India is from May to July, when hotel prices tend to be lower.</p>
<p><strong>Look for last-minute deals:</strong> Keep an eye out for flash sales and special promotions.</p>
<p><strong>Be flexible with dates:</strong> Prices may fluctuate depending on factors such as the hotel's location, star rating, and the time of year.</p>
<p><strong>Consider your location:</strong> Exploring alternative nearby cities can uncover a wealth of experiences while providing more budget-friendly lodging options.</p>
"""

# 2. UAE
uae_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">Discover the United Arab Emirates, a dazzling fusion of tradition and modernity. Marvel at the iconic skyline of Dubai, where luxury shopping and desert adventures beckon. Unwind on pristine beaches, explore vibrant marinas, and experience the serene beauty of the Arabian desert. Cultural gems like the Sheikh Zayed Grand Mosque in Abu Dhabi and the UNESCO-listed Al Ain Oasis offer a glimpse into rich heritage. Whether you seek opulent resorts or thrilling adventures, the UAE promises an unforgettable escape.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in United Arab Emirates</h3>
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>Dubai:</strong> Dubai is a dazzling metropolis known for its futuristic skyline and luxury shopping experiences. Visitors can explore the iconic Burj Khalifa and enjoy stunning views from the observation deck.</li>
    <li style="margin-bottom: 15px;"><strong>Abu Dhabi:</strong> Abu Dhabi, the capital of the UAE, offers a unique blend of tradition and modernity. A must-see is the magnificent Sheikh Zayed Grand Mosque, an architectural masterpiece that showcases stunning artistry.</li>
    <li style="margin-bottom: 15px;"><strong>Ras Al Khaimah:</strong> Ras Al Khaimah is a hidden gem for those seeking a more relaxed experience. Known for its stunning beaches and natural landscapes, it's the perfect spot for sunbathing or water sports.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in United Arab Emirates</h3>
<p><strong>Book for the cheapest times:</strong> The most affordable period to visit the United Arab Emirates is between July and September, when hotel prices are typically lower.</p>
<p><strong>Look for last-minute deals:</strong> Stay informed about any price drops or room availability for a spontaneous getaway.</p>
<p><strong>Be flexible with dates:</strong> Being flexible with your travel dates may help you save on your stay.</p>
<p><strong>Consider your location:</strong> Smaller towns and rural areas are more likely to be affordable, presenting a tempting alternative for budget-conscious travellers.</p>
"""

# 3. UK
uk_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">The United Kingdom, a treasure trove of history and culture, invites travellers to explore its enchanting landscapes and iconic landmarks. Wander through the hallowed halls of ancient castles, marvel at world-class museums in London, or lose yourself in the breathtaking beauty of the Lake District’s rolling hills. Stroll along the charming streets of Edinburgh’s Old Town, or discover the rugged coastlines of Cornwall.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in United Kingdom</h3>
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>London:</strong> London is a vibrant, bustling metropolis that seamlessly blends history and modernity. It's a cultural hotspot where you can catch a West End show, explore the British Museum, or stroll through the charming streets of Covent Garden.</li>
    <li style="margin-bottom: 15px;"><strong>Edinburgh:</strong> Edinburgh is a city steeped in history and charm, making it a unique destination for travellers. The majestic Edinburgh Castle dominates the skyline and offers breathtaking views of the city.</li>
    <li style="margin-bottom: 15px;"><strong>Manchester:</strong> Manchester is a dynamic city known for its rich industrial heritage and cultural diversity. It's a great place for those interested in music and arts.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in United Kingdom</h3>
<p><strong>Book for the cheapest times:</strong> The most affordable time to visit the United Kingdom is from January to March, when hotel prices tend to be lower.</p>
<p><strong>Look for last-minute deals:</strong> Enable email alerts to keep you informed about flash sales and special promotions.</p>
<p><strong>Be flexible with dates:</strong> Boutique hotels often provide a more personalised touch and can sometimes offer better value.</p>
<p><strong>Consider your location:</strong> Accommodations in city centres are typically more expensive due to their proximity to popular attractions and amenities.</p>
"""

# 4. USA
usa_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">The United States of America, a vibrant tapestry of cultures and landscapes, beckons travellers with its diverse allure. From the sun-kissed beaches of California to the majestic peaks of the Rocky Mountains, each state offers its own unique charm. Explore world-class museums in New York City, wander through the enchanting national parks like Yosemite, or indulge in the culinary delights of New Orleans.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in United States of America</h3>
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>New York:</strong> New York is a vibrant metropolis where the energy of the city never sleeps. With its iconic skyline and diverse neighbourhoods, it offers a rich tapestry of cultural experiences.</li>
    <li style="margin-bottom: 15px;"><strong>Las Vegas:</strong> Las Vegas is a dazzling oasis known for its entertainment and vibrant atmosphere. The famous Strip is lined with extravagant hotels and resorts, each offering unique experiences.</li>
    <li style="margin-bottom: 15px;"><strong>Orlando:</strong> Orlando is a dream destination for families and thrill-seekers alike, boasting some of the best theme parks in the world.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in United States of America</h3>
<p><strong>Book for the cheapest times:</strong> The most affordable time to visit the United States of America is during January, February, and November, when hotel prices are generally lower.</p>
<p><strong>Look for last-minute deals:</strong> Discover discounted hotel rates as your travel date approaches.</p>
<p><strong>Be flexible with dates:</strong> Being flexible with your travel dates could help you save on your stay.</p>
<p><strong>Consider your location:</strong> Staying in the heart of major cities across the United States can provide unparalleled convenience... However, this prime location often comes with a heftier price tag.</p>
"""

# 5. Indonesia
indonesia_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">Discover Indonesia, a tropical paradise where pristine beaches meet ancient temples. Explore the enchanting island of Bali, renowned for its vibrant culture, stunning rice terraces, and serene seaside retreats. Wander through the majestic Borobudur and Prambanan temples, marveling at their intricate architecture and spiritual significance. Dive into the crystal-clear waters of Komodo National Park, home to the legendary Komodo dragon and vibrant marine life.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in Indonesia</h3>
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>Ubud:</strong> Ubud is a haven for those seeking tranquillity and a connection to nature. Nestled among lush rice terraces and vibrant forests, it offers a serene environment perfect for relaxation.</li>
    <li style="margin-bottom: 15px;"><strong>Seminyak:</strong> Seminyak is the stylish heartbeat of Bali, ideal for travellers looking to soak up the sun on stunning beaches while enjoying a vibrant atmosphere.</li>
    <li style="margin-bottom: 15px;"><strong>Senggigi:</strong> Senggigi is a charming coastal destination on Lombok, renowned for its beautiful beaches and vibrant marine life, making it a snorkeller's delight.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in Indonesia</h3>
<p><strong>Book for the cheapest times:</strong> The most budget-friendly times to visit Indonesia are February, March, and November.</p>
<p><strong>Look for last-minute deals:</strong> Check for last-minute discounts closer to your travel dates.</p>
<p><strong>Be flexible with dates:</strong> Flexibility allows you to capitalize on sudden price drops.</p>
<p><strong>Consider your location:</strong> Smaller towns and rural areas tend to be more affordable, making them an attractive option for budget-conscious travellers.</p>
"""

# 6. Singapore
singapore_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">Singapore, a dazzling city-state, seamlessly blends tradition and modernity. Explore the lush Gardens by the Bay, where futuristic Supertrees soar above vibrant floral displays. Wander through vibrant cultural enclaves like Chinatown and Little India, or shop till you drop on Orchard Road. Singapore’s world-class culinary scene, from humble hawker centers to Michelin-starred dining, offers a spectacular journey for your taste buds.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in Singapore</h3>
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>Marina Bay:</strong> The ultimate luxury experience with stunning waterfront views, upscale dining, and direct access to iconic landmarks like Marina Bay Sands and the ArtScience Museum.</li>
    <li style="margin-bottom: 15px;"><strong>Orchard Road:</strong> Ideal for shoppers, this bustling district is lined with massive malls, luxury boutiques, and high-end hotels.</li>
    <li style="margin-bottom: 15px;"><strong>Sentosa Island:</strong> A tropical resort island just off the coast, perfect for families and beach lovers seeking theme parks, golf courses, and relaxation.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in Singapore</h3>
<p><strong>Book for the cheapest times:</strong> Avoiding major events like the Formula 1 Grand Prix can help secure much better rates.</p>
<p><strong>Look for last-minute deals:</strong> Business hotels often discount unbooked rooms during the weekends.</p>
<p><strong>Be flexible with dates:</strong> Mid-week stays can sometimes offer surprising value.</p>
<p><strong>Consider your location:</strong> Neighborhoods slightly outside the central core offer excellent value and are extremely accessible via the efficient MRT system.</p>
"""

# 7. Maldives
maldives_html = """
<p style="font-size: 1.1rem; line-height: 1.8;">The Maldives is synonymous with paradise. This breathtaking archipelago of coral islands in the Indian Ocean offers crystal-clear turquoise waters, pristine white-sand beaches, and luxurious overwater bungalows. It’s the ultimate destination for romance, relaxation, and world-class scuba diving. Discover vibrant coral reefs teeming with marine life or simply unwind to the sound of gentle waves beneath a starry sky.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Top locations to stay in the Maldives</h3>
<ul style="list-style: none; padding-left: 0;">
    <li style="margin-bottom: 15px;"><strong>North Malé Atoll:</strong> Conveniently close to the international airport, offering a wide range of luxury resorts and excellent surf breaks.</li>
    <li style="margin-bottom: 15px;"><strong>South Ari Atoll:</strong> Renowned for its incredible marine life, making it one of the best spots in the world for swimming with whale sharks and manta rays.</li>
    <li style="margin-bottom: 15px;"><strong>Baa Atoll:</strong> A UNESCO Biosphere Reserve, offering untouched natural beauty and unparalleled snorkeling experiences in Hanifaru Bay.</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">4 tips for savvy savings when booking a hotel in the Maldives</h3>
<p><strong>Book for the cheapest times:</strong> The low season, from May to October, offers significantly discounted rates (though you may encounter some rain).</p>
<p><strong>Consider All-Inclusive Packages:</strong> Dining on remote islands can be very expensive; all-inclusive plans often provide the best overall value.</p>
<p><strong>Check transfer costs:</strong> Seaplane transfers can add significantly to your budget, so consider resorts accessible by a shorter speedboat ride.</p>
<p><strong>Look for local islands:</strong> Guesthouses on local islands offer a much more budget-friendly and culturally immersive alternative to luxury private island resorts.</p>
"""


create_blog('templates/blog-india.html', 'Hotels in India', 'Unearth the Wonders of India: A Tapestry of Temples and Timeless Treasures', 'fa-om', india_html, 'https://images.unsplash.com/photo-1524492412937-b28074a5d7da?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')
create_blog('templates/blog-uae.html', 'Hotels in United Arab Emirates', 'Whispers of the Dunes: A Tapestry of Desert Dreams and Coastal Wonders', 'fa-mosque', uae_html, 'https://images.unsplash.com/photo-1512453979798-5ea266f8880c?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')
create_blog('templates/blog-uk.html', 'Hotels in United Kingdom', 'Enchanting Escapades: Discover the Timeless Treasures of the United Kingdom', 'fa-chess-rook', uk_html, 'https://images.unsplash.com/photo-1513635269975-59663e0ac1ad?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')
create_blog('templates/blog-usa.html', 'Hotels in United States of America', 'Discover the Tapestry of America: Nature, Culture, and Adventure Awaits', 'fa-flag-usa', usa_html, 'https://images.unsplash.com/photo-1501504905252-473c47e087f8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')
create_blog('templates/blog-indonesia.html', 'Hotels in Indonesia', 'Embrace the Enchantment of Indonesia: Where Temples Meet Tranquil Shores', 'fa-water', indonesia_html, 'https://images.unsplash.com/photo-1537996194471-e657df975ab4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')
create_blog('templates/blog-singapore.html', 'Hotels in Singapore', 'Singapore: A Tapestry of Urban Gardens and Cultural Wonders', 'fa-city', singapore_html, 'https://images.unsplash.com/photo-1525625293386-3f8f99389edd?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')
create_blog('templates/blog-maldives.html', 'Hotels in Maldives', 'Maldives: The Ultimate Tropical Paradise', 'fa-umbrella-beach', maldives_html, 'https://images.unsplash.com/photo-1514282401047-d79a71a590e8?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80')

