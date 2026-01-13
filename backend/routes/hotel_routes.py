"""
Coast to Coast Journeys - Hotel Routes
API routes for hotel search and booking
"""
from flask import Blueprint, request, jsonify
from services.etg_service import etg_service
from services.supabase_service import supabase_service
from services.google_maps_service import google_maps_service
import time

hotel_bp = Blueprint('hotels', __name__, url_prefix='/api/hotels')


# ==========================================
# SEARCH ENDPOINTS
# ==========================================

@hotel_bp.route('/search/region', methods=['POST'])
def search_by_region():
    """
    Search hotels by region
    
    Request Body:
    {
        "region_id": 1234,
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2,
        "children_ages": [],
        "currency": "INR"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        required = ['region_id', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Format guests
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', [])
        )
        
        # Call ETG API
        result = etg_service.search_by_region(
            region_id=data['region_id'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'INR'),
            residency=data.get('residency', 'in')
        )
        
        # Save search to history (async, don't wait)
        try:
            supabase_service.save_search_history({
                'search_type': 'region',
                'search_params': data,
                'results_count': len(result.get('data', {}).get('hotels', [])) if result.get('success') else 0
            })
        except:
            pass  # Don't fail if history save fails
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/search/geo', methods=['POST'])
def search_by_geo():
    """
    Search hotels by latitude/longitude
    
    Request Body:
    {
        "latitude": 28.6139,
        "longitude": 77.2090,
        "radius": 5000,
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2,
        "children_ages": []
    }
    """
    try:
        data = request.get_json()
        
        required = ['latitude', 'longitude', 'radius', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', [])
        )
        
        result = etg_service.search_by_geo(
            latitude=data['latitude'],
            longitude=data['longitude'],
            radius=data['radius'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'INR')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/search/hotels', methods=['POST'])
def search_by_hotel_ids():
    """
    Search specific hotels by IDs
    
    Request Body:
    {
        "hotel_ids": ["hotel_id_1", "hotel_id_2"],
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2
    }
    """
    try:
        data = request.get_json()
        
        required = ['hotel_ids', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', [])
        )
        
        result = etg_service.search_by_hotels(
            hotel_ids=data['hotel_ids'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'INR')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/search/destination', methods=['POST'])
def search_by_destination():
    """
    Search hotels by destination name (uses geocoding)
    Converts destination to coordinates and searches nearby
    
    Request Body:
    {
        "destination": "Goa, India",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2,
        "radius": 10000
    }
    """
    try:
        data = request.get_json()
        
        required = ['destination', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Geocode destination
        geo_result = google_maps_service.geocode(data['destination'])
        
        if not geo_result.get('success'):
            return jsonify({
                'success': False,
                'error': f"Could not find location: {data['destination']}"
            }), 400
        
        coords = geo_result['data']
        
        # Search hotels by geo
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', [])
        )
        
        result = etg_service.search_by_geo(
            latitude=coords['latitude'],
            longitude=coords['longitude'],
            radius=data.get('radius', 10000),
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'INR')
        )
        
        # Attach location info to result
        if result.get('success'):
            result['location'] = coords
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# HOTEL DETAILS ENDPOINT
# ==========================================

@hotel_bp.route('/details', methods=['POST'])
def get_hotel_details():
    """
    Get detailed hotel information with room rates
    
    Request Body:
    {
        "hotel_id": "hotel_123",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "adults": 2,
        "children_ages": []
    }
    """
    try:
        data = request.get_json()
        
        required = ['hotel_id', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', [])
        )
        
        result = etg_service.get_hotel_page(
            hotel_id=data['hotel_id'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'INR')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/info/<hotel_id>', methods=['GET'])
def get_hotel_info(hotel_id):
    """Get static hotel information"""
    try:
        # Check cache first
        cached = supabase_service.get_cached_hotel(hotel_id)
        if cached.get('success') and cached.get('data'):
            return jsonify({
                'success': True,
                'data': cached['data']['hotel_data'],
                'source': 'cache'
            })
        
        # Fetch from ETG API
        result = etg_service.get_hotel_info(hotel_id)
        
        # Cache if successful
        if result.get('success') and result.get('data'):
            supabase_service.cache_hotel(hotel_id, result['data'])
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# PREBOOK ENDPOINT
# ==========================================

@hotel_bp.route('/prebook', methods=['POST'])
def prebook_rate():
    """
    Prebook a rate - check availability and final price
    
    Request Body:
    {
        "book_hash": "hash_from_hotel_page",
        "price_increase_percent": 5
    }
    """
    try:
        data = request.get_json()
        
        if 'book_hash' not in data:
            return jsonify({'success': False, 'error': 'Missing book_hash'}), 400
        
        result = etg_service.prebook_rate(
            book_hash=data['book_hash'],
            price_increase_percent=data.get('price_increase_percent', 5)
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# BOOKING ENDPOINTS
# ==========================================

@hotel_bp.route('/book', methods=['POST'])
def create_booking():
    """
    Create a new hotel booking
    
    Request Body:
    {
        "book_hash": "hash_from_prebook",
        "guests": [{"first_name": "John", "last_name": "Doe"}],
        "user_id": "optional_user_id",
        "hotel_name": "Hotel Name",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "total_amount": 5000.00
    }
    """
    try:
        data = request.get_json()
        
        required = ['book_hash', 'guests']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        # Generate unique partner order ID
        partner_order_id = etg_service.generate_partner_order_id()
        
        # Get user IP
        user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        
        # Create booking in ETG
        etg_result = etg_service.create_booking(
            book_hash=data['book_hash'],
            partner_order_id=partner_order_id,
            guests=data['guests'],
            user_ip=user_ip
        )
        
        if not etg_result.get('success'):
            return jsonify(etg_result), 400
        
        # Save booking to Supabase
        booking_data = {
            'partner_order_id': partner_order_id,
            'user_id': data.get('user_id'),
            'hotel_id': data.get('hotel_id', ''),
            'hotel_name': data.get('hotel_name', ''),
            'check_in': data.get('checkin'),
            'check_out': data.get('checkout'),
            'rooms': len(data['guests']),
            'guests': data['guests'],
            'total_amount': data.get('total_amount', 0),
            'currency': data.get('currency', 'INR'),
            'status': 'created',
            'booking_response': etg_result.get('data')
        }
        
        db_result = supabase_service.create_booking(booking_data)
        
        return jsonify({
            'success': True,
            'partner_order_id': partner_order_id,
            'etg_response': etg_result.get('data'),
            'booking_id': db_result.get('data', {}).get('id')
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/book/finish', methods=['POST'])
def finish_booking():
    """
    Finalize booking and start status polling
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123"
    }
    """
    try:
        data = request.get_json()
        
        if 'partner_order_id' not in data:
            return jsonify({'success': False, 'error': 'Missing partner_order_id'}), 400
        
        partner_order_id = data['partner_order_id']
        
        # Call finish booking
        result = etg_service.finish_booking(partner_order_id)
        
        if result.get('success'):
            # Update booking status in database
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id,
                {'status': 'processing'}
            )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/book/status', methods=['POST'])
def check_booking_status():
    """
    Check booking status (poll until complete)
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123"
    }
    """
    try:
        data = request.get_json()
        
        if 'partner_order_id' not in data:
            return jsonify({'success': False, 'error': 'Missing partner_order_id'}), 400
        
        partner_order_id = data['partner_order_id']
        
        result = etg_service.check_booking_status(partner_order_id)
        
        # Update status in database based on response
        if result.get('success') and result.get('data'):
            status = result['data'].get('status', 'unknown')
            update_data = {
                'status': 'confirmed' if status == 'ok' else status,
                'booking_response': result['data']
            }
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id,
                update_data
            )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/book/poll', methods=['POST'])
def poll_booking_status():
    """
    Poll booking status until final (with timeout)
    Polls every 2.5 seconds for max 60 seconds
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123"
    }
    """
    try:
        data = request.get_json()
        
        if 'partner_order_id' not in data:
            return jsonify({'success': False, 'error': 'Missing partner_order_id'}), 400
        
        partner_order_id = data['partner_order_id']
        max_attempts = 24  # 60 seconds / 2.5 seconds
        attempt = 0
        
        while attempt < max_attempts:
            result = etg_service.check_booking_status(partner_order_id)
            
            if result.get('success') and result.get('data'):
                status = result['data'].get('status', '')
                
                if status != 'processing':
                    # Final status reached
                    final_status = 'confirmed' if status == 'ok' else status
                    supabase_service.update_booking_by_partner_order_id(
                        partner_order_id,
                        {'status': final_status, 'booking_response': result['data']}
                    )
                    return jsonify({
                        'success': True,
                        'status': final_status,
                        'data': result['data']
                    })
            
            attempt += 1
            time.sleep(2.5)
        
        return jsonify({
            'success': False,
            'error': 'Booking status check timed out',
            'status': 'timeout'
        }), 408
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# POST-BOOKING ENDPOINTS
# ==========================================

@hotel_bp.route('/booking/<partner_order_id>', methods=['GET'])
def get_booking(partner_order_id):
    """Get booking details from ETG"""
    try:
        result = etg_service.get_booking_info(partner_order_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/booking/cancel', methods=['POST'])
def cancel_booking():
    """
    Cancel a booking
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123"
    }
    """
    try:
        data = request.get_json()
        
        if 'partner_order_id' not in data:
            return jsonify({'success': False, 'error': 'Missing partner_order_id'}), 400
        
        partner_order_id = data['partner_order_id']
        
        # Cancel in ETG
        result = etg_service.cancel_booking(partner_order_id)
        
        if result.get('success'):
            # Update status in database
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id,
                {'status': 'cancelled'}
            )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# USER BOOKINGS
# ==========================================

@hotel_bp.route('/user/<user_id>/bookings', methods=['GET'])
def get_user_bookings(user_id):
    """Get all bookings for a user"""
    try:
        result = supabase_service.get_user_bookings(user_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
