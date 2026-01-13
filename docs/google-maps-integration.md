# Google Maps Integration Guide

## Overview

This document describes how to set up and use Google Maps API for hotel location display and geocoding in Coast to Coast Journeys.

## Required APIs

Enable these APIs in [Google Cloud Console](https://console.cloud.google.com/):

| API | Purpose | Cost* |
|-----|---------|-------|
| Maps JavaScript API | Interactive maps on frontend | $7/1K loads |
| Geocoding API | Address to coordinates | $5/1K requests |
| Places API | Place search and details | $17-32/1K |
| Distance Matrix API | Distance calculations | $5-10/1K |
| Static Maps API | Map images | $2/1K |

*Cost is after $200/month free credit

## Setup Steps

### 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create new project or select existing
3. Enable billing (required for API access)

### 2. Enable Required APIs

1. Go to "APIs & Services" → "Library"
2. Search and enable each API listed above
3. At minimum, enable:
   - Maps JavaScript API
   - Geocoding API
   - Places API

### 3. Create API Key

1. Go to "APIs & Services" → "Credentials"
2. Click "Create Credentials" → "API Key"
3. Restrict your API key:
   - **Application restrictions**: HTTP referrers
   - Add your domains:
     - `localhost:*`
     - `127.0.0.1:*`
     - `yourdomain.com/*`
   - **API restrictions**: Restrict to enabled APIs

### 4. Add to Environment

Add your API key to `.env` file:

```env
GOOGLE_MAPS_API_KEY=AIzaSy...your_api_key...
```

## Frontend Integration

### Add Script to HTML

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&libraries=places" async defer></script>
```

### Initialize Map

```javascript
function initMap() {
    const map = new google.maps.Map(document.getElementById('map'), {
        center: { lat: 28.6139, lng: 77.2090 }, // New Delhi
        zoom: 12
    });
}
```

### Add Hotel Marker

```javascript
function addHotelMarker(map, hotel) {
    const marker = new google.maps.Marker({
        position: { lat: hotel.latitude, lng: hotel.longitude },
        map: map,
        title: hotel.name,
        icon: {
            url: '/assets/icons/hotel-marker.png',
            scaledSize: new google.maps.Size(40, 40)
        }
    });
    
    const infoWindow = new google.maps.InfoWindow({
        content: `
            <div class="hotel-info">
                <h3>${hotel.name}</h3>
                <p>${hotel.address}</p>
                <p>₹${hotel.price}/night</p>
            </div>
        `
    });
    
    marker.addListener('click', () => {
        infoWindow.open(map, marker);
    });
}
```

## Backend API Usage

### Geocode Address

```python
from services.google_maps_service import google_maps_service

result = google_maps_service.geocode("Taj Mahal, Agra, India")
if result['success']:
    lat = result['data']['latitude']
    lng = result['data']['longitude']
```

### Search Hotels Near Location

```python
result = google_maps_service.search_places(
    query="hotels",
    location=(28.6139, 77.2090),  # Delhi
    radius=5000,
    place_type="lodging"
)
```

### Calculate Distance

```python
result = google_maps_service.calculate_distance(
    origin="Delhi Airport",
    destination="The Leela Palace, Delhi",
    mode="driving"
)
# Returns: distance_text, duration_text
```

### Static Map URL

```python
url = google_maps_service.get_static_map_url(
    latitude=28.6139,
    longitude=77.2090,
    zoom=15,
    size="600x300"
)
# Use this URL in <img src="...">
```

## Cost Management

### Tips to Reduce Costs:

1. **Cache geocoding results** - Don't geocode same address twice
2. **Use autocomplete wisely** - Debounce user input (300ms)
3. **Limit Places API details** - Only request needed fields
4. **Use Static Maps** - For non-interactive displays

### Set Billing Alerts:

1. Go to Cloud Console → Billing
2. Set budget alerts at 50%, 90%, 100%
3. Monitor usage in dashboard

## Security Best Practices

1. **Restrict API Key** by referrer
2. **Never expose** service-side keys to frontend
3. **Use separate keys** for frontend and backend
4. **Monitor quota usage** regularly
5. **Regenerate keys** if compromised

## Troubleshooting

| Issue | Solution |
|-------|----------|
| API key not working | Check restrictions, quota, billing |
| Map not loading | Verify script URL, check console errors |
| Geocoding fails | Check address format, API quota |
| High costs | Implement caching, reduce API calls |
