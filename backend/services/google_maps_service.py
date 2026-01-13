"""
Coast to Coast Journeys - Google Maps Service
Handles Google Maps integration for hotel location and mapping
"""
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Only import googlemaps if API key is configured
try:
    import googlemaps
    GOOGLEMAPS_AVAILABLE = True
except ImportError:
    GOOGLEMAPS_AVAILABLE = False
    print("⚠️  Warning: googlemaps package not installed. Run: pip install googlemaps")


class GoogleMapsService:
    """Service class for Google Maps operations"""
    
    def __init__(self):
        """Initialize Google Maps client"""
        self.api_key = Config.GOOGLE_MAPS_API_KEY
        self.client = None
        
        if self.api_key and self.api_key != 'your_google_maps_api_key' and GOOGLEMAPS_AVAILABLE:
            try:
                self.client = googlemaps.Client(key=self.api_key)
            except ValueError as e:
                print(f"⚠️  Warning: Google Maps API key invalid: {e}")
                self.client = None
        elif not self.api_key or self.api_key == 'your_google_maps_api_key':
            print("⚠️  Warning: Google Maps API key not configured")
    
    def is_available(self) -> bool:
        """Check if Google Maps service is available"""
        return self.client is not None
    
    def geocode(self, address: str) -> dict:
        """
        Convert address to coordinates
        
        Args:
            address: Address string (e.g., "Taj Mahal, Agra, India")
        
        Returns:
            dict with lat, lng, formatted_address
        """
        if not self.is_available():
            return {"success": False, "error": "Google Maps not configured"}
        
        try:
            result = self.client.geocode(address)
            
            if result:
                location = result[0]['geometry']['location']
                return {
                    "success": True,
                    "data": {
                        "latitude": location['lat'],
                        "longitude": location['lng'],
                        "formatted_address": result[0]['formatted_address'],
                        "place_id": result[0].get('place_id')
                    }
                }
            else:
                return {"success": False, "error": "No results found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def reverse_geocode(self, latitude: float, longitude: float) -> dict:
        """
        Convert coordinates to address
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
        
        Returns:
            dict with address information
        """
        if not self.is_available():
            return {"success": False, "error": "Google Maps not configured"}
        
        try:
            result = self.client.reverse_geocode((latitude, longitude))
            
            if result:
                return {
                    "success": True,
                    "data": {
                        "formatted_address": result[0]['formatted_address'],
                        "place_id": result[0].get('place_id'),
                        "address_components": result[0].get('address_components', [])
                    }
                }
            else:
                return {"success": False, "error": "No results found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_places(
        self,
        query: str,
        location: tuple = None,
        radius: int = 5000,
        place_type: str = "lodging"
    ) -> dict:
        """
        Search for places (hotels, landmarks, etc.)
        
        Args:
            query: Search query
            location: (latitude, longitude) tuple for location bias
            radius: Search radius in meters
            place_type: Type of place (lodging, restaurant, etc.)
        
        Returns:
            List of places
        """
        if not self.is_available():
            return {"success": False, "error": "Google Maps not configured"}
        
        try:
            if location:
                result = self.client.places(
                    query=query,
                    location=location,
                    radius=radius,
                    type=place_type
                )
            else:
                result = self.client.places(query=query, type=place_type)
            
            places = []
            for place in result.get('results', []):
                places.append({
                    "name": place.get('name'),
                    "address": place.get('formatted_address'),
                    "place_id": place.get('place_id'),
                    "rating": place.get('rating'),
                    "user_ratings_total": place.get('user_ratings_total'),
                    "latitude": place['geometry']['location']['lat'],
                    "longitude": place['geometry']['location']['lng'],
                    "types": place.get('types', []),
                    "photos": place.get('photos', [])
                })
            
            return {"success": True, "data": places}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_place_details(self, place_id: str) -> dict:
        """
        Get detailed information about a place
        
        Args:
            place_id: Google Place ID
        
        Returns:
            Detailed place information
        """
        if not self.is_available():
            return {"success": False, "error": "Google Maps not configured"}
        
        try:
            result = self.client.place(
                place_id=place_id,
                fields=[
                    'name', 'formatted_address', 'formatted_phone_number',
                    'website', 'rating', 'reviews', 'photos', 'opening_hours',
                    'geometry', 'price_level', 'url'
                ]
            )
            
            if result.get('result'):
                place = result['result']
                location = place.get('geometry', {}).get('location', {})
                
                return {
                    "success": True,
                    "data": {
                        "name": place.get('name'),
                        "address": place.get('formatted_address'),
                        "phone": place.get('formatted_phone_number'),
                        "website": place.get('website'),
                        "rating": place.get('rating'),
                        "reviews": place.get('reviews', []),
                        "latitude": location.get('lat'),
                        "longitude": location.get('lng'),
                        "google_maps_url": place.get('url'),
                        "price_level": place.get('price_level'),
                        "opening_hours": place.get('opening_hours', {})
                    }
                }
            else:
                return {"success": False, "error": "Place not found"}
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def calculate_distance(
        self,
        origin: str,
        destination: str,
        mode: str = "driving"
    ) -> dict:
        """
        Calculate distance and duration between two locations
        
        Args:
            origin: Starting address or coordinates
            destination: Ending address or coordinates
            mode: Travel mode (driving, walking, bicycling, transit)
        
        Returns:
            Distance and duration information
        """
        if not self.is_available():
            return {"success": False, "error": "Google Maps not configured"}
        
        try:
            result = self.client.distance_matrix(
                origins=[origin],
                destinations=[destination],
                mode=mode,
                units="metric"
            )
            
            if result['rows'][0]['elements'][0]['status'] == 'OK':
                element = result['rows'][0]['elements'][0]
                return {
                    "success": True,
                    "data": {
                        "distance_text": element['distance']['text'],
                        "distance_meters": element['distance']['value'],
                        "duration_text": element['duration']['text'],
                        "duration_seconds": element['duration']['value'],
                        "mode": mode
                    }
                }
            else:
                return {
                    "success": False,
                    "error": result['rows'][0]['elements'][0]['status']
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_static_map_url(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 15,
        size: str = "600x300",
        markers: list = None
    ) -> str:
        """
        Generate a static map URL for embedding
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            zoom: Zoom level (1-21)
            size: Image size (widthxheight)
            markers: List of marker coordinates [(lat, lng), ...]
        
        Returns:
            Static map URL
        """
        if not self.api_key:
            return None
        
        base_url = "https://maps.googleapis.com/maps/api/staticmap"
        
        url = f"{base_url}?center={latitude},{longitude}&zoom={zoom}&size={size}&key={self.api_key}"
        
        # Add center marker
        url += f"&markers=color:red|{latitude},{longitude}"
        
        # Add additional markers
        if markers:
            for lat, lng in markers:
                url += f"&markers=color:blue|{lat},{lng}"
        
        return url
    
    def get_embed_url(
        self,
        latitude: float,
        longitude: float,
        zoom: int = 15
    ) -> str:
        """
        Generate an embeddable map URL
        
        Args:
            latitude: Center latitude
            longitude: Center longitude
            zoom: Zoom level
        
        Returns:
            Embed URL for iframe
        """
        if not self.api_key:
            return None
        
        return f"https://www.google.com/maps/embed/v1/view?key={self.api_key}&center={latitude},{longitude}&zoom={zoom}"


# Configuration requirements for Google Maps
GOOGLE_MAPS_REQUIREMENTS = """
# Google Maps Integration Requirements

## Required APIs (enable in Google Cloud Console):
1. Maps JavaScript API - For interactive maps on frontend
2. Geocoding API - For address to coordinates conversion
3. Places API - For place search and details
4. Distance Matrix API - For distance calculations (optional)
5. Static Maps API - For map images (optional)

## Setup Steps:
1. Go to Google Cloud Console: https://console.cloud.google.com/
2. Create a new project or select existing
3. Enable the required APIs above
4. Create an API key with appropriate restrictions
5. Add the API key to your .env file

## Frontend Integration (add to your HTML):
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places"></script>

## Cost Considerations:
- Free tier: $200/month credit (good for small projects)
- Geocoding: $5 per 1,000 requests
- Places: $17-32 per 1,000 requests
- Distance Matrix: $5-10 per 1,000 elements

## Security:
- Restrict API key to your domain
- Enable billing alerts
- Monitor usage in Cloud Console
"""


# Singleton instance
google_maps_service = GoogleMapsService()
