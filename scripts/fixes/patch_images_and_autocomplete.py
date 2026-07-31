import sys

file_path = "backend/routes/hotel_routes.py"
with open(file_path, "r") as f:
    content = f.read()

# 1. Update image fallback
old_image_fallback = """        # 3. Use fallback only as last resort
        if not all_images:
            all_images = ['https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600']"""

new_image_fallback = """        # 3. Use fallback only as last resort
        if not all_images:
            fallback_images = [
                'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600',
                'https://images.unsplash.com/photo-1582719478250-c894e4dc240e?w=600',
                'https://images.unsplash.com/photo-1542314831-c6a4d14d8373?w=600',
                'https://images.unsplash.com/photo-1571003123894-1f0594d2b5d9?w=600',
                'https://images.unsplash.com/photo-1551882547-ff40c0d5b5fa?w=600',
                'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600',
                'https://images.unsplash.com/photo-1445019980597-93fa8acb246c?w=600',
                'https://images.unsplash.com/photo-1496417263034-38ec4f0b665a?w=600',
                'https://images.unsplash.com/photo-1512918728675-ed5a9ecdebfd?w=600',
                'https://images.unsplash.com/photo-1590490360182-c33d57733427?w=600'
            ]
            all_images = [fallback_images[idx % len(fallback_images)]]"""

content = content.replace(old_image_fallback, new_image_fallback)


# 2. Update Autocomplete fallback list
old_autocomplete = """            # Return fallback with popular matching cities
            popular = [
                {'description': 'Mumbai, Maharashtra, India', 'types': ['locality'], 'structured_formatting': {'main_text': 'Mumbai', 'secondary_text': 'Maharashtra, India'}},
                {'description': 'Delhi, India', 'types': ['locality'], 'structured_formatting': {'main_text': 'Delhi', 'secondary_text': 'India'}},
                {'description': 'Dubai, United Arab Emirates', 'types': ['locality'], 'structured_formatting': {'main_text': 'Dubai', 'secondary_text': 'United Arab Emirates'}},
                {'description': 'Paris, France', 'types': ['locality'], 'structured_formatting': {'main_text': 'Paris', 'secondary_text': 'France'}},
                {'description': 'London, United Kingdom', 'types': ['locality'], 'structured_formatting': {'main_text': 'London', 'secondary_text': 'United Kingdom'}},
            ]"""

new_autocomplete = """            # Return fallback with popular matching cities
            popular = [
                {'description': 'Mumbai, Maharashtra, India', 'types': ['locality'], 'structured_formatting': {'main_text': 'Mumbai', 'secondary_text': 'Maharashtra, India'}},
                {'description': 'Delhi, India', 'types': ['locality'], 'structured_formatting': {'main_text': 'Delhi', 'secondary_text': 'India'}},
                {'description': 'Dubai, United Arab Emirates', 'types': ['locality'], 'structured_formatting': {'main_text': 'Dubai', 'secondary_text': 'United Arab Emirates'}},
                {'description': 'Paris, France', 'types': ['locality'], 'structured_formatting': {'main_text': 'Paris', 'secondary_text': 'France'}},
                {'description': 'London, United Kingdom', 'types': ['locality'], 'structured_formatting': {'main_text': 'London', 'secondary_text': 'United Kingdom'}},
                {'description': 'Lima, Peru', 'types': ['locality'], 'structured_formatting': {'main_text': 'Lima', 'secondary_text': 'Peru'}},
                {'description': 'Dallas, Texas', 'types': ['locality'], 'structured_formatting': {'main_text': 'Dallas', 'secondary_text': 'Texas, USA'}},
                {'description': 'Houston, Texas', 'types': ['locality'], 'structured_formatting': {'main_text': 'Houston', 'secondary_text': 'Texas, USA'}},
                {'description': 'Austin, Texas', 'types': ['locality'], 'structured_formatting': {'main_text': 'Austin', 'secondary_text': 'Texas, USA'}},
                {'description': 'New York City, New York', 'types': ['locality'], 'structured_formatting': {'main_text': 'New York City', 'secondary_text': 'New York, USA'}},
                {'description': 'Los Angeles, California', 'types': ['locality'], 'structured_formatting': {'main_text': 'Los Angeles', 'secondary_text': 'California, USA'}},
                {'description': 'Chicago, Illinois', 'types': ['locality'], 'structured_formatting': {'main_text': 'Chicago', 'secondary_text': 'Illinois, USA'}},
                {'description': 'Tokyo, Japan', 'types': ['locality'], 'structured_formatting': {'main_text': 'Tokyo', 'secondary_text': 'Japan'}},
                {'description': 'Rome, Italy', 'types': ['locality'], 'structured_formatting': {'main_text': 'Rome', 'secondary_text': 'Italy'}},
                {'description': 'Cusco, Peru', 'types': ['locality'], 'structured_formatting': {'main_text': 'Cusco', 'secondary_text': 'Peru'}},
                {'description': 'Cancun, Mexico', 'types': ['locality'], 'structured_formatting': {'main_text': 'Cancun', 'secondary_text': 'Mexico'}},
                {'description': 'Bangkok, Thailand', 'types': ['locality'], 'structured_formatting': {'main_text': 'Bangkok', 'secondary_text': 'Thailand'}},
                {'description': 'Sydney, Australia', 'types': ['locality'], 'structured_formatting': {'main_text': 'Sydney', 'secondary_text': 'Australia'}},
                {'description': 'Toronto, Canada', 'types': ['locality'], 'structured_formatting': {'main_text': 'Toronto', 'secondary_text': 'Canada'}}
            ]"""

content = content.replace(old_autocomplete, new_autocomplete)

with open(file_path, "w") as f:
    f.write(content)

print("Patch applied successfully.")
