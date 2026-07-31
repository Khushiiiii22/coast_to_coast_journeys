import re

def update_blog(filename, new_title, new_content_html):
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the inner content
    # We look for <div class="content-wrapper policy-content"> and replace everything inside it until </main> (or the next section)
    # Actually, in the previous script, I replaced everything from <div class="policy-intro"> to <section class="contact-section">
    # Let's just find the <div class="content-wrapper policy-content"> and replace its contents.
    
    # regex to match <div class="content-wrapper policy-content">...</div>
    # It's safer to use split and replace
    
    start_marker = '<div class="content-wrapper policy-content">'
    end_marker = '</main>'
    
    start_idx = content.find(start_marker)
    end_idx = content.find(end_marker, start_idx)
    
    if start_idx != -1 and end_idx != -1:
        # Keep the wrapper div open
        before = content[:start_idx + len(start_marker)]
        # We need to find the closing div of content-wrapper. It's right before </main> usually.
        after = content[end_idx:]
        
        # We just insert the new_content_html and a closing </div> before after
        new_full_content = before + "\n" + new_content_html + "\n</div>\n" + after
        
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(new_full_content)
        print(f"Updated {filename}")
    else:
        print(f"Could not find markers in {filename}")

beach_html = """
<div style="margin-bottom: 30px;">
    <img src="https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?ixlib=rb-4.0.3&auto=format&fit=crop&w=1200&q=80" alt="Beach Resort" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
</div>
<p style="font-size: 1.1rem; line-height: 1.8;">There's something about the sound of waves outside your window that no city skyline can match. Whether you're planning a honeymoon, a family escape, or a solo reset, the United States is packed with oceanfront properties that rival anything you'd find overseas. Here are ten of the best.</p>

<h3 style="margin-top: 30px; color: var(--primary);">1. The Breakers — Palm Beach, Florida</h3>
<p>An Italian Renaissance-style landmark on Florida's Gold Coast, The Breakers pairs old-world grandeur with a private beach, two championship golf courses, and a spa that could headline its own vacation.</p>

<h3 style="margin-top: 30px; color: var(--primary);">2. Montage Laguna Beach — California</h3>
<p>Perched on a bluff above the Pacific, Montage Laguna Beach blends Craftsman-style architecture with sweeping ocean views. The coastal boardwalk and tide pools right below the property make it a favorite for families.</p>

<h3 style="margin-top: 30px; color: var(--primary);">3. Casa Marina, A Waldorf Astoria Resort — Key West, Florida</h3>
<p>Built in 1920 as Henry Flagler's last great railroad hotel, Casa Marina sits on the widest private beach in Key West, with sunset views and a laid-back island rhythm.</p>

<h3 style="margin-top: 30px; color: var(--primary);">4. The Ritz-Carlton, Naples — Florida</h3>
<p>Consistently ranked among the top beach resorts in the country, this Gulf Coast property offers three miles of white-sand beach, a Turkish-style spa, and some of the best sunset views in Florida.</p>

<h3 style="margin-top: 30px; color: var(--primary);">5. Ocean House — Watch Hill, Rhode Island</h3>
<p>A New England classic reimagined, Ocean House sits on a bluff above its own private beach, with a wraparound porch, a wine cellar, and understated coastal elegance.</p>

<h3 style="margin-top: 30px; color: var(--primary);">6. Four Seasons Resort Maui at Wailea — Hawaii</h3>
<p>On Maui's sunny south shore, this resort offers adults-only pools, a full-service spa, and some of the most attentive service in the Hawaiian Islands.</p>

<h3 style="margin-top: 30px; color: var(--primary);">7. The Cloister at Sea Island — Georgia</h3>
<p>A Southern institution since 1928, Sea Island offers five miles of private beach, championship golf, and a level of hospitality that feels handed down through generations.</p>

<h3 style="margin-top: 30px; color: var(--primary);">8. Rosewood Miramar Beach — Montecito, California</h3>
<p>Set on Butterfly Beach with the Santa Ynez Mountains as a backdrop, Rosewood Miramar mixes California cool with genuine luxury, including beachfront cabanas and a farm-to-table dining scene.</p>

<h3 style="margin-top: 30px; color: var(--primary);">9. The St. Regis Bal Harbour Resort — Miami, Florida</h3>
<p>Old-school St. Regis service meets Miami glamour, with a private beach, a Remède Spa, and butler service on every floor.</p>

<h3 style="margin-top: 30px; color: var(--primary);">10. Hotel del Coronado — San Diego, California</h3>
<p>An icon since 1888, "The Del" is instantly recognizable, with its red-turreted Victorian architecture rising straight out of the sand on Coronado Island.</p>

<div style="background: #f8fafc; padding: 20px; border-left: 4px solid var(--primary); border-radius: 4px; margin-top: 40px;">
    <h4 style="margin-top: 0;">Booking Tip</h4>
    <p style="margin-bottom: 0;">Peak beach season varies by coast — Florida and the Gulf Coast fill up in winter, while California and New England peak in summer. Book 3–6 months out for the best rates, and always check for resort credits or free-night promotions before you pay full price.</p>
</div>
"""

nyc_html = """
<div style="margin-bottom: 30px;">
    <img src="https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=1200&q=80" alt="New York City" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
</div>
<p style="font-size: 1.1rem; line-height: 1.8;">New York City is huge, and picking the wrong neighborhood can mean an hour of subway transfers between everything you actually want to see. Here's a first-timer's breakdown of the best areas to base yourself, depending on what kind of trip you're after.</p>

<h3 style="margin-top: 30px; color: var(--primary);">Midtown Manhattan — Best for First-Time Sightseers</h3>
<p>If it's your first visit and you want to check off the classics — Times Square, Broadway, Rockefeller Center, the Empire State Building — Midtown puts you within walking distance of nearly all of it. It's loud, bright, and touristy, but it's also incredibly convenient, with subway lines running in every direction.</p>
<ul style="list-style-type: disc; margin-left: 20px; color: #475569;">
    <li><strong>Good for:</strong> first-timers, theater lovers, short trips</li>
    <li><strong>Watch out for:</strong> higher hotel prices and heavy foot traffic</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">The Upper West Side — Best for a Quieter Homebase</h3>
<p>Tree-lined streets, Central Park on one side, and a genuinely residential feel make the Upper West Side a favorite for travelers who still want to be close to the action without the Times Square chaos. It's an easy walk to the Museum of Natural History and Lincoln Center.</p>
<ul style="list-style-type: disc; margin-left: 20px; color: #475569;">
    <li><strong>Good for:</strong> families, culture lovers, longer stays</li>
    <li><strong>Watch out for:</strong> fewer late-night dining options than downtown</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">Chelsea — Best for Food, Art, and Nightlife</h3>
<p>Home to the High Line, Chelsea Market, and a dense cluster of art galleries, Chelsea has become one of the most walkable and stylish neighborhoods in Manhattan. It's central enough to reach most of the island quickly, with a more local, less frantic energy than Midtown.</p>
<ul style="list-style-type: disc; margin-left: 20px; color: #475569;">
    <li><strong>Good for:</strong> foodies, art lovers, couples</li>
    <li><strong>Watch out for:</strong> can get pricey on weekends</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">SoHo & the West Village — Best for Boutique Charm</h3>
<p>Cobblestone streets, cast-iron architecture, and some of the city's best shopping and people-watching make SoHo and the West Village a top pick for travelers who want a more intimate, less corporate New York experience.</p>
<ul style="list-style-type: disc; margin-left: 20px; color: #475569;">
    <li><strong>Good for:</strong> shopping, romantic getaways, boutique hotels</li>
    <li><strong>Watch out for:</strong> fewer big chain hotels, so book early</li>
</ul>

<h3 style="margin-top: 30px; color: var(--primary);">Brooklyn (Williamsburg & DUMBO) — Best for a Local Feel and Value</h3>
<p>Staying across the river gets you some of the best skyline views in the city, better hotel prices, and a genuinely local vibe — all just one or two subway stops from Manhattan. DUMBO in particular offers a postcard-perfect view of the Manhattan Bridge.</p>
<ul style="list-style-type: disc; margin-left: 20px; color: #475569;">
    <li><strong>Good for:</strong> budget-conscious travelers, photographers, longer stays</li>
    <li><strong>Watch out for:</strong> a slightly longer commute into central Manhattan</li>
</ul>

<div style="background: #f8fafc; padding: 20px; border-left: 4px solid var(--primary); border-radius: 4px; margin-top: 40px;">
    <h4 style="margin-top: 0;">Booking Tip</h4>
    <p style="margin-bottom: 0;">Manhattan hotel prices swing significantly by season — expect the highest rates around the winter holidays and lowest in January and February (excluding major events). If you're flexible, shoulder-season trips in spring or fall get you great weather without peak pricing.</p>
</div>
"""

vegas_html = """
<div style="margin-bottom: 30px;">
    <img src="https://images.unsplash.com/photo-1605810230434-7631ac76ec81?auto=format&fit=crop&w=1200&q=80" alt="Las Vegas" style="width: 100%; border-radius: 12px; object-fit: cover; max-height: 400px;">
</div>
<p style="font-size: 1.1rem; line-height: 1.8;">A room upgrade in Vegas can mean the difference between a standard box on floor 12 and a suite with a Strip view and a soaking tub. You don't need to be a high roller to get one — you just need to know how the game works.</p>

<h3 style="margin-top: 30px; color: var(--primary);">1. Join the Hotel's Loyalty Program Before You Book</h3>
<p>Every major Vegas resort brand — Caesars Rewards, MGM Rewards, Wyndham, Hilton Honors — has a free loyalty tier that puts you ahead of walk-in guests for upgrades. Sign up before you book, not at check-in, so your reservation is linked to your account from the start.</p>

<h3 style="margin-top: 30px; color: var(--primary);">2. Book Directly With the Hotel, Not a Third Party</h3>
<p>Rooms booked through the hotel's own website or app are far more likely to be flagged for a complimentary upgrade than rooms booked through third-party travel sites. Direct bookings also make it easier for the front desk to modify your reservation on the spot.</p>

<h3 style="margin-top: 30px; color: var(--primary);">3. Check In Later in the Day</h3>
<p>Upgrades usually happen when the hotel has a clearer picture of unsold inventory — which is typically mid-afternoon to early evening. Checking in around 4–6 PM, rather than the moment rooms open at 3 PM, can improve your odds simply because staff know what's actually available to give away.</p>

<h3 style="margin-top: 30px; color: var(--primary);">4. Be Polite, Not Demanding</h3>
<p>Front desk staff have discretion over upgrades, and that discretion tends to go to guests who are friendly and low-maintenance. A simple, warm "Is there any chance of a room with a better view?" goes a lot further than an entitled ask.</p>

<h3 style="margin-top: 30px; color: var(--primary);">5. Mention Special Occasions</h3>
<p>Birthdays, anniversaries, honeymoons, and other special occasions are commonly rewarded with a small upgrade or a room with a better view — especially if you note it in the special requests field when booking.</p>

<h3 style="margin-top: 30px; color: var(--primary);">6. Travel on Weekdays or During Slower Periods</h3>
<p>Vegas hotels are busiest Friday through Sunday and during major conventions or fights. Staying Sunday through Thursday, or avoiding peak convention weeks, means more unsold premium rooms available to hand out.</p>

<h3 style="margin-top: 30px; color: var(--primary);">7. Use Elite Status, Even at the Lowest Tier</h3>
<p>You don't need top-tier status to benefit. Even the entry-level free tier of most casino loyalty programs flags you in the system as a member, which alone can bump you ahead of unaffiliated guests.</p>

<h3 style="margin-top: 30px; color: var(--primary);">8. Ask About "Resort Credit" Room Categories</h3>
<p>Some hotels offer bookable room categories that come bundled with resort credit, spa access, or pool cabana perks — effectively an upgrade you can book outright rather than hope for. Ask reservations about these when you book.</p>

<div style="background: #fff1f2; padding: 20px; border-left: 4px solid #e11d48; border-radius: 4px; margin-top: 40px;">
    <h4 style="margin-top: 0; color: #be123c;">What Not to Do</h4>
    <p style="margin-bottom: 0; color: #881337;">Don't try to bribe front desk staff — it's against most hotel policies and can backfire. And don't ask before your reservation is even pulled up; let the agent see your booking and status first.</p>
</div>
"""

update_blog('templates/blog-beach-resorts.html', 'The 10 Best Luxury Beach Resorts in the US', beach_html)
update_blog('templates/blog-nyc-guide.html', "Where to Stay in New York City: First Timer's Guide", nyc_html)
update_blog('templates/blog-vegas-upgrades.html', 'How to Score Free Room Upgrades in Las Vegas', vegas_html)

