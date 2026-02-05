"""
C2C Journeys - Map Routes
API routes for Google Maps integration
"""
from flask import Blueprint, request, jsonify, redirect
from services.google_maps_service import google_maps_service

maps_bp = Blueprint('maps', __name__, url_prefix='/api/maps')


@maps_bp.route('/status', methods=['GET'])
def maps_status():
    """Check if Google Maps service is available"""
    return jsonify({
        'available': google_maps_service.is_available(),
        'message': 'Google Maps API is configured' if google_maps_service.is_available() else 'Google Maps API key not configured'
    })


@maps_bp.route('/geocode', methods=['POST'])
def geocode():
    """
    Convert address to coordinates
    
    Request Body:
    {
        "address": "Taj Mahal, Agra, India"
    }
    """
    try:
        data = request.get_json()
        
        if 'address' not in data:
            return jsonify({'success': False, 'error': 'Missing address'}), 400
        
        result = google_maps_service.geocode(data['address'])
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@maps_bp.route('/reverse-geocode', methods=['POST'])
def reverse_geocode():
    """
    Convert coordinates to address
    
    Request Body:
    {
        "latitude": 27.1751,
        "longitude": 78.0421
    }
    """
    try:
        data = request.get_json()
        
        if 'latitude' not in data or 'longitude' not in data:
            return jsonify({'success': False, 'error': 'Missing latitude or longitude'}), 400
        
        result = google_maps_service.reverse_geocode(
            data['latitude'],
            data['longitude']
        )
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@maps_bp.route('/search', methods=['POST'])
def search_places():
    """
    Search for places (hotels, landmarks, etc.)
    
    Request Body:
    {
        "query": "hotels in Goa",
        "latitude": 15.2993,
        "longitude": 74.1240,
        "radius": 10000,
        "type": "lodging"
    }
    """
    try:
        data = request.get_json()
        
        if 'query' not in data:
            return jsonify({'success': False, 'error': 'Missing query'}), 400
        
        location = None
        if 'latitude' in data and 'longitude' in data:
            location = (data['latitude'], data['longitude'])
        
        result = google_maps_service.search_places(
            query=data['query'],
            location=location,
            radius=data.get('radius', 5000),
            place_type=data.get('type', 'lodging')
        )
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@maps_bp.route('/place/<place_id>', methods=['GET'])
def get_place_details(place_id):
    """Get detailed information about a place"""
    try:
        result = google_maps_service.get_place_details(place_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@maps_bp.route('/distance', methods=['POST'])
def calculate_distance():
    """
    Calculate distance between two locations
    
    Request Body:
    {
        "origin": "Delhi Airport",
        "destination": "Taj Hotel, New Delhi",
        "mode": "driving"
    }
    """
    try:
        data = request.get_json()
        
        if 'origin' not in data or 'destination' not in data:
            return jsonify({'success': False, 'error': 'Missing origin or destination'}), 400
        
        result = google_maps_service.calculate_distance(
            origin=data['origin'],
            destination=data['destination'],
            mode=data.get('mode', 'driving')
        )
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@maps_bp.route('/static-map', methods=['GET'])
def get_static_map():
    """
    Get static map URL for embedding
    
    Query Params:
        latitude: Center latitude
        longitude: Center longitude
        zoom: Zoom level (default: 15)
        size: Image size (default: 600x300)
    """
    try:
        latitude = float(request.args.get('latitude', 0))
        longitude = float(request.args.get('longitude', 0))
        zoom = int(request.args.get('zoom', 15))
        size = request.args.get('size', '600x300')
        
        if latitude == 0 or longitude == 0:
            return jsonify({'success': False, 'error': 'Missing coordinates'}), 400
        
        url = google_maps_service.get_static_map_url(
            latitude=latitude,
            longitude=longitude,
            zoom=zoom,
            size=size
        )
        
        if url:
            return redirect(url)
        else:
            return jsonify({'success': False, 'error': 'Google Maps not configured'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@maps_bp.route('/embed', methods=['GET'])
def get_embed_url():
    """
    Get embed URL for iframe maps
    
    Query Params:
        latitude: Center latitude
        longitude: Center longitude
        zoom: Zoom level (default: 15)
    """
    try:
        latitude = float(request.args.get('latitude', 0))
        longitude = float(request.args.get('longitude', 0))
        zoom = int(request.args.get('zoom', 15))
        
        if latitude == 0 or longitude == 0:
            return jsonify({'success': False, 'error': 'Missing coordinates'}), 400
        
        url = google_maps_service.get_embed_url(
            latitude=latitude,
            longitude=longitude,
            zoom=zoom
        )
        
        if url:
            return jsonify({'success': True, 'url': url})
        else:
            return jsonify({'success': False, 'error': 'Google Maps not configured'}), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
