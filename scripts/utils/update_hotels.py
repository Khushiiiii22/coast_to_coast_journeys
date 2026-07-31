import re

filepath = 'templates/hotel-booking.html'
with open(filepath, 'r') as f:
    content = f.read()

# Replace Header
content = content.replace('<h2>Hotels in Mumbai</h2>', '<h2>5 Star Hotels in United States</h2>')
content = content.replace('Showing 156 properties', 'Showing Top 5 Luxury Properties')

# Hotel 1
content = content.replace('The Taj Mahal Palace', 'The Plaza')
content = content.replace('Colaba, Mumbai • 2.5 km from center', 'New York City, NY • 0.5 km from center')
content = content.replace('$15,999', '$850')
content = content.replace('https://images.unsplash.com/photo-1566073771259-6a8506099945?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', 'https://images.unsplash.com/photo-1578683010236-d716f9a3f461?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80')

# Hotel 2
content = content.replace('The Oberoi Mumbai', 'The Beverly Hills Hotel')
content = content.replace('Nariman Point, Mumbai • 1.2 km from center', 'Los Angeles, CA • 2.0 km from center')
content = content.replace('$14,500', '$1,200')
content = content.replace('https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', 'https://images.unsplash.com/photo-1582719508461-905c673771fd?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80')

# Hotel 3
content = content.replace('ITC Grand Central', 'Bellagio Hotel & Casino')
content = content.replace('Parel, Mumbai • 4.8 km from center', 'Las Vegas, NV • 0.1 km from center')
content = content.replace('$12,000', '$650')
content = content.replace('https://images.unsplash.com/photo-1551882547-ff40c0d509af?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', 'https://images.unsplash.com/photo-1605810230434-7631ac76ec81?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80')

# Hotel 4
content = content.replace('Trident Nariman Point', 'Four Seasons Resort Maui')
content = content.replace('Nariman Point, Mumbai • 0.8 km from center', 'Wailea, HI • Beachfront')
content = content.replace('$11,500', '$1,450')
content = content.replace('https://images.unsplash.com/photo-1522798514-97ceb8c4f1c8?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', 'https://images.unsplash.com/photo-1540541338287-41700207dee6?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80')

# Hotel 5
content = content.replace('JW Marriott Mumbai Juhu', 'The Waldorf Astoria')
content = content.replace('Juhu Beach, Mumbai • 12 km from center', 'Chicago, IL • 1.2 km from center')
content = content.replace('$13,500', '$750')
content = content.replace('https://images.unsplash.com/photo-1517840901100-8179e982acb7?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80', 'https://images.unsplash.com/photo-1564501049412-61c2a3083791?ixlib=rb-4.0.3&auto=format&fit=crop&w=600&q=80')

# Also replace the default 'Mumbai' in JS autocomplete searchString exclusions/fallback
content = content.replace("const destination = document.getElementById('destination').value || 'Mumbai';", "const destination = document.getElementById('destination').value || 'New York';")

with open(filepath, 'w') as f:
    f.write(content)

print("Updated hotel-booking.html to US Hotels")
