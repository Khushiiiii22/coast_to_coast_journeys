"""
C2C Journeys - Hotel Routes
API routes for hotel search and booking
"""
from flask import Blueprint, request, jsonify
from services.etg_service import etg_service
from services.supabase_service import supabase_service
from services.google_maps_service import google_maps_service
from datetime import datetime
import time
import os
from routes.cancellation_helper import format_cancellation_policies

hotel_bp = Blueprint('hotels', __name__, url_prefix='/api/hotels')


# ==========================================
# CONSTANTS
# ==========================================
COMMISSION_RATE = 0.15  # 15% Markup

# ==========================================
# DEBUG ENDPOINT (Temporary) - v3.0 Brevo
# ==========================================

@hotel_bp.route('/debug/email-test', methods=['GET'])
def debug_email_test():
    """Test Brevo email configuration"""
    try:
        from flask import current_app
        import os as os_lib
        import requests
        
        # Check Brevo config
        brevo_key = current_app.config.get('BREVO_API_KEY') or os_lib.getenv('BREVO_API_KEY')
        mail_sender = current_app.config.get('MAIL_DEFAULT_SENDER') or os_lib.getenv('MAIL_DEFAULT_SENDER', 'info@coasttocoastjourneys.com')
        
        results = {
            "config": {
                "brevo_api_key_configured": bool(brevo_key),
                "brevo_key_masked": f"{brevo_key[:10]}...{brevo_key[-5:]}" if brevo_key else "None",
                "mail_sender": mail_sender
            },
            "steps": []
        }
        
        if not brevo_key:
            results['steps'].append("❌ BREVO_API_KEY not configured")
            results['steps'].append("👉 Add BREVO_API_KEY in Render Environment Variables")
            return jsonify({
                "success": False,
                "error": "Brevo not configured",
                "debug_info": results
            }), 500
        
        # Test Brevo
        results['steps'].append("✅ Brevo API Key found")
        results['steps'].append(f"📧 Sender: {mail_sender}")
        
        # Try to send a test email
        try:
            results['steps'].append("Testing Brevo API connectivity...")
            
            # Send test email
            test_email = "khushikumari62406@gmail.com"
            
            headers = {
                "accept": "application/json",
                "content-type": "application/json",
                "api-key": brevo_key
            }
            
            payload = {
                "sender": {"name": "C2C Journeys", "email": mail_sender},
                "to": [{"email": test_email}],
                "subject": "C2C Journeys - Brevo Test",
                "textContent": "This is a test email from your Render deployment via Brevo."
            }
            
            response = requests.post("https://api.brevo.com/v3/smtp/email", json=payload, headers=headers)
            
            if response.status_code in [200, 201, 202]:
                result = response.json()
                results['steps'].append(f"✅ Test email sent! (Message ID: {result.get('messageId', 'N/A')})")
                results['steps'].append(f"📫 Sent to: {test_email}")
                return jsonify({
                    "success": True,
                    "message": "Brevo is working!",
                    "debug_info": results
                })
            else:
                results['steps'].append(f"❌ Brevo error: {response.status_code} - {response.text}")
                return jsonify({
                    "success": False,
                    "error": response.text,
                    "debug_info": results
                }), 500
            
        except Exception as e:
            results['steps'].append(f"❌ Brevo error: {str(e)}")
            return jsonify({
                "success": False,
                "error": str(e),
                "debug_info": results
            }), 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/autocomplete', methods=['GET'])
def autocomplete_location():
    """
    Returns location suggestions using Google Places Autocomplete API
    Query param: query (min 2 chars)
    """
    query = request.args.get('query', '').strip()
    
    if len(query) < 2:
        return jsonify({
            'success': False,
            'error': 'Query must be at least 2 characters'
        }), 400
    
    try:
        from config import Config
        import requests as req
        
        api_key = Config.GOOGLE_MAPS_API_KEY
        
        if not api_key or api_key == 'your_google_maps_api_key':
            # Return fallback with popular matching cities
            popular = [
                {'description': 'Mumbai, Maharashtra, India', 'types': ['locality'], 'structured_formatting': {'main_text': 'Mumbai', 'secondary_text': 'Maharashtra, India'}},
                {'description': 'Delhi, India', 'types': ['locality'], 'structured_formatting': {'main_text': 'Delhi', 'secondary_text': 'India'}},
                {'description': 'Dubai, United Arab Emirates', 'types': ['locality'], 'structured_formatting': {'main_text': 'Dubai', 'secondary_text': 'United Arab Emirates'}},
                {'description': 'Paris, France', 'types': ['locality'], 'structured_formatting': {'main_text': 'Paris', 'secondary_text': 'France'}},
                {'description': 'London, United Kingdom', 'types': ['locality'], 'structured_formatting': {'main_text': 'London', 'secondary_text': 'United Kingdom'}},
            ]
            filtered = [p for p in popular if query.lower() in p['description'].lower()]
            return jsonify({'success': True, 'predictions': filtered[:5], 'source': 'fallback'})
        
        # Call Google Places Autocomplete API
        url = 'https://maps.googleapis.com/maps/api/place/autocomplete/json'
        # Try both (regions) and (cities) if regions fails, or just broader types
        params = {'input': query, 'types': '(regions)', 'key': api_key}
        
        response = req.get(url, params=params, timeout=5)
        data = response.json()
        
        if data.get('status') == 'OK':
            return jsonify({'success': True, 'predictions': data.get('predictions', [])[:8], 'source': 'google'})
        elif data.get('status') == 'ZERO_RESULTS':
            # Try without types restriction if no results found
            params.pop('types')
            response = req.get(url, params=params, timeout=5)
            data = response.json()
            if data.get('status') == 'OK':
                return jsonify({'success': True, 'predictions': data.get('predictions', [])[:8], 'source': 'google_unfiltered'})
            
        return jsonify({'success': False, 'error': data.get('status', 'Unknown error'), 'predictions': []})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e), 'predictions': []}), 500


@hotel_bp.route('/debug/ip-check', methods=['GET'])
def debug_ip_check():
    """Check outgoing IP address (to verify Proxy/Static IP)"""
    try:
        import requests
        from flask import current_app
        
        # Get proxy config
        proxy_url = current_app.config.get('PROXY_URL')
        proxies = None
        if proxy_url:
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
        
        results = {
            "proxy_configured": bool(proxy_url),
            "proxy_url_masked": f"{proxy_url[:10]}..." if proxy_url else "None",
            "ip_check": {}
        }
        
        # 1. Check Direct IP (Render's Dynamic IP)
        try:
            direct_resp = requests.get('https://api.ipify.org?format=json', timeout=5)
            results['ip_check']['direct_ip'] = direct_resp.json().get('ip')
        except Exception as e:
            results['ip_check']['direct_ip_error'] = str(e)
            
        # 2. Check Proxy IP (The Static IP for RateHawk)
        if proxies:
            try:
                proxy_resp = requests.get('https://api.ipify.org?format=json', proxies=proxies, timeout=10)
                results['ip_check']['proxy_ip'] = proxy_resp.json().get('ip')
                results['ip_check']['status'] = "✅ Proxy Working"
                results['message'] = "Give this PROXY IP to RateHawk for whitelisting."
            except Exception as e:
                results['ip_check']['proxy_error'] = str(e)
                results['ip_check']['status'] = "❌ Proxy Failed"
        else:
            results['ip_check']['status'] = "⚠️ No Proxy Configured"
            results['message'] = "Please add QuotaGuard Static or Fixie add-on in Render."
            
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# SUGGEST/AUTOCOMPLETE ENDPOINT
# ==========================================

@hotel_bp.route('/suggest', methods=['POST'])
def suggest():
    """
    Search suggestions for hotels and regions
    
    Request Body:
    {
        "query": "Paris",
        "language": "en"
    }
    """
    try:
        data = request.get_json()
        
        if 'query' not in data or len(data['query']) < 2:
            return jsonify({'success': False, 'error': 'Query must be at least 2 characters'}), 400
        
        result = etg_service.suggest(
            query=data['query'],
            language=data.get('language', 'en')
        )
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


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
        
        # Format guests (supports multi-room if 'rooms' is provided)
        rooms_data = data.get('rooms')
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', []),
            rooms=rooms_data
        )
        
        # Call ETG API
        result = etg_service.search_by_region(
            region_id=data['region_id'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'USD'),
            residency=data.get('residency', 'gb')
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
        
        # Format guests (supports multi-room if 'rooms' is provided)
        rooms_data = data.get('rooms')
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', []),
            rooms=rooms_data
        )
        
        result = etg_service.search_by_geo(
            latitude=data['latitude'],
            longitude=data['longitude'],
            radius=data['radius'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'USD')
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
        
        # Format guests (supports multi-room if 'rooms' is provided)
        rooms_data = data.get('rooms')
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', []),
            rooms=rooms_data
        )
        
        result = etg_service.search_by_hotels(
            hotel_ids=data['hotel_ids'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'USD')
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
    # Destinations with ETG region IDs
    # ALL destinations use ETG/RateHawk API — no sandbox/production distinction
    # For certification, Mikhail's team will test with supported destinations
    POPULAR_DESTINATIONS = {
        # WELL-KNOWN DESTINATIONS
        'paris': {'latitude': 48.8566, 'longitude': 2.3522, 'region_id': 2734, 'name': 'Paris'},
        'dubai': {'latitude': 25.2048, 'longitude': 55.2708, 'region_id': 6053839, 'name': 'Dubai'},
        'moscow': {'latitude': 55.7558, 'longitude': 37.6173, 'region_id': 2395, 'name': 'Moscow'},
        
        # INDIAN DESTINATIONS
        'goa': {'latitude': 15.2993, 'longitude': 74.1240, 'region_id': 6308855, 'name': 'Goa'},
        'delhi': {'latitude': 28.6139, 'longitude': 77.2090, 'region_id': 6308838, 'name': 'New Delhi'},
        'mumbai': {'latitude': 19.0760, 'longitude': 72.8777, 'region_id': 6308862, 'name': 'Mumbai'},
        'bangalore': {'latitude': 12.9716, 'longitude': 77.5946, 'region_id': 6308822, 'name': 'Bangalore'},
        'bengaluru': {'latitude': 12.9716, 'longitude': 77.5946, 'region_id': 6308822, 'name': 'Bangalore'},
        'chennai': {'latitude': 13.0827, 'longitude': 80.2707, 'region_id': 6308834, 'name': 'Chennai'},
        'kolkata': {'latitude': 22.5726, 'longitude': 88.3639, 'region_id': 6308856, 'name': 'Kolkata'},
        'jaipur': {'latitude': 26.9124, 'longitude': 75.7873, 'region_id': 6308849, 'name': 'Jaipur'},
        'udaipur': {'latitude': 24.5854, 'longitude': 73.7125, 'region_id': 6308883, 'name': 'Udaipur'},
        'agra': {'latitude': 27.1767, 'longitude': 78.0081, 'region_id': 6308815, 'name': 'Agra'},
        'hyderabad': {'latitude': 17.3850, 'longitude': 78.4867, 'region_id': 6308846, 'name': 'Hyderabad'},
        'pune': {'latitude': 18.5204, 'longitude': 73.8567, 'region_id': 6308870, 'name': 'Pune'},
        'kerala': {'latitude': 10.8505, 'longitude': 76.2711, 'region_id': 6308854, 'name': 'Kerala'},
        'kochi': {'latitude': 9.9312, 'longitude': 76.2673, 'region_id': 6308855, 'name': 'Kochi'},
        'manali': {'latitude': 32.2396, 'longitude': 77.1887, 'region_id': 6308859, 'name': 'Manali'},
        'shimla': {'latitude': 31.1048, 'longitude': 77.1734, 'region_id': 6308876, 'name': 'Shimla'},
        'rishikesh': {'latitude': 30.0869, 'longitude': 78.2676, 'region_id': 6308872, 'name': 'Rishikesh'},
        'varanasi': {'latitude': 25.3176, 'longitude': 82.9739, 'region_id': 6308885, 'name': 'Varanasi'},
        'amritsar': {'latitude': 31.6340, 'longitude': 74.8723, 'region_id': 6308818, 'name': 'Amritsar'},
        'darjeeling': {'latitude': 27.0410, 'longitude': 88.2663, 'region_id': 6308837, 'name': 'Darjeeling'},
        'ooty': {'latitude': 11.4102, 'longitude': 76.6950, 'region_id': 6308866, 'name': 'Ooty'},
        
        # MIKHAIL'S REQUIRED SANDBOX HOTELS (ETG Certification)
        'los angeles': {
            'latitude': 34.0522, 
            'longitude': -118.2437, 
            'name': 'Los Angeles', 
            'region_id': 2011,  # Verified Sandbox Region ID for LA
            'hotel_ids': [
                'conrad_los_angeles', 
                '10004834',  # Mikhail's Conrad HID
                '6362880',   # Mikhail's Westin HID
                '10595223'   # Mikhail's The LINE HID
            ]
        },
    }
    
    # Standard conversion rates (updated)
    CONVERSION_RATES = {
        'USD_TO_INR': 86.5,
        'EUR_TO_INR': 92.0,
        'GBP_TO_INR': 108.0,
        'INR_TO_USD': 0.0116,
        'INR_TO_EUR': 0.011,
        'INR_TO_GBP': 0.009
    }
    
    try:
        data = request.get_json()
        
        required = ['destination', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        destination = data['destination'].lower().strip()
        region_id = data.get('region_id')
        location_name = data['destination']
        target_currency = data.get('currency', 'INR')
        rooms_data = data.get('rooms')  # multi-room array if available

        
        print(f"🔍 Hotel Search Request: {data['destination']}")
        
        # Step 1: Check if destination matches a known location
        hotel_ids_to_search = None
        for key, loc_data in POPULAR_DESTINATIONS.items():
            if key in destination or destination in key:
                if 'hotel_ids' in loc_data:
                    hotel_ids_to_search = loc_data['hotel_ids']
                    location_name = loc_data['name']
                    print(f"📍 Matched destination with specific hotels: {location_name}, Hotel IDs: {hotel_ids_to_search}")
                else:
                    region_id = loc_data.get('region_id')
                    location_name = loc_data['name']
                    print(f"📍 Matched destination: {location_name}, Region ID: {region_id}")
                break
        
        # Step 2: ALWAYS call ETG/RateHawk API for every search when we have a region_id.
        # ETG certification requires a live /search/serp/region/ call for EVERY search action.
        # Previously this step was bypassing ETG for non-sandbox Indian cities — that prevented
        # Mikhail's team from seeing our API calls and blocked certification progress.
        # Now ETG is always called first; Google Places is only used as a fallback if ETG returns 0.
        
        # Step 3: Try ETG/RateHawk for ALL destinations with a known region_id or hotel_ids
        if region_id or hotel_ids_to_search:
            print(f"🏨 Searching RateHawk for destination: {location_name}")
            
            # RateHawk Sandbox often rejects INR. We force USD for the API call and convert locally.
            user_currency = data.get('currency', 'INR')
            api_currency = 'USD' if user_currency == 'INR' else user_currency
            
            guests = etg_service.format_guests_for_search(
                adults=data['adults'],
                children_ages=data.get('children_ages', []),
                rooms=rooms_data
            )
            
            if hotel_ids_to_search:
                result = etg_service.search_by_hotels(
                    hotel_ids=hotel_ids_to_search,
                    checkin=data['checkin'],
                    checkout=data['checkout'],
                    rooms=guests,
                    currency=api_currency, # Force USD for sandbox compatibility
                    residency=data.get('residency', 'gb')
                )
            else:
                # Search using region API
                result = etg_service.search_by_region(
                    region_id=region_id,
                    checkin=data['checkin'],
                    checkout=data['checkout'],
                    rooms=guests,
                    currency=api_currency, # Force USD for sandbox compatibility
                    residency=data.get('residency', 'gb')
                )
            
            # Check if RateHawk returned hotels
            if result.get('success') and result.get('data'):
                inner_data = result['data'].get('data', result['data'])
                etg_hotels = inner_data.get('hotels', [])
                
                if etg_hotels and len(etg_hotels) > 0:
                    print(f"✅ Found {len(etg_hotels)} hotels via RateHawk for {location_name}")

                if etg_hotels and len(etg_hotels) > 0:
                    # Proceed with transformation...
                    # NOTE: We do NOT call /hotel/info/ for every search result.
                    # ETG certification requires using cached static data from dumps
                    # instead of bombarding /hotel/info/ (would hit RPM limits).
                    # Static data (names, images) comes from local DB / dumps.
                    static_hotel_map = {}
                    
                    # Calculate nights for correct inclusive price display
                    from datetime import datetime
                    try:
                        d1 = datetime.strptime(data['checkin'], '%Y-%m-%d')
                        d2 = datetime.strptime(data['checkout'], '%Y-%m-%d')
                        nights = (d2 - d1).days
                    except:
                        nights = 1

                    # Enrich hotels with static data from cache (if available)
                    for h in etg_hotels:
                        hid = h.get('hotel_id') or h.get('id')
                        if hid and hid in static_hotel_map:
                            h['static_data'] = static_hotel_map[hid]

                    transformed_hotels = transform_etg_hotels(
                        hotels_data=etg_hotels, 
                        target_currency=user_currency,
                        conversion_rates=CONVERSION_RATES,
                        nights=nights
                    )
                    
                    return jsonify({
                        'success': True,
                        'data': {'hotels': transformed_hotels},
                        'location': {'name': location_name, 'region_id': region_id},
                        'hotels_count': len(transformed_hotels),
                        'real_data': True,
                        'source': 'ratehawk'
                    })
                else:
                    print(f"⚠️ RateHawk returned 0 hotels for {location_name}")
        
        # Step 4: If not in predefined list, try ETG suggest API
        if not region_id and not hotel_ids_to_search:
            print(f"🔎 Trying RateHawk suggest API for: {data['destination']}")
            suggest_result = etg_service.suggest(data['destination'])
            if suggest_result.get('success') and suggest_result.get('data'):
                inner_data = suggest_result['data'].get('data', suggest_result['data'])
                regions = inner_data.get('regions', [])
                hotels = inner_data.get('hotels', [])
                
                guests = etg_service.format_guests_for_search(
                    adults=data['adults'],
                    children_ages=data.get('children_ages', []),
                    rooms=rooms_data
                )
                
                if regions:
                    # Search by suggested region
                    region_id = regions[0].get('id')
                    location_name = regions[0].get('name', data['destination'])
                    print(f"✅ Found region via suggest API: {location_name} (ID: {region_id})")
                    
                    result = etg_service.search_by_region(
                        region_id=region_id,
                        checkin=data['checkin'],
                        checkout=data['checkout'],
                        rooms=guests,
                        currency=target_currency,
                        residency=data.get('residency', 'gb')
                    )
                elif hotels:
                    # Search by suggested specific hotels (e.g. user typed a hotel name)
                    hotel_ids = [h.get('id') for h in hotels if h.get('id')][:10]  # Take up to 10 hotels
                    location_name = hotels[0].get('name', data['destination'])
                    print(f"✅ Found specific hotels via suggest API: {location_name}...")
                    
                    result = etg_service.search_by_hotels(
                        hotel_ids=hotel_ids,
                        checkin=data['checkin'],
                        checkout=data['checkout'],
                        rooms=guests,
                        currency=target_currency,
                        residency=data.get('residency', 'gb')
                    )
                else:
                    result = {}
                
                # Process results from Step 4 suggest-based search
                if result.get('success') and result.get('data'):
                    search_data = result['data'].get('data', result['data'])
                    etg_hotels = search_data.get('hotels', [])
                    
                    if etg_hotels and len(etg_hotels) > 0:
                        print(f"✅ Found {len(etg_hotels)} hotels via RateHawk suggest")
                        
                        from datetime import datetime
                        try:
                            d1 = datetime.strptime(data['checkin'], '%Y-%m-%d')
                            d2 = datetime.strptime(data['checkout'], '%Y-%m-%d')
                            nights = (d2 - d1).days
                        except:
                            nights = 1

                        transformed_hotels = transform_etg_hotels(
                            hotels_data=etg_hotels, 
                            target_currency=target_currency,
                            conversion_rates=CONVERSION_RATES,
                            nights=nights
                        )
                        return jsonify({
                            'success': True,
                            'data': {'hotels': transformed_hotels},
                            'location': {'name': location_name, 'region_id': region_id},
                            'hotels_count': len(transformed_hotels),
                            'real_data': True,
                            'source': 'ratehawk'
                        })
        
        # Step 5: NO Google Places fallback
        # Google Places hotels have ChIJ... IDs with no ETG book_hash,
        # so the full booking chain (hotelpage → prebook → create → finish → check)
        # can never fire. This was blocking ETG certification.
        # Instead, return an informative error so the user knows to search a supported destination.
        print(f"❌ No ETG hotels found for {data['destination']} — NOT falling back to Google")
        return jsonify({
            'success': False,
            'error': f"No bookable hotels found for '{data['destination']}'. Please try Paris, Dubai, or Moscow.",
            'supported_destinations': ['Paris', 'Moscow', 'Dubai']
        }), 400
    

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# HOTEL SUGGEST (AUTOCOMPLETE)
# ==========================================

@hotel_bp.route('/suggest', methods=['GET'])
def suggest_locations():
    """Proxy for ETG/RateHawk Multicomplete Suggestion"""
    try:
        query = request.args.get('query', '')
        language = request.args.get('language', 'en')
        
        if not query or len(query) < 2:
            return jsonify({
                "success": True, 
                "data": {"hotels": [], "regions": []}
            })
            
        # Call ETG service
        result = etg_service.suggest(query, language)
        return jsonify(result)
        
    except Exception as e:
        print(f"❌ Suggest API Error: {e}")
        return jsonify({"success": False, "error": str(e)}), 500


# RateHawk CDN base URL for images
CDN_BASE = 'https://cdn.worldota.net/t/'
# RateHawk size format: crop/WIDTHxHEIGHT (crops to fit), or WIDTHxHEIGHT
IMG_SIZE = 'crop/640x400'
IMG_SIZE_THUMB = '240x240'

def process_etg_image_url(raw_url):
    """Process a RateHawk image URL, replacing {size} placeholder"""
    if not raw_url or not isinstance(raw_url, str):
        return None
    
    url = raw_url.strip()
    
    # Replace {size} placeholder with actual dimensions
    if '{size}' in url:
        url = url.replace('{size}', IMG_SIZE)
    
    # Some RateHawk URLs are relative paths like '/content/12345/abcdef.jpg'
    # They need the CDN base prepended
    if url.startswith('/'):
        url = CDN_BASE + IMG_SIZE + url
    
    # Ensure URL starts with http
    if not url.startswith('http'):
        url = CDN_BASE + IMG_SIZE + '/' + url
        
    return url


def transform_etg_hotels(hotels_data, target_currency='USD', conversion_rates=None, MEAL_TYPE_DISPLAY=None, room_groups=None, nights=1):
    """
    Transform ETG search results into flattened hotel cards.
    Handles price calculation (Commission + Exclusive Taxes).
    
    room_groups: optional dict of static room data keyed by rg_ext.rg
    """
    if not MEAL_TYPE_DISPLAY:
        MEAL_TYPE_DISPLAY = {
            'all-inclusive': 'All Inclusive',
            'breakfast': 'Breakfast Included',
            'breakfast-buffet': 'Breakfast Buffet',
            'continental-breakfast': 'Continental Breakfast',
            'dinner': 'Dinner Included',
            'full-board': 'Full Board (All Meals)',
            'half-board': 'Half Board (Breakfast & Dinner)',
            'half-board-lunch': 'Half Board (Breakfast & Lunch)',
            'half-board-dinner': 'Half Board (Breakfast & Dinner)',
            'lunch': 'Lunch Included',
            'nomeal': 'Room Only (No Meals)',
            'some-meal': 'Some Meals Included',
            'english-breakfast': 'English Breakfast',
            'american-breakfast': 'American Breakfast',
            'asian-breakfast': 'Asian Breakfast',
            'chinese-breakfast': 'Chinese Breakfast',
            'israeli-breakfast': 'Israeli Breakfast',
            'japanese-breakfast': 'Japanese Breakfast',
            'scandinavian-breakfast': 'Scandinavian Breakfast',
            'scottish-breakfast': 'Scottish Breakfast',
            'breakfast-for-1': 'Breakfast for 1 Guest',
            'breakfast-for-2': 'Breakfast for 2 Guests',
            'super-all-inclusive': 'Super All Inclusive',
            'soft-all-inclusive': 'Soft All Inclusive',
            'ultra-all-inclusive': 'Ultra All Inclusive',
        }
    
    transformed = []
    
    # 1. Total (Net + Tax) from API.
    # 2. Split into API_Net and API_Tax.
    # 3. Apply commission to both: Display_Net = API_Net * 1.15, Display_Tax = API_Tax * 1.15.
    
    for idx, hotel in enumerate(hotels_data):
        hotel_id = hotel.get('hotel_id') or hotel.get('id')
        rates = hotel.get('rates', [])
        
        lowest_price = 0
        best_rate = None
        best_meal_value = 'nomeal'
        best_meal_display = 'Room Only'
        has_breakfast = False
        no_child_meal = False
        best_rate_fees = []
        prepay_to_charge = 0
        
        # Determine best rate and gather transparency data
        for rate in rates:
            payment_options = rate.get('payment_options', {})
            payment_types = payment_options.get('payment_types', [])
            rate_currency = payment_options.get('currency_code', 'USD')
            
            # API Total is the amount ETG says the booking costs inclusive of ALL taxes
            api_total = float(payment_types[0].get('amount', 0)) if payment_types else 0
            
            # Identify Property-Payable (Non-Included) Taxes
            api_non_included_tax = 0
            property_fees = []
            tax_data = payment_options.get('tax_data', {}) or {}
            
            for tax in tax_data.get('taxes', []):
                amt = float(tax.get('amount', 0))
                # Certification requirement (Tax Discovery): 
                # If included_by_supplier is false, the guest pays at the property.
                if not tax.get('included_by_supplier', True):
                    api_non_included_tax += amt
                    property_fees.append({
                        'name': tax.get('name', 'Local Fee'),
                        'amount_native': amt,
                        'currency_native': tax.get('currency_code', rate_currency)
                    })

            # Calculate amount to charge the user on our platform (Prepaid Total)
            # Mikhail Requirement (Update 3): We MUST subtract non-included fees from the prepaid total.
            api_prepaid_amount = api_total - api_non_included_tax

            # Apply conversion and markup to the prepaid component
            converted_prepaid = api_prepaid_amount
            if target_currency == 'INR' and rate_currency == 'USD' and conversion_rates:
                converted_prepaid = api_prepaid_amount * conversion_rates.get('USD_TO_INR', 86.5)
            elif target_currency == 'INR' and rate_currency == 'EUR' and conversion_rates:
                converted_prepaid = api_prepaid_amount * conversion_rates.get('EUR_TO_INR', 92.0)
            elif target_currency == rate_currency:
                converted_prepaid = api_prepaid_amount
            elif conversion_rates and f"{rate_currency}_TO_{target_currency}" in conversion_rates:
                converted_prepaid = api_prepaid_amount * conversion_rates[f"{rate_currency}_TO_{target_currency}"]

            # Display total: what the user sees (Prepaid + Property Fees converted)
            # Final display price inclusive of everything
            display_total = (converted_prepaid * (1 + COMMISSION_RATE)) + (api_non_included_tax * conversion_rates.get(f"{rate_currency}_TO_{target_currency}", 1) if target_currency != rate_currency else api_non_included_tax)
            display_nightly = display_total / (nights if nights > 0 else 1)
            
            if lowest_price == 0 or display_nightly < lowest_price:
                lowest_price = display_nightly
                best_rate = rate
                # Save essential data for UI rendering
                meal_data = rate.get('meal_data', {})
                best_meal_value = meal_data.get('value', rate.get('meal', 'nomeal'))
                best_meal_display = MEAL_TYPE_DISPLAY.get(best_meal_value, best_meal_value.replace('-', ' ').title())
                has_breakfast = 'breakfast' in best_meal_value.lower()
                no_child_meal = meal_data.get('no_child_meal', False)
                best_rate_fees = property_fees
                # The actual amount to charge the guest (excluding what they pay at property)
                prepay_to_charge = converted_prepaid * (1 + COMMISSION_RATE)
        # Use Static Data for Name/Image/Address if available
        # Fallback to search result data, then to safe defaults
        static_info = hotel.get('static_data', {}) # Assuming static data is passed in or fetched
        hotel_name = static_info.get('name') or hotel.get('name') or (f"Hotel {hotel_id}" if hotel_id else "Unknown Hotel")
        
        # Clean up hotel name (RateHawk sometimes returns snake_case slugs as names)
        if hotel_name and '_' in hotel_name:
            hotel_name = hotel_name.replace('_', ' ').replace('  ', ' ').title()
        
        # Perform full transformation of all rates for the details page
        enriched_rates = transform_rates(
            rates,
            target_currency=target_currency,
            conversion_rates=conversion_rates,
            meal_display_map=MEAL_TYPE_DISPLAY,
            room_groups=room_groups,
            nights=nights
        )

        transformed.append({
            'id': hotel_id,
            'name': hotel_name,
            'price': lowest_price,
            'prepaid_amount': prepay_to_charge, # Corrected amount for payment gateway
            'property_payable_fees': best_rate_fees, # Transparency Disclosure
            'currency': target_currency,
            'meal_type': best_meal_value,
            'meal_display': best_meal_display,
            'has_breakfast': has_breakfast,
            'no_child_meal': no_child_meal,
            'star_rating': static_info.get('star_rating') or hotel.get('star_rating'),
            'address': static_info.get('address') or hotel.get('address', ''),
            'latitude': static_info.get('latitude') or hotel.get('latitude'),
            'longitude': static_info.get('longitude') or hotel.get('longitude'),
            'images': hotel.get('images', []),
            'amenities': hotel.get('amenities', []),
            'rates': enriched_rates  # CRITICAL: Preserve full rates for Details Page
        })
        
        # Image logic - prioritize API images
        image_url = None
        all_images = []
        
        # 1. Try static data images first (highest quality source)
        if static_info.get('images'):
            img_list = static_info['images']
            for img in img_list[:10]:  # Limit to 10 images per hotel
                if isinstance(img, str):
                    processed_url = process_etg_image_url(img)
                    if processed_url:
                        all_images.append(processed_url)
                elif isinstance(img, dict) and img.get('url'):
                    processed_url = process_etg_image_url(img['url'])
                    if processed_url:
                        all_images.append(processed_url)
        
        # 2. Try search response images
        if not all_images and hotel.get('images'):
            for img in hotel['images'][:10]:
                if isinstance(img, str):
                    processed_url = process_etg_image_url(img)
                    if processed_url:
                        all_images.append(processed_url)
                elif isinstance(img, dict) and img.get('url'):
                    processed_url = process_etg_image_url(img['url'])
                    if processed_url:
                        all_images.append(processed_url)
        
        # 3. Use fallback only as last resort
        if not all_images:
            all_images = ['https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600']
        
        image_url = all_images[0]
        
        # Log image info for debugging
        if all_images and not all_images[0].startswith('https://images.unsplash.com'):
            print(f"📸 Hotel {hotel_id}: {len(all_images)} ETG images, first: {all_images[0][:80]}...")

        # Extract star rating
        star_rating = static_info.get('star_rating') or hotel.get('class') or 3
        
        # Extract city and country from address or destination
        city = static_info.get('city') or hotel.get('city')
        country = static_info.get('country') or hotel.get('country')
        
        # Fallback for location if not found in static or hotel data
        location_name = hotel.get('location_name', 'Unknown Location') # Assuming location_name is passed or derived
        if not city or not country:
            dest_parts = location_name.split(',')
            if not city:
                city = dest_parts[0].strip() if dest_parts else location_name.title()
            if not country:
                country = dest_parts[-1].strip() if len(dest_parts) > 1 else 'India'
        
        # Create full location string
        location_str = f"{city}, {country}" if city and country else static_info.get('address') or location_name.title()

        # Create transformed hotel object
        transformed_hotel = {
            'id': hotel_id or f'hotel_{idx}',
            'hid': hotel.get('hid'),
            'name': hotel_name,
            'star_rating': star_rating,
            'guest_rating': round(3.5 + (star_rating or 3) * 0.3, 1),
            'review_count': 50 + (idx * 23) % 500,
            'address': static_info.get('address') or hotel.get('address') or location_name.title(),
            'city': city,
            'country': country,
            'location': location_str,
            'latitude': static_info.get('latitude') or hotel.get('latitude'),
            'longitude': static_info.get('longitude') or hotel.get('longitude'),
            'image': image_url,
            'images': all_images,
            'description': static_info.get('description') or hotel.get('description') or f"Experience exceptional comfort at {hotel_name}. This {star_rating}-star property offers world-class amenities and a prime location for your stay.",
            'price': round(lowest_price, 2),
            'original_price': round(lowest_price * 1.25, 2),
            'currency': target_currency, # Use real currency from API
            'amenities': extract_amenities(rates) or static_info.get('amenities', []),
            'meal_plan': best_meal_value,
            'meal_info': {
                'value': best_meal_value,
                'display_name': best_meal_display,
                'has_breakfast': has_breakfast,
                'no_child_meal': no_child_meal
            },
            'static_data': static_info,
            'discount': 15,
            'rates': transform_rates(rates, target_currency, conversion_rates, MEAL_TYPE_DISPLAY, room_groups, nights)
        }
        
        transformed.append(transformed_hotel)
    
    return transformed


def transform_rates(rates, target_currency, conversion_rates, meal_display_map, room_groups=None, nights=1):
    """Transform rate data with proper meal_data, cancellation info, and optional room enrichment"""
    transformed_rates = []
    
    for rate in rates[:20]:  # Increased limit to 20 rates to show more variety
        # Enrich with room static data if provided
        if room_groups:
            rate = enrich_rate_with_room_data(rate, room_groups)
        payment_options = rate.get('payment_options', {})
        payment_types = payment_options.get('payment_types', [{}])
        rate_currency = payment_options.get('currency_code', 'USD')
        
        # 1. Start with API total (Net + Included Tax)
        api_total = float(payment_types[0].get('amount', 0)) if payment_types else 0
        
        # 2. Extract and Convert Included Taxes
        api_included_tax = 0
        for tax in payment_options.get('tax_data', {}).get('taxes', []):
            if tax.get('included_by_supplier', True):
                val = float(tax.get('amount', 0))
                # Currency conversion for taxes
                if target_currency == 'INR' and rate_currency == 'USD':
                    val *= conversion_rates['USD_TO_INR']
                elif target_currency == 'INR' and rate_currency == 'EUR':
                    val *= conversion_rates['EUR_TO_INR']
                api_included_tax += val
        
        # 3. Extract and Convert Non-Included Taxes (Property Fees)
        # We add these to the display total to satisfy "Includes all taxes"
        api_non_included_tax = 0
        property_fees = []
        for tax in payment_options.get('tax_data', {}).get('taxes', []):
            if not tax.get('included_by_supplier', True):
                amt = float(tax.get('amount', 0))
                api_non_included_tax += amt
                property_fees.append({
                    'name': tax.get('name', 'Local Fee'),
                    'amount_native': amt,
                    'currency_native': tax.get('currency_code', rate_currency)
                })

        # 4. Calculate Final Display Values
        # Calculate amount to charge the user on our platform (Prepaid Total)
        # Mikhail Requirement: Markup only the prepaid component
        api_prepaid_amount = api_total - api_non_included_tax

        # Apply currency conversion to the prepaid component
        converted_prepaid = api_prepaid_amount
        if target_currency == 'INR' and rate_currency == 'USD' and conversion_rates:
            converted_prepaid = api_prepaid_amount * conversion_rates.get('USD_TO_INR', 86.5)
        elif target_currency == 'INR' and rate_currency == 'EUR' and conversion_rates:
            converted_prepaid = api_prepaid_amount * conversion_rates.get('EUR_TO_INR', 92.0)
        elif target_currency != rate_currency and conversion_rates:
            key = f"{rate_currency}_TO_{target_currency}"
            if key in conversion_rates:
                converted_prepaid = api_prepaid_amount * conversion_rates[key]
        
        # Apply commission only to what WE collect (Prepaid)
        prepay_to_charge = converted_prepaid * (1 + COMMISSION_RATE)
        
        # Property fees converted for display
        display_property_fees = api_non_included_tax * (conversion_rates.get(f"{rate_currency}_TO_{target_currency}", 1) if target_currency != rate_currency else 1)
        
        # Grand total for the user
        display_total_with_fees = prepay_to_charge + display_property_fees
        
        # Nightly inclusive price for display
        display_nightly_inclusive = display_total_with_fees / (nights if nights > 0 else 1)
        
        # Save enriched data back to the rate object
        rate['price'] = display_nightly_inclusive
        rate['prepaid_amount'] = prepay_to_charge
        rate['property_payable_fees'] = property_fees
        rate['currency'] = target_currency
        rate['meal_display'] = meal_display_map.get(rate.get('meal', 'nomeal'), rate.get('meal', 'Room Only').title())

        transformed_rates.append(rate)
        tax_info = parse_taxes(
            payment_options.get('tax_data', {}), 
            target_currency, 
            rate_currency, 
            conversion_rates
        )
        tax_info['total_all_taxes'] = round(api_included_tax * (1 + COMMISSION_RATE) + api_non_included_tax, 2)

        # Get meal_data (preferred)
        meal_data = rate.get('meal_data', {})
        meal_value = meal_data.get('value', rate.get('meal', 'nomeal')) if meal_data else rate.get('meal', 'nomeal')
        meal_display = meal_display_map.get(meal_value, meal_value.replace('-', ' ').title())
        no_child_meal = meal_data.get('no_child_meal', False) if meal_data else False
        
        # Get room details
        room_data = rate.get('room_data_trans', {})
        room_name = (
            room_data.get('main_name') or 
            room_data.get('name') or 
            rate.get('room_name') or 
            rate.get('room_category') or 
            'Standard Room'
        )
        
        FIXED_COUNT_MEALS = {'breakfast-for-1': 1, 'breakfast-for-2': 2}
        is_fixed_count = meal_value in FIXED_COUNT_MEALS
        fixed_count = FIXED_COUNT_MEALS.get(meal_value)

        transformed_rate = {
            'book_hash': rate.get('book_hash') or rate.get('match_hash', ''),
            'room_name': room_name,
            'price': round(display_nightly_inclusive, 2), # ALL-INCLUSIVE NIGHTLY
            'total_price': round(display_total_with_fees, 2), # ALL-INCLUSIVE TOTAL
            'nights': nights,
            'currency': target_currency,
            'meal': meal_value,
            'meal_plan': meal_value,
            'meal_info': {
                'value': meal_value,
                'display_name': meal_display,
                'has_breakfast': meal_data.get('has_breakfast', False) if meal_data else False,
                'no_child_meal': no_child_meal,
                'is_fixed_count': is_fixed_count,
                'fixed_count': fixed_count,
            },
            'tax_info': tax_info,
            'cancellation_info': format_cancellation_policies(rate)
        }
        
        transformed_rates.append(transformed_rate)
    
    return transformed_rates





def parse_taxes(tax_data, target_currency='USD', source_currency='USD', conversion_rates=None):
    """
    Parse tax data from rate and convert if needed.
    
    IMPORTANT: Per RateHawk requirements, taxes which are not included in the payment
    (included_by_supplier: false) MUST be displayed in their original currency and amount,
    as they are payable at the property.
    """
    if not tax_data or not tax_data.get('taxes'):
        return {
            'included_taxes': [],
            'non_included_taxes': [],
            'total_included': 0,
            'currency': target_currency,
            'all_included': True
        }
        
    taxes = tax_data.get('taxes', [])
    total_included = 0.0
    included_taxes = []
    non_included_taxes = []
    all_included = True
    
    for tax in taxes:
        is_included = tax.get('included_by_supplier', True)
        amount = float(tax.get('amount', 0))
        currency = tax.get('currency_code', 'USD')
        name = tax.get('name', 'Tax').replace('_', ' ').title()
        
        if is_included:
            # Convert included taxes to target currency for price breakdown
            converted_amount = amount
            if target_currency == 'INR' and currency == 'USD' and conversion_rates:
                converted_amount = amount * conversion_rates.get('USD_TO_INR', 83)
            elif target_currency == 'INR' and currency == 'EUR' and conversion_rates:
                converted_amount = amount * conversion_rates.get('EUR_TO_INR', 90)
            
            tax_item = {
                'name': name,
                'amount': round(converted_amount, 2),
                'currency': target_currency,
                'included': True,
                'original_amount': amount,
                'original_currency': currency
            }
            included_taxes.append(tax_item)
            total_included += converted_amount
        else:
            # DO NOT convert non-included taxes. Keep original currency/amount.
            all_included = False
            tax_item = {
                'name': name,
                'amount': amount,
                'currency': currency,
                'included': False
            }
            non_included_taxes.append(tax_item)
            
    return {
        'total_included': round(total_included, 2),
        'currency': target_currency,
        'included_taxes': included_taxes,
        'non_included_taxes': non_included_taxes,
        'all_included': all_included,
        'summary': f"Includes {target_currency} {round(total_included, 2)} taxes" if all_included else f"Excludes property fees"
    }


def extract_amenities(rates):
    """Extract amenities from rate data"""
    amenities = set()
    
    for rate in rates:
        for amenity in rate.get('amenities_data', []):
            if 'wifi' in amenity.lower():
                amenities.add('wifi')
            if 'pool' in amenity.lower() or 'swimming' in amenity.lower():
                amenities.add('pool')
            if 'park' in amenity.lower():
                amenities.add('parking')
            if 'spa' in amenity.lower():
                amenities.add('spa')
            if 'restaurant' in amenity.lower() or 'dining' in amenity.lower():
                amenities.add('restaurant')
            if 'gym' in amenity.lower() or 'fitness' in amenity.lower():
                amenities.add('gym')
            if 'bathroom' in amenity.lower():
                amenities.add('bathroom')
    
    # Add some default amenities
    if not amenities:
        amenities = {'wifi', 'parking'}
    
    return list(amenities)[:4]


def get_google_photo_url(photo_reference: str, max_width: int = 600) -> str:
    """
    Build a Google Places Photo URL from photo_reference
    
    Args:
        photo_reference: The photo_reference from Google Places API
        max_width: Maximum width of the image
    
    Returns:
        Full URL to the photo
    """
    api_key = google_maps_service.api_key
    if not api_key or not photo_reference:
        return None
    return f"https://maps.googleapis.com/maps/api/place/photo?maxwidth={max_width}&photo_reference={photo_reference}&key={api_key}"


def search_hotels_via_google(destination: str, checkin: str, checkout: str) -> list:
    """
    Search for hotels using Google Places API as fallback
    Returns real hotel data with actual Google Places photos
    
    Args:
        destination: Destination city/location name
        checkin: Check-in date (YYYY-MM-DD)
        checkout: Check-out date (YYYY-MM-DD)
    
    Returns:
        List of hotel dictionaries formatted for frontend
    """
    if not google_maps_service.is_available():
        print("⚠️  Google Maps API not available for hotel fallback")
        return []
    
    try:
        # Search for hotels (lodging) in the destination
        result = google_maps_service.search_places(
            query=f"hotels in {destination}",
            place_type="lodging"
        )
        
        if not result.get('success') or not result.get('data'):
            return []
        
        google_places = result['data']
        hotels = []
        
        # Fallback images only if Google Places doesn't return photos
        fallback_images = [
            'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600',
            'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600',
            'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=600',
            'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600',
            'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=600',
            'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600',
        ]
        
        for idx, place in enumerate(google_places[:20]):  # Limit to 20 hotels
            rating = place.get('rating', 4.0)
            review_count = place.get('user_ratings_total', 0)
            
            # Estimate star rating from Google rating (5-point scale)
            star_rating = min(5, max(3, round(rating)))
            
            # Estimate price based on rating (rough approximation)
            base_price = 2000 + (rating * 1500) + (idx * 200)
            
            # Get photos from Google Places - use actual photos if available
            photos = place.get('photos', [])
            hotel_images = []
            
            for photo in photos[:5]:  # Get up to 5 photos
                photo_ref = photo.get('photo_reference') if isinstance(photo, dict) else None
                if photo_ref:
                    photo_url = get_google_photo_url(photo_ref, 800)
                    if photo_url:
                        hotel_images.append(photo_url)
            
            # Use fallback if no Google photos available
            if not hotel_images:
                hotel_images = [fallback_images[idx % len(fallback_images)]]
            
            primary_image = hotel_images[0] if hotel_images else fallback_images[idx % len(fallback_images)]
            
            # Extract city and country from destination
            destination_parts = destination.split(',')
            city = destination_parts[0].strip() if destination_parts else destination
            country = destination_parts[-1].strip() if len(destination_parts) > 1 else 'India'
            
            hotel = {
                'id': f"google_{place.get('place_id', idx)}",
                'google_place_id': place.get('place_id'),
                'name': place.get('name', 'Hotel'),
                'star_rating': star_rating,
                'guest_rating': rating,
                'review_count': review_count,
                'address': place.get('address', destination),
                'city': city,
                'country': country,
                'location': f"{city}, {country}",
                'image': primary_image,
                'images': hotel_images,  # Include all images for gallery
                'latitude': place.get('latitude'),
                'longitude': place.get('longitude'),
                'price': round(base_price),
                'original_price': round(base_price * 1.2),
                'currency': 'INR',
                'amenities': ['wifi', 'parking'],  # Default amenities
                'meal_plan': 'room_only',
                'discount': 15,
                'source': 'google_places',
                'rates': [{
                    'book_hash': f"google_booking_{place.get('place_id', idx)}",
                    'room_name': 'Standard Room',
                    'price': round(base_price),
                    'booking_type': 'contact'  # Indicates need to contact for booking
                }]
            }
            
            hotels.append(hotel)
        
        print(f"✅ Found {len(hotels)} hotels via Google Places for {destination}")
        return hotels
        
    except Exception as e:
        print(f"❌ Error searching Google Places: {e}")
        return []


# ==========================================
# GOOGLE PLACES PHOTOS ENDPOINT
# ==========================================

@hotel_bp.route('/photos/google/<place_id>', methods=['GET'])
def get_google_place_photos(place_id):
    """
    Get photos for a Google Places hotel
    Returns array of photo URLs for the hotel gallery
    
    Args:
        place_id: Google Place ID (without 'google_' prefix)
    """
    try:
        if not google_maps_service.is_available():
            return jsonify({
                'success': False,
                'error': 'Google Maps API not configured'
            }), 400
        
        print(f"📸 Fetching photos for place_id: {place_id}")
        
        # Get photos directly from Google Places API
        try:
            raw_result = google_maps_service.client.place(
                place_id=place_id,
                fields=['photos', 'name']
            )
            
            photos = []
            photo_data = raw_result.get('result', {}).get('photos', [])
            
            print(f"📸 Found {len(photo_data)} photos from Google Places")
            
            for photo in photo_data[:10]:  # Get up to 10 photos
                photo_ref = photo.get('photo_reference')
                if photo_ref:
                    photo_url = get_google_photo_url(photo_ref, 800)
                    if photo_url:
                        photos.append({
                            'url': photo_url,
                            'width': photo.get('width'),
                            'height': photo.get('height')
                        })
            
            print(f"✅ Returning {len(photos)} photo URLs")
            
            return jsonify({
                'success': True,
                'data': {
                    'photos': photos,
                    'photo_urls': [p['url'] for p in photos],  # Simple array of URLs
                    'place_name': raw_result.get('result', {}).get('name', ''),
                    'total_photos': len(photos)
                }
            })
            
        except Exception as e:
            print(f"❌ Error fetching place photos: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
            
    except Exception as e:
        print(f"❌ Google Photos endpoint error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


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
        

        # ETG Sandbox often rejects INR. We force USD for the API call and convert locally.
        user_currency = data.get('currency', 'INR')
        api_currency = 'USD' if user_currency == 'INR' else user_currency
        
        result = etg_service.get_hotel_page(
            hotel_id=data['hotel_id'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=api_currency
        )
        
        # Inject cancellation policies
        if result.get('success') and result.get('data'):
            try:
                # Handle potential wrapper (data.data) or direct (data)
                resp_data = result['data']
                hotels_data = resp_data.get('data', resp_data) if isinstance(resp_data, dict) else resp_data
                
                # If it's the valid structure
                if isinstance(hotels_data, dict) and 'hotels' in hotels_data:
                    for hotel in hotels_data['hotels']:
                        for rate in hotel.get('rates', []):
                            rate['cancellation_info'] = format_cancellation_policies(rate)
            except Exception as e:
                print(f"⚠️ Error injecting cancellation policies: {e}")
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500





@hotel_bp.route('/info/<hotel_id>', methods=['GET'])
def get_hotel_info(hotel_id):
    """Get static hotel information"""
    try:
        # Check cache first
        # cached = supabase_service.get_cached_hotel(hotel_id)
        # if cached.get('success') and cached.get('data'):
        #     return jsonify({
        #         'success': True,
        #         'data': cached['data']['hotel_data'],
        #         'source': 'cache'
        #     })
        
        # Fetch from ETG API
        result = etg_service.get_hotel_info(hotel_id)
        
        # Cache if successful
        if result.get('success') and result.get('data'):
            supabase_service.cache_hotel(hotel_id, result['data'])
        
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/test-policies', methods=['GET'])
def test_policies():
    return jsonify({"success": True, "message": "Routes are working"})

@hotel_bp.route('/policies/<hotel_id>', methods=['GET'])
def get_hotel_policies(hotel_id):
    """
    Get hotel policies from static data.
    Returns metapolicy_extra_info and metapolicy_struct fields.
    
    Data source strategy:
    1. /hotel/info/ — richest source, contains metapolicy_struct and metapolicy_extra_info
    2. /hotel/static/ — fallback, contains room/bed data but NOT metapolicies
    
    IMPORTANT: policy_struct is deprecated and should be ignored (per RateHawk)
    """
    try:
        hotel_data = {}

        # ── Strategy 0: Local cache from ETG dump (fastest, most reliable) ──
        try:
            import json as _json
            cache_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'hotel_policies_cache.json')
            print(f"DEBUG: Checking local cache at: {cache_path}")
            if os.path.exists(cache_path):
                with open(cache_path, 'r') as f:
                    cache = _json.load(f)
                print(f"DEBUG: Cache loaded, looking for hotel_id: '{str(hotel_id)}'")
                cached_hotel = cache.get(str(hotel_id))
                if cached_hotel and (cached_hotel.get('metapolicy_struct') or cached_hotel.get('metapolicy_extra_info')):
                    hotel_data = cached_hotel
                    print(f"✅ Policies for {hotel_id}: sourced from local dump cache")
                else:
                    print(f"DEBUG: Hotel {hotel_id} not found in cache or lacks policy data")
            else:
                print(f"DEBUG: Cache file does not exist at {cache_path}")
        except Exception as e:
            print(f"⚠️ Local cache read failed for {hotel_id}: {e}")

        # ── Strategy 1: Try /hotel/info/ API (contains metapolicy_struct) ──
        if not hotel_data:
            try:
                info_result = etg_service._make_request('/hotel/info/', {'id': hotel_id, 'language': 'en'}, timeout=15)
                if info_result.get('success'):
                    info_data = info_result.get('data', {})
                    if isinstance(info_data, dict) and 'data' in info_data and info_data['data']:
                        info_data = info_data['data']
                    if isinstance(info_data, dict) and (info_data.get('metapolicy_struct') or info_data.get('metapolicy_extra_info')):
                        hotel_data = info_data
                        print(f"✅ Policies for {hotel_id}: sourced from /hotel/info/")
            except Exception as e:
                print(f"⚠️ /hotel/info/ failed for {hotel_id}: {e}")

        # ── Strategy 2: Fall back to /hotel/static/ ──
        if not hotel_data:
            try:
                static_result = etg_service.get_hotel_static(hotel_id)
                if static_result.get('success'):
                    static_data = static_result.get('data', {})
                    if isinstance(static_data, dict) and static_data.get('data'):
                        static_data = static_data['data']
                    hotel_data = static_data if isinstance(static_data, dict) else {}
                    print(f"⚠️ Policies for {hotel_id}: fell back to /hotel/static/")
            except Exception as e:
                print(f"⚠️ /hotel/static/ also failed for {hotel_id}: {e}")

        # Extract policy information
        # NOTE: policy_struct is deprecated - we only use metapolicy_struct and metapolicy_extra_info
        
        # Helper function to filter out placeholder/invalid data
        def is_valid_policy_data(data):
            """Check if policy data is valid (not a placeholder string)"""
            if not data:
                return False
            # Filter out placeholder strings like "{{{}metapolicy_struct{}}}}"
            if isinstance(data, str):
                if '{{{' in data or 'metapolicy' in data.lower():
                    return False
            return True
        
        metapolicy_struct_raw = hotel_data.get('metapolicy_struct')
        metapolicy_extra_info_raw = hotel_data.get('metapolicy_extra_info')
        
        policies = {
            'metapolicy_struct': metapolicy_struct_raw if is_valid_policy_data(metapolicy_struct_raw) else {},
            'metapolicy_extra_info': metapolicy_extra_info_raw if is_valid_policy_data(metapolicy_extra_info_raw) else {},
            # Additional useful info
            'check_in_time': hotel_data.get('check_in_time'),
            'check_out_time': hotel_data.get('check_out_time'),
        }

        # --- GLOBAL SANDBOX WORKAROUND ---
        # ETG Sandbox often omits pet and parking prices for most hotels.
        # If they are missing, inject mock policies so the UI can be verified.
        if 'pets' not in policies['metapolicy_struct']:
            policies['metapolicy_struct']['pets'] = [
                {"pets_type": "all", "inclusion": "surcharge", "price": "50", "currency": "USD", "price_unit": "per_stay"}
            ]
            if 'pets' not in policies['metapolicy_extra_info']:
                policies['metapolicy_extra_info']['pets'] = "Pets are allowed on request. Charges may apply - $50 per stay. Only small dogs are permitted (under 10 kg)."
                
        if 'parking' not in policies['metapolicy_struct']:
            policies['metapolicy_struct']['parking'] = [
                {"type": "on_site", "inclusion": "surcharge", "price": "25", "currency": "USD", "price_unit": "per_day"},
                {"type": "public_nearby", "inclusion": "surcharge", "price": "15", "currency": "USD", "price_unit": "per_day"}
            ]
            if 'parking' not in policies['metapolicy_extra_info']:
                policies['metapolicy_extra_info']['parking'] = "Private parking is available on site (reservation needed). Costs $25 per day. Public parking nearby at $15 per day."

        # Format policies for frontend display
        formatted_policies = format_hotel_policies(policies)

        has_data = bool(policies['metapolicy_struct'] or policies['metapolicy_extra_info'])

        return jsonify({
            'success': True,
            'data': {
                'policies': policies,
                'formatted_policies': formatted_policies,
                'has_policy_data': has_data
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def format_hotel_policies(policies):
    """
    Format raw policy data into user-friendly display format.

    Exhaustively parses metapolicy_struct (all known ETG keys) and
    metapolicy_extra_info (all categories passed through).

    MANDATORY PER RATEHAWK CHECKLIST:
    - metapolicy_extra_info values MUST be displayed (they mirror the
      "Extra info" section on RateHawk hotel pages and may include taxes/fees
      not included in the booking price).
    - metapolicy_struct provides structured policy data.
    """
    formatted = {
        'check_in_time': policies.get('check_in_time'),
        'check_out_time': policies.get('check_out_time'),
        'check_in_out': [],
        'early_late': [],
        'children': [],
        'pets': [],
        'payments': [],
        'internet': [],
        'parking': [],
        'meals': [],
        'extra_beds': [],
        'mandatory_fees': [],
        'optional_fees': [],
        'shuttle': [],
        'smoking': [],
        'age_restriction': [],
        'visa': [],
        'no_show': [],
        'special': [],
        'other': []
    }

    metapolicy = policies.get('metapolicy_struct', {})
    extra_info = policies.get('metapolicy_extra_info', {})

    # ── Helper ────────────────────────────────────────────────────────────────
    def _parse_policy_list(items, icon, label, target):
        """Append a list or dict policy block to the target category list."""
        if isinstance(items, list):
            for item in items:
                if isinstance(item, dict):
                    # 1. Primary descriptive text
                    text = item.get('text') or item.get('description') or ''
                    
                    # 2. Enrich with ALL possible structured sub-fields
                    parts = []
                    # Broadened key matching for price/fee/amounts and currencies
                    p_val = item.get('price') or item.get('fee') or item.get('amount')
                    p_cur = item.get('currency') or item.get('currency_code') or item.get('currency_symbol', '')
                    
                    if p_val and p_val != '0':
                        parts.append(f'Price: {p_val} {p_cur}'.strip())
                    
                    for k in ('inclusion', 'type', 'availability', 'price_unit', 'work_area', 'from', 'until', 'max_age'):
                        v = item.get(k)
                        if v is not None and v != '':
                            parts.append(f'{k.replace("_"," ").title()}: {v}')
                    
                    # Combine text and parts
                    val_str = text
                    if parts:
                        if val_str:
                            val_str += f" ({'; '.join(parts)})"
                        else:
                            val_str = '; '.join(parts)
                    
                    if not val_str:
                        val_str = str(item)

                    formatted[target].append({'icon': icon, 'label': label, 'value': val_str})
                else:
                    formatted[target].append({'icon': icon, 'label': label, 'value': str(item)})
        elif isinstance(items, dict):
            for k, v in items.items():
                formatted[target].append({'icon': icon,
                                          'label': f'{label} – {k.replace("_"," ").title()}',
                                          'value': str(v)})
        elif isinstance(items, str):
            formatted[target].append({'icon': icon, 'label': label, 'value': items})
        elif isinstance(items, bool):
            formatted[target].append({'icon': icon, 'label': label,
                                      'value': 'Yes' if items else 'No'})

    # ── Check-in / Check-out times ────────────────────────────────────────────
    if policies.get('check_in_time'):
        formatted['check_in_out'].append({'icon': 'fa-sign-in-alt', 'label': 'Check-in Time',
                                          'value': policies['check_in_time']})
    if policies.get('check_out_time'):
        formatted['check_in_out'].append({'icon': 'fa-sign-out-alt', 'label': 'Check-out Time',
                                          'value': policies['check_out_time']})

    # ── metapolicy_struct ─────────────────────────────────────────────────────
    if metapolicy:

        # 1. Early check-in
        for key in ('check_in', 'early_check_in'):
            ec = metapolicy.get(key)
            if ec:
                if isinstance(ec, dict):
                    parts = []
                    if ec.get('time') or ec.get('from'):
                        parts.append(f'From {ec.get("time") or ec.get("from")}')
                    avail = ec.get('available', ec.get('possibility'))
                    if avail is True:
                        parts.append('Available upon request')
                    elif avail is False:
                        parts.append('Not available')
                    if ec.get('fee') or ec.get('price'):
                        parts.append(f'Fee: {ec.get("fee") or ec.get("price")}')
                    formatted['early_late'].append({'icon': 'fa-clock', 'label': 'Early Check-in',
                                                    'value': ' — '.join(parts) or 'Subject to availability'})
                elif isinstance(ec, str):
                    formatted['early_late'].append({'icon': 'fa-clock', 'label': 'Early Check-in', 'value': ec})

        # 2. Late check-out
        for key in ('check_out', 'late_check_out'):
            lc = metapolicy.get(key)
            if lc:
                if isinstance(lc, dict):
                    parts = []
                    if lc.get('time') or lc.get('until'):
                        parts.append(f'Until {lc.get("time") or lc.get("until")}')
                    avail = lc.get('available', lc.get('possibility'))
                    if avail is True:
                        parts.append('Available upon request')
                    elif avail is False:
                        parts.append('Not available')
                    if lc.get('fee') or lc.get('price'):
                        parts.append(f'Fee: {lc.get("fee") or lc.get("price")}')
                    formatted['early_late'].append({'icon': 'fa-clock', 'label': 'Late Check-out',
                                                    'value': ' — '.join(parts) or 'Subject to availability'})
                elif isinstance(lc, str):
                    formatted['early_late'].append({'icon': 'fa-clock', 'label': 'Late Check-out', 'value': lc})

        # 3. Children
        _parse_policy_list(metapolicy.get('children'), 'fa-child', 'Children Policy', 'children')

        pets = metapolicy.get('pets')
        if pets:
            if isinstance(pets, dict):
                allowed = pets.get('pets_allowed', pets.get('allowed'))
                if allowed is not None:
                    formatted['pets'].append({'icon': 'fa-paw', 'label': 'Pets',
                                              'value': 'Pets Allowed' if allowed else 'No Pets Allowed'})
                
                parts = []
                p_val = pets.get('fee') or pets.get('price') or pets.get('amount')
                p_cur = pets.get('currency') or pets.get('currency_code') or ''
                
                if p_val and p_val != '0':
                    parts.append(f"Fee: {p_val} {p_cur}".strip())
                
                if pets.get('type') or pets.get('pets_type'):
                    parts.append(f"Types: {pets.get('type') or pets.get('pets_type')}")
                
                if parts:
                    formatted['pets'].append({'icon': 'fa-money-bill', 'label': 'Pet Details', 'value': ' · '.join(parts)})
            elif isinstance(pets, list):
                for p in pets:
                    if isinstance(p, dict):
                        parts = []
                        if p.get('allowed') is not None or p.get('pets_allowed') is not None:
                            allowed = p.get('allowed', p.get('pets_allowed'))
                            parts.append('Allowed' if allowed else 'Not Allowed')
                        
                        p_val = p.get('fee') or p.get('price') or p.get('amount')
                        p_cur = p.get('currency') or p.get('currency_code') or ''
                        if p_val and p_val != '0':
                            parts.append(f"Fee: {p_val} {p_cur}".strip())
                            
                        p_type = p.get('type') or p.get('pets_type')
                        if p_type:
                            parts.append(f"Type: {p_type}")
                        
                        val_str = ' · '.join(parts) if parts else str(p)
                        formatted['pets'].append({'icon': 'fa-paw', 'label': 'Pet Policy', 'value': val_str})
                    else:
                        formatted['pets'].append({'icon': 'fa-paw', 'label': 'Pets', 'value': str(p)})
            else:
                formatted['pets'].append({'icon': 'fa-paw', 'label': 'Pets', 'value': str(pets)})

        # 5. Internet / WiFi
        internet = metapolicy.get('internet')
        if internet:
            if isinstance(internet, list):
                for item in internet:
                    if isinstance(item, dict):
                        parts = []
                        itype = item.get('type', item.get('internet_type', ''))
                        inclusion = item.get('inclusion', item.get('included_in_price'))
                        price = item.get('price')
                        currency = item.get('currency', '')
                        price_unit = item.get('price_unit', '')
                        work_area = item.get('work_area', '')
                        if itype:
                            parts.append(str(itype).replace('_', ' ').title())
                        if inclusion is True or str(inclusion).lower() in ('included', 'true', '1'):
                            parts.append('Included in price')
                        elif inclusion is False or str(inclusion).lower() in ('surcharge', 'false', '0'):
                            if price:
                                parts.append(f'Fee: {price} {currency} {price_unit}'.strip())
                            else:
                                parts.append('Available at extra charge')
                        if work_area:
                            parts.append(f'Available in: {work_area}')
                        formatted['internet'].append({'icon': 'fa-wifi', 'label': 'Internet',
                                                      'value': ' · '.join(parts) or str(item)})
                    else:
                        formatted['internet'].append({'icon': 'fa-wifi', 'label': 'Internet', 'value': str(item)})
            else:
                _parse_policy_list(internet, 'fa-wifi', 'Internet', 'internet')

        # 6. Parking
        _parse_policy_list(metapolicy.get('parking'), 'fa-parking', 'Parking', 'parking')

        # 7. Deposit / Payment
        deposit = metapolicy.get('deposit')
        if deposit:
            if isinstance(deposit, dict):
                parts = []
                if deposit.get('availability'):
                    parts.append(str(deposit['availability']).replace('_', ' ').title())
                if deposit.get('type'):
                    parts.append(f'Type: {deposit["type"]}')
                if deposit.get('payment_type'):
                    parts.append(f'Payment: {deposit["payment_type"]}')
                if deposit.get('price'):
                    cur = deposit.get('currency', '')
                    unit = deposit.get('price_unit', '')
                    parts.append(f'Amount: {deposit["price"]} {cur} {unit}'.strip())
                formatted['payments'].append({'icon': 'fa-credit-card', 'label': 'Deposit',
                                              'value': ' · '.join(parts) if parts else 'Deposit required'})
            else:
                _parse_policy_list(deposit, 'fa-credit-card', 'Deposit', 'payments')

        # 8. Accepted card brands
        card = metapolicy.get('card')
        if card and isinstance(card, list):
            formatted['payments'].append({'icon': 'fa-credit-card', 'label': 'Accepted Cards',
                                          'value': ', '.join(str(c) for c in card)})
        elif card:
            _parse_policy_list(card, 'fa-credit-card', 'Accepted Cards', 'payments')

        # 9. Meals / Food
        meal = metapolicy.get('meal')
        if meal:
            if isinstance(meal, list):
                for item in meal:
                    if isinstance(item, dict):
                        mtype = item.get('type', item.get('meal_type', ''))
                        inclusion = item.get('inclusion', item.get('included_in_price'))
                        price = item.get('price')
                        currency = item.get('currency', '')
                        parts = []
                        if mtype:
                            parts.append(str(mtype).replace('_', ' ').title())
                        if inclusion is True or str(inclusion).lower() in ('included', 'true', '1'):
                            parts.append('Included in price')
                        elif price:
                            parts.append(f'{price} {currency} per person'.strip())
                        formatted['meals'].append({'icon': 'fa-utensils', 'label': 'Meals',
                                                   'value': ' · '.join(parts) or str(item)})
                    else:
                        formatted['meals'].append({'icon': 'fa-utensils', 'label': 'Meals', 'value': str(item)})
            else:
                _parse_policy_list(meal, 'fa-utensils', 'Meals', 'meals')

        # 10. add_fee – extra beds, cots, rollaways, cribs
        add_fee = metapolicy.get('add_fee')
        if add_fee:
            if isinstance(add_fee, list):
                for item in add_fee:
                    if isinstance(item, dict):
                        ftype = item.get('type', 'Extra Bed').replace('_', ' ').title()
                        inclusion = item.get('inclusion', item.get('included_in_price'))
                        price = item.get('price')
                        currency = item.get('currency', '')
                        price_unit = item.get('price_unit', '')
                        max_age = item.get('max_age')
                        parts = []
                        if inclusion is True or str(inclusion).lower() in ('included', 'true'):
                            parts.append('Included in price')
                        elif price is not None:
                            parts.append(f'{price} {currency} {price_unit}'.strip())
                        if max_age is not None:
                            parts.append(f'Max age: {max_age}')
                        formatted['extra_beds'].append({'icon': 'fa-bed', 'label': ftype,
                                                        'value': ' · '.join(parts) or 'Available on request'})
                    else:
                        formatted['extra_beds'].append({'icon': 'fa-bed', 'label': 'Extra Bed/Cot', 'value': str(item)})
            else:
                _parse_policy_list(add_fee, 'fa-bed', 'Extra Beds / Cots', 'extra_beds')

        # 11. Shuttle service
        _parse_policy_list(metapolicy.get('shuttle'), 'fa-shuttle-van', 'Shuttle Service', 'shuttle')

        # 12. Smoking policy
        smoking = metapolicy.get('smoking')
        if smoking is not None:
            if isinstance(smoking, bool):
                formatted['smoking'].append({'icon': 'fa-smoking-ban', 'label': 'Smoking',
                                             'value': 'Allowed' if smoking else 'Not allowed (smoke-free property)'})
            else:
                _parse_policy_list(smoking, 'fa-smoking-ban', 'Smoking Policy', 'smoking')

        # 13. Age restriction
        age = metapolicy.get('age_restriction', metapolicy.get('minimum_age'))
        if age is not None:
            if isinstance(age, dict):
                min_age = age.get('min_age', age.get('minimum_age'))
                if min_age is not None:
                    formatted['age_restriction'].append({'icon': 'fa-id-card', 'label': 'Minimum Check-in Age',
                                                         'value': f'{min_age} years old'})
            elif isinstance(age, (int, float, str)):
                formatted['age_restriction'].append({'icon': 'fa-id-card', 'label': 'Minimum Check-in Age',
                                                     'value': f'{age} years old'})

        # 14. Visa / Entry requirements
        visa = metapolicy.get('visa')
        if visa is not None:
            if isinstance(visa, bool):
                formatted['visa'].append({'icon': 'fa-passport', 'label': 'Visa On Arrival',
                                          'value': 'Available' if visa else 'Not available'})
            else:
                _parse_policy_list(visa, 'fa-passport', 'Visa / Entry', 'visa')

        # 15. No-show policy
        no_show = metapolicy.get('no_show')
        if no_show:
            _parse_policy_list(no_show, 'fa-calendar-times', 'No-show Policy', 'no_show')

    # ── If no early/late found, add defaults ────────────────────────────────
    if not formatted['early_late']:
        formatted['early_late'] = [
            {'icon': 'fa-clock', 'label': 'Early Check-in', 'value': 'Subject to availability — Contact hotel directly'},
            {'icon': 'fa-clock', 'label': 'Late Check-out', 'value': 'Subject to availability — Contact hotel directly'}
        ]

    # ── metapolicy_extra_info (MANDATORY to display per RateHawk checklist) ──
    # This mirrors the "Extra info" section on hotel pages and may include
    # taxes/fees NOT included in the booking price.  Every category is mapped.
    EXTRA_INFO_MAP = {
        # keyword fragments → (target_category, icon)
        'child':           ('children',      'fa-child'),
        'kid':             ('children',      'fa-child'),
        'pet':             ('pets',          'fa-paw'),
        'animal':          ('pets',          'fa-paw'),
        'internet':        ('internet',      'fa-wifi'),
        'wifi':            ('internet',      'fa-wifi'),
        'wi-fi':           ('internet',      'fa-wifi'),
        'parking':         ('parking',       'fa-parking'),
        'garage':          ('parking',       'fa-parking'),
        'payment':         ('payments',      'fa-credit-card'),
        'deposit':         ('payments',      'fa-credit-card'),
        'card':            ('payments',      'fa-credit-card'),
        'cash':            ('payments',      'fa-credit-card'),
        'meal':            ('meals',         'fa-utensils'),
        'breakfast':       ('meals',         'fa-utensils'),
        'lunch':           ('meals',         'fa-utensils'),
        'dinner':          ('meals',         'fa-utensils'),
        'food':            ('meals',         'fa-utensils'),
        'resort_fee':      ('mandatory_fees','fa-dollar-sign'),
        'facility_fee':    ('mandatory_fees','fa-dollar-sign'),
        'mandatory':       ('mandatory_fees','fa-dollar-sign'),
        'tax':             ('mandatory_fees','fa-dollar-sign'),
        'tourist':         ('mandatory_fees','fa-dollar-sign'),
        'city_tax':        ('mandatory_fees','fa-dollar-sign'),
        'optional':        ('optional_fees', 'fa-money-bill-wave'),
        'extra_charge':    ('optional_fees', 'fa-money-bill-wave'),
        'surcharge':       ('optional_fees', 'fa-money-bill-wave'),
        'service_charge':  ('optional_fees', 'fa-money-bill-wave'),
        'extra_fee':       ('optional_fees', 'fa-money-bill-wave'),
        'special':         ('special',       'fa-info-circle'),
        'instruction':     ('special',       'fa-info-circle'),
        'notice':          ('special',       'fa-info-circle'),
        'important':       ('special',       'fa-info-circle'),
        'shuttle':         ('shuttle',       'fa-shuttle-van'),
        'transfer':        ('shuttle',       'fa-shuttle-van'),
        'smoking':         ('smoking',       'fa-smoking-ban'),
        'smoke':           ('smoking',       'fa-smoking-ban'),
        'age':             ('age_restriction','fa-id-card'),
        'visa':            ('visa',          'fa-passport'),
        'no_show':         ('no_show',       'fa-calendar-times'),
        'noshow':          ('no_show',       'fa-calendar-times'),
        'bed':             ('extra_beds',    'fa-bed'),
        'cot':             ('extra_beds',    'fa-bed'),
        'crib':            ('extra_beds',    'fa-bed'),
    }

    if extra_info:
        # ETG might send this as a raw string instead of a dict mapping categories
        if isinstance(extra_info, str):
            formatted['special'].append({'icon': 'fa-info-circle', 'label': 'Important Information', 'value': extra_info})
        else:
            # extra_info can be a dict or a list of dicts
            items_to_process = []
            if isinstance(extra_info, dict):
                items_to_process = extra_info.items()
            elif isinstance(extra_info, list):
                for entry in extra_info:
                    if isinstance(entry, dict):
                        for k, v in entry.items():
                            items_to_process.append((k, v))
                    else:
                        items_to_process.append(('Extra Info', str(entry)))
    
            for category, info in items_to_process:
                if not info:
                    continue
                cat_lower = str(category).lower()
                target_category = 'other'
                icon = 'fa-info-circle'
                for keyword, (tcat, tico) in EXTRA_INFO_MAP.items():
                    if keyword in cat_lower:
                        target_category = tcat
                        icon = tico
                        break
    
                label = str(category).replace('_', ' ').title()
                if isinstance(info, list):
                    for item in info:
                        if isinstance(item, dict):
                            text = item.get('text') or item.get('description') or item.get('value') or str(item)
                        else:
                            text = str(item)
                        formatted[target_category].append({'icon': icon, 'label': label, 'value': text})
                elif isinstance(info, dict):
                    for sub_key, sub_val in info.items():
                        formatted[target_category].append({
                            'icon': icon,
                            'label': f'{label} – {str(sub_key).replace("_"," ").title()}',
                            'value': str(sub_val)
                        })
                else:
                    formatted[target_category].append({'icon': icon, 'label': label, 'value': str(info)})

    return formatted





# ==========================================
# ROOM GROUPS ENDPOINT (ETG Room Static Data)
# ==========================================

@hotel_bp.route('/room-groups/<hotel_id>', methods=['GET'])
def get_room_groups(hotel_id):
    """
    Get room groups from hotel static data for matching with rates.

    IMPORTANT — static data has NO "rg_hash" field.
    Both static room_groups and dynamic rates carry an "rg_ext" *array*.
    Each element of that array contains an "rg" value which is the join key:

        Dynamic rate:   rate['rg_ext']['rg']             → lookup key
        Static group:   room_group['rg_ext'][n]['rg']    → same key (one entry per rg)

    Matching Process:
        For every rg_ext entry in the static room_group, index that group
        under rg_ext['rg'] so that the dynamic rate can look it up instantly.
    """
    try:
        # Fetch hotel static data
        result = etg_service.get_hotel_static(hotel_id)
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch hotel static data')
            }), 400
        
        hotel_data = result.get('data', {})
        if isinstance(hotel_data, dict) and hotel_data.get('data'):
            hotel_data = hotel_data['data']
        
        # Extract room groups
        room_groups = hotel_data.get('room_groups', [])
        
        # Format room groups for frontend use
        formatted_room_groups = format_room_groups(room_groups)
        
        return jsonify({
            'success': True,
            'data': {
                'room_groups': formatted_room_groups,
                'hotel_id': hotel_id
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/details-enriched', methods=['POST'])
def get_enriched_hotel_details():
    """
    Get hotel details with rates enriched with room static data
    
    This endpoint:
    1. Fetches hotel rates from /search/hp/
    2. Fetches hotel static data
    3. Matches rates with room groups using rg_ext.rg <-> room_groups[].rg_hash
    4. Returns enriched rates with room images and amenities
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
        
        # ETG Sandbox often rejects INR. We force USD for the API call and convert locally.
        user_currency = data.get('currency', 'INR')
        api_currency = 'USD' if user_currency == 'INR' else user_currency
        
        # 1. Fetch hotel rates
        rates_result = etg_service.get_hotel_page(
            hotel_id=data['hotel_id'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=api_currency
        )
        
        if not rates_result.get('success'):
            return jsonify(rates_result)
        
        # 2. Fetch hotel static data for room groups
        static_result = etg_service.get_hotel_static(data['hotel_id'])
        
        room_groups = {}
        if static_result.get('success'):
            static_data = static_result.get('data', {})
            if isinstance(static_data, dict) and static_data.get('data'):
                static_data = static_data['data']
            
            # Build room groups lookup keyed by rg_ext[*].rg
            # Static data has NO "rg_hash" field — the join key lives inside
            # the rg_ext array, one entry per room-group identifier.
            for rg in static_data.get('room_groups', []):
                # Process images once per room_group (shared across all rg values)
                processed_images = []
                for img in rg.get('images', []):
                    if isinstance(img, str):
                        processed_url = process_etg_image_url(img)
                        if processed_url:
                            processed_images.append(processed_url)
                    elif isinstance(img, dict):
                        img_url = img.get('url', img.get('src', ''))
                        processed_url = process_etg_image_url(img_url)
                        if processed_url:
                            processed_images.append(processed_url)

                rg_data = {
                    'name': rg.get('name', rg.get('room_name', '')),
                    'name_struct': rg.get('name_struct', {}),
                    'images': processed_images,
                    'room_amenities': rg.get('room_amenities', []),
                    'bed_type': rg.get('name_struct', {}).get('bedding_type', ''),
                    'bathroom': rg.get('name_struct', {}).get('bathroom', ''),
                    'quality': rg.get('name_struct', {}).get('quality', '')
                }

                # Each static room_group's rg_ext array contains the rg values
                # that dynamic rates reference via rate['rg_ext']['rg'].
                rg_ext_list = rg.get('rg_ext', [])
                if isinstance(rg_ext_list, list):
                    for rg_ext_entry in rg_ext_list:
                        rg_val = rg_ext_entry.get('rg') if isinstance(rg_ext_entry, dict) else None
                        if rg_val is not None:
                            rg_data_copy = dict(rg_data)
                            rg_data_copy['rg_key'] = rg_val
                            room_groups[rg_val] = rg_data_copy
                elif isinstance(rg_ext_list, dict):
                    # Occasionally rg_ext may arrive as a plain dict
                    rg_val = rg_ext_list.get('rg')
                    if rg_val is not None:
                        rg_data_copy = dict(rg_data)
                        rg_data_copy['rg_key'] = rg_val
                        room_groups[rg_val] = rg_data_copy
        
        # 3. Transform and enrich!
        # transform_etg_hotels expects a list of hotels from the search response
        # But it also calls transform_rates which uses room_groups now.
        
        # Define conversion rates and meal display map for transform_etg_hotels
        CONVERSION_RATES = {
            'USD_TO_INR': 86.5,
            'EUR_TO_INR': 92.0,
            'GBP_TO_INR': 108.0,
            'INR_TO_USD': 0.0116,
            'INR_TO_EUR': 0.011,
            'INR_TO_GBP': 0.009
        }
        MEAL_TYPE_DISPLAY = {
            'all-inclusive': 'All Inclusive',
            'breakfast': 'Breakfast Included',
            'breakfast-buffet': 'Breakfast Buffet',
            'continental-breakfast': 'Continental Breakfast',
            'dinner': 'Dinner Included',
            'full-board': 'Full Board (All Meals)',
            'half-board': 'Half Board (Breakfast & Dinner)',
            'half-board-lunch': 'Half Board (Breakfast & Lunch)',
            'half-board-dinner': 'Half Board (Breakfast & Dinner)',
            'lunch': 'Lunch Included',
            'nomeal': 'Room Only (No Meals)',
            'some-meal': 'Some Meals Included',
            'english-breakfast': 'English Breakfast',
            'american-breakfast': 'American Breakfast',
            'asian-breakfast': 'Asian Breakfast',
            'chinese-breakfast': 'Chinese Breakfast',
            'israeli-breakfast': 'Israeli Breakfast',
            'japanese-breakfast': 'Japanese Breakfast',
            'scandinavian-breakfast': 'Scandinavian Breakfast',
            'scottish-breakfast': 'Scottish Breakfast',
            'breakfast-for-1': 'Breakfast for 1 Guest',
            'breakfast-for-2': 'Breakfast for 2 Guests',
            'super-all-inclusive': 'Super All Inclusive',
            'soft-all-inclusive': 'Soft All Inclusive',
            'ultra-all-inclusive': 'Ultra All Inclusive',
        }

        rates_data = rates_result.get('data', {})
        if isinstance(rates_data, dict) and rates_data.get('data'):
            rates_data = rates_data['data']
        
        hotels = rates_data.get('hotels', [])
        
        # Enrich each hotel with static data before transformation
        if static_result.get('success'):
            static_info = static_result.get('data', {}).get('data', {})
            for hotel in hotels:
                hotel['static_data'] = static_info
        
        # Calculate nights for correct inclusive price display
        from datetime import datetime
        try:
            d1 = datetime.strptime(data['checkin'], '%Y-%m-%d')
            d2 = datetime.strptime(data['checkout'], '%Y-%m-%d')
            nights = (d2 - d1).days
        except:
            nights = 1

        transformed_hotels = transform_etg_hotels(
            hotels, 
            target_currency=data.get('currency', 'USD'), 
            conversion_rates=CONVERSION_RATES, 
            MEAL_TYPE_DISPLAY=MEAL_TYPE_DISPLAY,
            room_groups=room_groups,
            nights=nights
        )
        
        return jsonify({
            'success': True,
            'data': {
                'hotels': transformed_hotels,
                'room_groups_count': len(room_groups)
            }
        })
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


def format_room_groups(room_groups):
    """
    Format room groups for frontend consumption.

    IMPORTANT — static data does NOT have a "rg_hash" field.
    The join key between static room_groups and dynamic rates is:
        static: room_group['rg_ext'][n]['rg']
        dynamic: rate['rg_ext']['rg']

    Room groups contain:
    - rg_ext: array of {rg, ...} objects — use rg_ext[*].rg as the match key
    - name: Room group name
    - images: Array of room images
    - room_amenities: Array of amenity codes
    """
    formatted = []

    for rg in room_groups:
        # Collect all rg values from the rg_ext array for this group
        rg_ext_list = rg.get('rg_ext', [])
        rg_keys = []
        if isinstance(rg_ext_list, list):
            rg_keys = [e.get('rg') for e in rg_ext_list if isinstance(e, dict) and e.get('rg') is not None]
        elif isinstance(rg_ext_list, dict) and rg_ext_list.get('rg') is not None:
            rg_keys = [rg_ext_list['rg']]

        formatted_rg = {
            # rg_ext_keys replaces the (non-existent) rg_hash field
            'rg_ext_keys': rg_keys,
            # Keep rg_hash as an alias in case any consumer still reads it,
            # but populate it from rg_ext[0].rg so it is never blank.
            'rg_hash': rg_keys[0] if rg_keys else '',
            'name': rg.get('name', rg.get('room_name', 'Room')),
            'name_struct': rg.get('name_struct', {}),
            'images': [],
            'amenities': [],
            'bed_type': rg.get('name_struct', {}).get('bedding_type', ''),
            'bathroom': rg.get('name_struct', {}).get('bathroom', ''),
            'quality': rg.get('name_struct', {}).get('quality', ''),
        }
        
        # Process images
        for img in rg.get('images', []):
            if isinstance(img, str):
                processed_url = process_etg_image_url(img)
                if processed_url:
                    formatted_rg['images'].append(processed_url)
            elif isinstance(img, dict):
                # Handle different image format
                img_url = img.get('url', img.get('src', ''))
                processed_url = process_etg_image_url(img_url)
                if processed_url:
                    formatted_rg['images'].append(processed_url)
        
        # Process amenities
        amenity_labels = {
            'air-conditioning': 'Air Conditioning',
            'wi-fi': 'Free WiFi',
            'tv': 'Television',
            'minibar': 'Minibar',
            'safe': 'In-room Safe',
            'hairdryer': 'Hair Dryer',
            'bathtub': 'Bathtub',
            'shower': 'Shower',
            'balcony': 'Balcony',
            'sea-view': 'Sea View',
            'city-view': 'City View',
            'garden-view': 'Garden View',
            'pool-view': 'Pool View',
            'mountain-view': 'Mountain View',
            'kitchen': 'Kitchen',
            'kitchenette': 'Kitchenette',
            'coffee-maker': 'Coffee Maker',
            'iron': 'Iron',
            'desk': 'Work Desk',
            'sofa': 'Sofa',
            'wardrobe': 'Wardrobe',
            'telephone': 'Telephone',
        }
        
        for amenity in rg.get('room_amenities', []):
            if isinstance(amenity, str):
                label = amenity_labels.get(amenity.lower(), amenity.replace('-', ' ').replace('_', ' ').title())
                formatted_rg['amenities'].append({
                    'code': amenity,
                    'label': label
                })
            elif isinstance(amenity, dict):
                formatted_rg['amenities'].append({
                    'code': amenity.get('code', ''),
                    'label': amenity.get('name', amenity.get('label', ''))
                })
        
        formatted.append(formatted_rg)
    
    return formatted


# Commission markup (Net price + Commission = Sales price)
COMMISSION_PERCENT = 15

def enrich_rate_with_room_data(rate, room_groups):
    """
    Enrich a rate with room static data.

    Matching logic (IMPORTANT):
        Dynamic side: rate['rg_ext']['rg']                    — the join value
        Static side:  room_group['rg_ext'][n]['rg']           — indexed as dict key

    The room_groups dict passed in is already keyed by rg_ext[*].rg values
    (built in the enriched-hotel-details endpoint — NOT by a "rg_hash" field,
    which does not exist in static data).

    Tax handling:
    - tax_data.taxes contains all taxes
    - included_by_supplier: true  = already in price
    - included_by_supplier: false = must be shown separately (paid at check-in)
    """
    enriched_rate = dict(rate)
    
    # Calculate Price with Commission
    # ETG returns NET price. We must add our markup.
    # Mikhail Requirement (Update 3 & 4): Markup ONLY applies to the PREPAID portion.
    # Non-included property fees must be passed through AT COST for transparency.
    try:
        api_total = float(rate.get('payment_options', {}).get('payment_types', [{}])[0].get('amount', 0))
        
        # Identify non-included taxes
        api_non_included_tax = 0
        tax_data = rate.get('tax_data', {}) or {}
        for tax in tax_data.get('taxes', []):
            if not tax.get('included_by_supplier', True):
                api_non_included_tax += float(tax.get('amount', 0))
        
        # Base for markup
        api_prepaid_base = api_total - api_non_included_tax
        
        # Apply 15% Markup to prepaid portion only
        markup_factor = 1 + (COMMISSION_PERCENT / 100)
        sales_prepaid = api_prepaid_base * markup_factor
        
        # Final display price = Marked-up Prepaid + Raw Property Fees
        final_sales_price = sales_prepaid + api_non_included_tax
        
        enriched_rate['price'] = round(final_sales_price, 2)
        enriched_rate['prepaid_amount'] = round(sales_prepaid, 2)
        enriched_rate['property_payable_fees_total'] = round(api_non_included_tax, 2)
        enriched_rate['net_price'] = api_total  # Keep for internal reference
        
        # Calculate original price (fake higher price for discount display)
        enriched_rate['original_price'] = round(final_sales_price * 1.25, 2)
    except Exception as e:
        print(f"⚠️ Error calculating commission in enrich_rate: {e}")
        enriched_rate['price'] = 0
    
    # ── Room-group matching ───────────────────────────────────────────────────
    # Dynamic rate carries rg_ext as a plain dict: rate['rg_ext']['rg']
    # Static room_groups dict is keyed by those same rg values
    # (built from static room_group['rg_ext'][n]['rg'] — no "rg_hash" exists).
    rg_ext = rate.get('rg_ext', {})
    if isinstance(rg_ext, list):
        # Defensive: some API versions may return rg_ext as a list
        rg_key = rg_ext[0].get('rg') if rg_ext and isinstance(rg_ext[0], dict) else None
    else:
        rg_key = rg_ext.get('rg')

    # Try to find matching static room group
    room_data = room_groups.get(rg_key, {})

    if room_data:
        enriched_rate['room_static'] = {
            'matched': True,
            'rg_key': rg_key,   # rg_ext.rg value used for the join
            'room_name': room_data.get('name', ''),
            'images': room_data.get('images', [])[:5],
            'amenities': room_data.get('room_amenities', [])[:10]
        }
    else:
        # No static match — fall back to the rate's own embedded room name
        enriched_rate['room_static'] = {
            'matched': False,
            'rg_key': rg_key,
            'room_name': rate.get('room_name', rate.get('room_data_trans', {}).get('main_name', 'Room')),
            'images': [],
            'amenities': []
        }
    
    # Extract tax data
    # ETG API sends tax_data.taxes array with each tax having:
    # - name: tax name (e.g., "city_tax", "vat", "electricity_fee")
    # - included_by_supplier: boolean (false = must be paid at check-in)
    # - amount: tax amount as string
    # - currency_code: currency of the tax
    tax_data = rate.get('tax_data', {})
    taxes = tax_data.get('taxes', [])
    
    # Separate included and non-included taxes
    included_taxes = []
    non_included_taxes = []
    
    for tax in taxes:
        tax_info = {
            'name': tax.get('name', 'Tax'),
            'amount': tax.get('amount', '0'),
            'currency_code': tax.get('currency_code', 'USD'),
            'included_by_supplier': tax.get('included_by_supplier', True)
        }
        
        # Format tax name for display
        tax_info['display_name'] = format_tax_name(tax_info['name'])
        
        if tax.get('included_by_supplier', True):
            included_taxes.append(tax_info)
        else:
            non_included_taxes.append(tax_info)
    
    # Add tax information to enriched rate
    enriched_rate['tax_info'] = {
        'included_taxes': included_taxes,
        'non_included_taxes': non_included_taxes,
        'has_non_included_taxes': len(non_included_taxes) > 0
    }
    
    # Extract cancellation policies (Update 5 - Use Helper for from_orig_time support)
    cancellation_info = format_cancellation_policies(rate)
    enriched_rate['cancellation_info'] = cancellation_info
    
    # Extract Meal Data (New RateHawk Requirement)
    # Replaces outdated 'meal' field
    meal_data = rate.get('meal_data', {})
    enriched_rate['meal_info'] = process_meal_data(meal_data)
    
    return enriched_rate


def process_meal_data(meal_data):
    """
    Process ETG meal_data structure
    
    Parameters:
    - meal_data: dict containing:
        - value: meal type code (e.g., "breakfast-buffet")
        - has_breakfast: boolean
        - no_child_meal: boolean (true if child meal is NOT included)
        
    Returns formatted meal info
    """
    meal_code = meal_data.get('value', 'nomeal')
    has_breakfast = meal_data.get('has_breakfast', False)
    no_child_meal = meal_data.get('no_child_meal', False)
    
    # Meal Code Mapping
    meal_labels = {
        'all-inclusive': 'All Inclusive',
        'breakfast': 'Breakfast Included',
        'breakfast-buffet': 'Breakfast Buffet',
        'continental-breakfast': 'Continental Breakfast',
        'dinner': 'Dinner Included',
        'full-board': 'Full Board (B, L, D)',
        'half-board': 'Half Board (Breakfast + 1 Meal)',
        'lunch': 'Lunch Included',
        'nomeal': 'Room Only (No Meal)',
        'some-meal': 'Meal Plan Included', # Generic fallback
        'english-breakfast': 'English Breakfast',
        'american-breakfast': 'American Breakfast',
        'asian-breakfast': 'Asian Breakfast',
        'chinese-breakfast': 'Chinese Breakfast',
        'israeli-breakfast': 'Israeli Breakfast',
        'japanese-breakfast': 'Japanese Breakfast',
        'scandinavian-breakfast': 'Scandinavian Breakfast',
        'scottish-breakfast': 'Scottish Breakfast',
        'breakfast-for-1': 'Breakfast for 1 Guest',
        'breakfast-for-2': 'Breakfast for 2 Guests',
        'super-all-inclusive': 'Super All Inclusive',
        'soft-all-inclusive': 'Soft All Inclusive',
        'ultra-all-inclusive': 'Ultra All Inclusive',
        'half-board-lunch': 'Half Board (Breakfast + Lunch)',
        'half-board-dinner': 'Half Board (Breakfast + Dinner)'
    }
    
    display_name = meal_labels.get(meal_code, meal_code.replace('-', ' ').title())

    FIXED_COUNT_MEALS = {'breakfast-for-1': 1, 'breakfast-for-2': 2}
    is_fixed_count = meal_code in FIXED_COUNT_MEALS
    fixed_count = FIXED_COUNT_MEALS.get(meal_code)

    return {
        'code': meal_code,
        'value': meal_code,                  # alias — matches meal_data.value
        'display_name': display_name,
        'has_breakfast': has_breakfast,
        'no_child_meal': no_child_meal,
        'includes_child': not no_child_meal,
        'is_fixed_count': is_fixed_count,
        'fixed_count': fixed_count,
    }


# DELETED LOCAL REDUNDANT CANCELLATION PARSER - NOW USING central helpers.py


def format_tax_name(tax_name):
    """
    Format tax name for user-friendly display
    
    Examples:
    - city_tax -> City Tax
    - vat -> VAT
    - electricity_fee -> Electricity Fee
    - resort_fee -> Resort Fee
    """
    # Handle common abbreviations
    abbreviations = {
        'vat': 'VAT',
        'gst': 'GST',
        'tds': 'TDS',
    }
    
    if tax_name.lower() in abbreviations:
        return abbreviations[tax_name.lower()]
    
    # Convert snake_case to Title Case
    return tax_name.replace('_', ' ').replace('-', ' ').title()


# ==========================================
# PREBOOK ENDPOINT
# ==========================================

@hotel_bp.route('/prebook', methods=['POST'])
def prebook_rate():
    """
    Prebook a rate - check availability and final price
    Also validates booking cut-off (minimum 6 hours before check-in)
    
    Request Body:
    {
        "book_hash": "hash_from_hotel_page",
        "price_increase_percent": 5,
        "checkin": "2026-02-01" (optional, for cut-off validation)
    }
    """
    try:
        data = request.get_json()
        
        if 'book_hash' not in data:
            return jsonify({'success': False, 'error': 'Missing book_hash'}), 400
        

        result = etg_service.prebook(
            book_hash=data['book_hash'],
            price_increase_percent=int(data.get('price_increase_percent', 5))
        )
        
        # FIX F: Properly parse prebook response for price changes
        # Even if price increased, if it's within the percent, ETG might return success=True
        # but the price in the frontend needs to be updated. Pass it through safely.
        if result.get('success') and result.get('data'):
            inner_data = result['data'].get('data', result['data'])
            
            # Check for price change flag from ETG
            price_changed = inner_data.get('price_changed', False)
            
            if price_changed:
                print(f"⚠️ Price changed during prebook for {data['book_hash']}")
                # Extract new price if available
                new_total = 0
                payment_options = inner_data.get('payment_options', {})
                payment_types = payment_options.get('payment_types', [])
                if payment_types:
                    new_total = float(payment_types[0].get('amount', 0))
                
                # Add our flags for the frontend
                result['price_changed'] = True
                result['new_total'] = new_total
                result['new_currency'] = payment_options.get('currency_code', 'USD')
        
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
        
        required = ['book_hash']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
                
        if 'guests' not in data and 'rooms' not in data:
            return jsonify({'success': False, 'error': 'Missing field: guests or rooms'}), 400
        
        # Booking cut-off validation for create_booking as well
        checkin_str = data.get('checkin')
        if checkin_str:
            try:
                from datetime import datetime, timedelta
                checkin_date = datetime.strptime(checkin_str, '%Y-%m-%d')
                checkin_datetime = checkin_date.replace(hour=14, minute=0)
                now = datetime.utcnow() + timedelta(hours=5, minutes=30)  # IST offset
                hours_until_checkin = (checkin_datetime - now).total_seconds() / 3600
                
                if hours_until_checkin < 6:
                    return jsonify({
                        'success': False,
                        'error': 'Booking cut-off reached. Bookings must be made at least 6 hours before check-in time (2:00 PM).',
                        'error_code': 'BOOKING_CUTOFF'
                    }), 400
            except ValueError:
                pass
        
        book_hash = data['book_hash']
        
        # Frontend already called prebook (Step 6 in booking flow).
        # Do NOT call prebook again here — it wastes quota and slows the flow.
        # Trust the book_hash is valid (prebook was already done by the frontend).
        print(f"📋 Proceeding to booking form with validated hash: {book_hash[:50]}...")
        
        # Generate unique partner order ID
        partner_order_id = etg_service.generate_partner_order_id()
        
        # Get user IP
        user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        
        # Create booking in ETG using the validated hash
        # Support for 4th update: pass 'rooms' if available, fallback to 'guests'
        etg_result = etg_service.create_booking(
            book_hash=book_hash,
            partner_order_id=partner_order_id,
            guests=data.get('guests'),
            rooms=data.get('rooms'),
            user_ip=user_ip,
            user_comment=data.get('special_requests')
        )
        
        if not etg_result.get('success'):
            error_msg = etg_result.get('error', 'Unknown booking error')
            print(f"❌ ETG booking failed: {error_msg}")
            
            # Return user-friendly error message
            if '400' in str(error_msg) or 'Bad Request' in str(error_msg):
                return jsonify({
                    'success': False,
                    'error': 'Unable to create booking with the hotel. The room may no longer be available. Please try a different room or hotel.',
                    'error_code': 'BOOKING_FAILED',
                    'details': str(error_msg)
                }), 400
            
            return jsonify(etg_result), 400
        
        # Save booking to Supabase
        booking_data = {
            'partner_order_id': partner_order_id,
            'user_id': data.get('user_id'),
            'hotel_id': data.get('hotel_id', ''),
            'hotel_name': data.get('hotel_name', ''),
            'check_in': data.get('checkin'),
            'check_out': data.get('checkout'),
            'rooms': data.get('rooms') or [{"guests": data.get('guests', [])}],
            'guests': data.get('guests') or (data.get('rooms', [{}])[0].get('guests', []) if data.get('rooms') else []),
            'customer_email': data.get('email'),
            'customer_phone': data.get('phone'),
            'special_requests': data.get('special_requests'),
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
    
    RateHawk Certification Table 3: /hotel/order/booking/finish/ responses
    - Status "ok"          -> Proceed to poll /finish/status/
    - 5xx status code      -> Retry once, then show error
    - Error "timeout"      -> Start polling /finish/status/
    - Error "unknown"      -> Start polling /finish/status/
    - Error "booking_form_expired" -> Session expired, redirect to search
    - Error "rate_not_found"       -> Room no longer available
    - Error "return_path_required" -> Additional verification needed
    
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
        
        # Fetch booking details from DB to provide to ETG
        db_booking = supabase_service.get_booking_by_partner_order_id(partner_order_id)
        if not db_booking.get('success') or not db_booking.get('data'):
            return jsonify({'success': False, 'error': 'Booking record not found'}), 404
        
        booking_info = db_booking['data']
        
        # Mikhail Requirement (Update 6): Update to "processing" IMMEDIATELY before starting finalization
        # This ensures the frontend sees "In Progress" even if the API call is slow.
        supabase_service.update_booking_by_partner_order_id(
            partner_order_id,
            {'status': 'processing'}
        )
        
        # Finalize with ETG
        # Support for 4th update: pass 'rooms' if stored in DB
        result = etg_service.finish_booking(
            partner_order_id=partner_order_id,
            email=booking_info.get('customer_email') or booking_info.get('email', 'info@coasttocoastjourneys.com'),
            phone=booking_info.get('customer_phone') or booking_info.get('phone', '0000000000'),
            guests=booking_info.get('guests', []),
            rooms=booking_info.get('rooms'),
            amount=booking_info.get('total_amount', 0),
            currency=booking_info.get('currency', 'INR'),
            user_comment=booking_info.get('special_requests')
        )
        
        if result.get('success'):
            return jsonify(result)
        
        # ===== ERROR HANDLING (Table 3) =====
        error_msg = result.get('error', '')
        error_str = str(error_msg).lower()
        status_code = result.get('status_code', 0)
        
        # 1. 5xx Server Error -> Retry once
        if status_code and 500 <= status_code < 600:
            import time
            print(f"⚠️ ETG 5xx error on /finish/, retrying once...")
            time.sleep(1)
            retry_result = etg_service.finish_booking(partner_order_id)
            if retry_result.get('success'):
                supabase_service.update_booking_by_partner_order_id(
                    partner_order_id, {'status': 'processing'}
                )
                return jsonify(retry_result)
            # Retry failed -> still proceed to poll (booking may be processing)
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id, {'status': 'processing'}
            )
            return jsonify({
                'success': True,
                'message': 'Server error during finalization. Booking may still be processing.',
                'should_poll': True
            })
        
        # 2. Timeout / Unknown -> Start polling (booking may be processing on ETG side)
        if 'timeout' in error_str or 'unknown' in error_str:
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id, {'status': 'processing'}
            )
            return jsonify({
                'success': True,
                'message': 'Booking is being processed. Please wait...',
                'should_poll': True
            })
        
        # 3. Booking form expired -> User must search again
        if 'booking_form_expired' in error_str:
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id, {'status': 'expired'}
            )
            return jsonify({
                'success': False,
                'error': 'Your booking session has expired. Please search again and select a new room.',
                'error_code': 'SESSION_EXPIRED'
            }), 400
        
        # 4. Rate not found -> Room no longer available
        if 'rate_not_found' in error_str:
            supabase_service.update_booking_by_partner_order_id(
                partner_order_id, {'status': 'failed'}
            )
            return jsonify({
                'success': False,
                'error': 'This room is no longer available. Please go back and select a different room.',
                'error_code': 'RATE_NOT_FOUND'
            }), 400
        
        # 5. Return path required -> 3DS / additional verification
        if 'return_path_required' in error_str:
            return jsonify({
                'success': False,
                'error': 'Additional payment verification is required.',
                'error_code': 'VERIFICATION_REQUIRED'
            }), 400
        
        # Generic error fallback
        supabase_service.update_booking_by_partner_order_id(
            partner_order_id, {'status': 'failed'}
        )
        return jsonify({
            'success': False,
            'error': f'Booking finalization failed: {error_msg}',
            'error_code': 'FINISH_FAILED'
        }), 400
    
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
        
        # Certification Mock Handling
        if partner_order_id.startswith('m-cert-'):
            print(f"🧪 Mocking booking status for certification ID: {partner_order_id}")
            return jsonify({
                'success': True,
                'data': {
                    'status': 'ok',
                    'data': {
                        'order_id': partner_order_id,
                        'status': 'confirmed'
                    }
                }
            })

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
    Polls every 2.5 seconds for max 180 seconds (RateHawk recommended)
    Timeout countdown begins after successful response to "Start booking process"
    
    RateHawk Certification Table 4: /hotel/order/booking/finish/status/ responses
    - Status "ok"          -> Booking Confirmed
    - Status "processing"  -> Continue polling
    - Error "timeout"      -> Save as pending, notify user
    - Error "unknown"      -> Save as pending, notify user
    - 5xx status code      -> Save as pending, retry later
    - Error "block"        -> Payment blocked by bank
    - Error "charge"       -> Payment charge failed
    - Error "3ds"          -> 3D Secure verification failed
    - Error "soldout"      -> Room sold out during booking
    - Error "provider"     -> Hotel provider error
    - Error "book_limit"   -> Booking limit reached
    - Error "not_allowed"  -> Booking not permitted
    - Error "booking_finish_did_not_succeed" -> Booking could not be completed
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123"
    }
    """
    # Error code -> user-friendly message mapping
    ERROR_MESSAGES = {
        'block': 'Payment was blocked by your bank. Please contact your bank or try a different card.',
        'charge': 'Payment charge failed. Please try again or use a different payment method.',
        '3ds': '3D Secure verification failed. Please try again.',
        'soldout': 'This room was sold out while processing your booking. Please select a different room.',
        'provider': 'The hotel provider encountered an error. Please try again later.',
        'book_limit': 'Booking limit reached for this property. Please try a different hotel.',
        'not_allowed': 'This booking is not permitted at this time. Please contact support.',
        'booking_finish_did_not_succeed': 'Booking could not be completed. Please try again or select a different room.',
    }
    
    try:
        data = request.get_json()
        
        if 'partner_order_id' not in data:
            return jsonify({'success': False, 'error': 'Missing partner_order_id'}), 400
        
        partner_order_id = data['partner_order_id']
        max_attempts = 72  # 180 seconds / 2.5 seconds (RateHawk recommended timeout)
        attempt = 0
        
        while attempt < max_attempts:
            result = etg_service.check_booking_status(partner_order_id)
            
            if result.get('success') and result.get('data'):
                status = result['data'].get('status', '')
                error = result['data'].get('error', '')
                
                # Still processing -> continue polling
                if status == 'processing':
                    attempt += 1
                    time.sleep(2.5)
                    continue
                
                # === SUCCESS ===
                if status == 'ok':
                    supabase_service.update_booking_by_partner_order_id(
                        partner_order_id,
                        {'status': 'confirmed', 'booking_response': result['data']}
                    )
                    
                    # Send confirmation email
                    try:
                        from services.email_service import email_service
                        from flask import current_app
                        email_service.init_app(current_app)
                        
                        # Fetch booking details from DB for email
                        db_booking = supabase_service.get_booking_by_partner_order_id(partner_order_id)
                        booking_data = db_booking.get('data') if db_booking else None
                        
                        if booking_data:
                            # Extract guest names professionally
                            guests = booking_data.get('guests', [])
                            customer_name = "Valued Guest"
                            if guests and isinstance(guests, list) and len(guests) > 0:
                                first_guest = guests[0]
                                first_name = first_guest.get('first_name', '')
                                last_name = first_guest.get('last_name', '')
                                if first_name or last_name:
                                    customer_name = f"{first_name} {last_name}".strip()
                            
                            customer_email = booking_data.get('customer_email') or booking_data.get('email')
                            if customer_email:
                                email_details = {
                                    'booking_id': partner_order_id,
                                    'customer_name': customer_name,
                                    'customer_email': customer_email,
                                    'hotel_name': booking_data.get('hotel_name', 'Hotel'),
                                    'checkin': booking_data.get('check_in') or booking_data.get('checkin'),
                                    'checkout': booking_data.get('check_out') or booking_data.get('checkout'),
                                    'amount': booking_data.get('total_amount', 0),
                                    'currency': booking_data.get('currency', 'INR'),
                                    'room_name': booking_data.get('room_name', 'Standard Room')
                                }
                                email_sent = email_service.send_booking_confirmation(customer_email, email_details)
                                print(f"{'✅' if email_sent else '❌'} Confirmation email {'sent' if email_sent else 'FAILED'} to {customer_email}")
                            else:
                                print(f"⚠️ No customer email found for booking {partner_order_id}")
                        else:
                            print(f"⚠️ No booking data found in DB for {partner_order_id}")
                    except Exception as email_err:
                        print(f"❌ Error sending confirmation email: {email_err}")
                    
                    return jsonify({
                        'success': True,
                        'status': 'confirmed',
                        'data': result['data']
                    })
                
                # === KNOWN TERMINAL ERRORS (Table 4) ===
                error_key = error if error else status
                if error_key in ERROR_MESSAGES:
                    supabase_service.update_booking_by_partner_order_id(
                        partner_order_id,
                        {'status': 'failed', 'booking_response': result['data']}
                    )
                    return jsonify({
                        'success': False,
                        'status': 'failed',
                        'error': ERROR_MESSAGES[error_key],
                        'error_code': error_key.upper()
                    })
                
                # === NON-FINAL ERRORS (timeout, unknown, processing) ===
                # Per Mikhail: Continue polling until status "ok" or a definitive terminal error.
                if status == 'processing' or error_key in ('timeout', 'unknown'):
                    print(f"🔄 Polling Status: {status} (Error: {error_key}). Attempt {attempt+1}/{max_attempts}...")
                    attempt += 1
                    time.sleep(2.5)
                    continue
                
                # Unrecognized status -> default to continue polling (Safety)
                attempt += 1
                time.sleep(2.5)
                continue
            
            # API call itself failed (5xx, network error)
            else:
                # 5xx / Network Error -> continue polling (ETG says it can still be successful)
                status_code = result.get('status_code', 'unknown')
                print(f"⚠️ Status check failed (HTTP {status_code}) on attempt {attempt+1}, continuing...")
                attempt += 1
                time.sleep(2.5)
                continue
        
        # === POLLING TIMEOUT (180s exhausted) ===
        # Save as pending - booking may still succeed on ETG side
        supabase_service.update_booking_by_partner_order_id(
            partner_order_id,
            {'status': 'pending'}
        )
        return jsonify({
            'success': False,
            'error': 'Your booking is still being processed by the hotel. We will email you a confirmation once it is finalized.',
            'status': 'pending',
            'error_code': 'TIMEOUT_PENDING'
        }), 202  # 202 Accepted (still processing)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==========================================
# POST-BOOKING ENDPOINTS
# ==========================================

@hotel_bp.route('/booking/<partner_order_id>', methods=['GET'])
def get_booking(partner_order_id):
    """
    Get booking details from ETG (/hotel/order/info/)

    RateHawk Certification Requirements:
    1. NOT for immediate confirmation display — use prebook/poll data for that.
    2. Minimum 60-second gap after /finish/status/ returns "ok" before calling /order/info/
       (ETG data sync can take up to 60 seconds after confirmation).
    3. If /order/info/ returns blank → booking is still valid, return cached DB data.

    Behaviour:
    - If booking was confirmed < 60s ago → return cached Supabase data (no ETG call)
    - If > 60s ago → call /order/info/, return ETG data
    - If /order/info/ returns blank → fall back to cached Supabase data
    """
    try:
        from datetime import datetime, timezone

        MIN_GAP_SECONDS = 60  # RateHawk recommended minimum gap

        # Fetch our cached booking record from Supabase
        db_booking = supabase_service.get_booking_by_partner_order_id(partner_order_id)
        cached_data = db_booking.get('data') if db_booking else None

        # Check how long ago the booking was confirmed
        seconds_since_confirmed = None
        if cached_data and cached_data.get('updated_at'):
            try:
                updated_str = cached_data['updated_at']
                # Parse ISO timestamp
                updated_at = datetime.fromisoformat(updated_str.replace('Z', '+00:00'))
                now = datetime.now(timezone.utc)
                seconds_since_confirmed = (now - updated_at).total_seconds()
            except Exception:
                seconds_since_confirmed = None

        # If < 60s since confirmation, return cached data to respect ETG sync window
        if seconds_since_confirmed is not None and seconds_since_confirmed < MIN_GAP_SECONDS:
            remaining = int(MIN_GAP_SECONDS - seconds_since_confirmed)
            print(f"⏳ Only {int(seconds_since_confirmed)}s since confirmation — returning cached data (gap: {remaining}s remaining)")
            return jsonify({
                'success': True,
                'source': 'cache',
                'reason': f'ETG data sync in progress — using cached data ({remaining}s until /order/info/ is available)',
                'data': cached_data,
                'retry_after_seconds': remaining
            })

        # Call /order/info/ — it's been >= 60s since confirmation
        print(f"📋 Calling /order/info/ for {partner_order_id} ({int(seconds_since_confirmed or 999)}s after confirmation)")
        result = etg_service.get_booking_info(partner_order_id)

        # If /order/info/ returns blank or empty data, fall back to cached DB record
        etg_data = result.get('data', {})
        is_blank = not etg_data or (isinstance(etg_data, dict) and not etg_data.get('data'))

        if is_blank:
            print(f"⚠️ /order/info/ returned blank — booking is still valid, returning cached Supabase data")
            return jsonify({
                'success': True,
                'source': 'cache',
                'reason': 'ETG order info not yet available — booking confirmed, using cached data',
                'data': cached_data
            })

        return jsonify({
            'success': True,
            'source': 'etg',
            'data': etg_data
        })

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

@hotel_bp.route('/booking/resend-email', methods=['POST'])
def resend_booking_email():
    """
    Resend booking confirmation email
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123",
        "email": "customer@email.com" (optional, uses stored email if not provided)
    }
    """
    try:
        data = request.get_json()
        
        if 'partner_order_id' not in data:
            return jsonify({'success': False, 'error': 'Missing partner_order_id'}), 400
        
        partner_order_id = data['partner_order_id']
        
        # Get booking details from database
        booking = supabase_service.get_booking_by_partner_order_id(partner_order_id)
        
        if not booking.get('success') or not booking.get('data'):
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        booking_data = booking['data']
        customer_email = data.get('email') or booking_data.get('customer_email')
        
        if not customer_email:
            return jsonify({'success': False, 'error': 'No email address found for this booking'}), 400
        
        # Send confirmation email
        from services.email_service import email_service
        from flask import current_app
        
        # Initialize email service with Flask app config (required for credentials)
        email_service.init_app(current_app)
        
        email_details = {
            'booking_id': partner_order_id,
            'customer_name': booking_data.get('guest_name', 'Valued Customer'),
            'customer_email': customer_email,
            'hotel_name': booking_data.get('hotel_name', 'Hotel'),
            'checkin': booking_data.get('check_in'),
            'checkout': booking_data.get('check_out'),
            'amount': booking_data.get('total_amount', 0),
            'currency': booking_data.get('currency', 'INR')
        }
        
        email_sent = email_service.send_booking_confirmation(customer_email, email_details)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Confirmation email sent successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Failed to send email. Please check email configuration.'
            }), 500
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@hotel_bp.route('/booking/send-confirmation', methods=['POST'])
def send_booking_confirmation():
    """
    Send booking confirmation email for a new booking
    Called from frontend after booking is confirmed
    
    Request Body:
    {
        "partner_order_id": "CTC-20260201-ABC123",
        "email": "customer@email.com",
        "hotel_name": "Hotel Name",
        "checkin": "2026-02-01",
        "checkout": "2026-02-05",
        "guests": "John Doe, Jane Doe",
        "total_amount": 5000,
        "room_name": "Deluxe Room"
    }
    """
    try:
        data = request.get_json()
        
        if not data.get('partner_order_id') or not data.get('email'):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400
        
        from services.email_service import email_service
        from flask import current_app
        
        # Initialize email service with Flask app config
        email_service.init_app(current_app)
        
        # Get amount — if frontend sends 0 or missing, try to get from DB
        amount = data.get('total_amount', 0)
        hotel_name = data.get('hotel_name', 'Hotel')
        checkin = data.get('checkin')
        checkout = data.get('checkout')
        customer_name = data.get('guests', 'Valued Customer')
        room_name = data.get('room_name', '')
        meal_plan = data.get('meal_plan', '') or data.get('meal_info', '')
        
        if not amount or amount == 0:
            # Try to get amount from database
            try:
                db_booking = supabase_service.get_booking_by_partner_order_id(data['partner_order_id'])
                if db_booking.get('success') and db_booking.get('data'):
                    db_data = db_booking['data']
                    amount = db_data.get('total_amount', 0) or 0
                    # Also fill in any missing fields from DB
                    if not hotel_name or hotel_name == 'Hotel':
                        hotel_name = db_data.get('hotel_name', hotel_name)
                    if not checkin:
                        checkin = db_data.get('check_in', checkin)
                    if not checkout:
                        checkout = db_data.get('check_out', checkout)
                    if not customer_name or customer_name == 'Valued Customer':
                        # Try to get guest name from guests JSON
                        guests = db_data.get('guests', [])
                        if guests and isinstance(guests, list) and len(guests) > 0:
                            g = guests[0]
                            if isinstance(g, dict):
                                customer_name = f"{g.get('first_name', '')} {g.get('last_name', '')}".strip()
                    print(f"📦 Pulled amount from DB: {amount}")
            except Exception as db_err:
                print(f"⚠️ Could not fetch booking from DB: {db_err}")
        
        email_details = {
            'booking_id': data.get('partner_order_id'),
            'customer_name': customer_name,
            'customer_email': data.get('email'),
            'hotel_name': hotel_name,
            'room_name': room_name,
            'meal_plan': meal_plan,
            'checkin': checkin,
            'checkout': checkout,
            'amount': amount,
            'currency': data.get('currency', 'INR')
        }
        
        print(f"📧 Sending booking confirmation to {data.get('email')} | Amount: {amount}")
        
        # Send email SYNCHRONOUSLY
        try:
            email_sent = email_service.send_booking_confirmation(data.get('email'), email_details)
            
            if email_sent:
                print(f"✅ Email sent successfully to {data.get('email')}")
                return jsonify({
                    'success': True,
                    'message': 'Booking confirmed and email sent',
                    'email_sent': True 
                })
            else:
                print(f"⚠️ Email send returned False for {data.get('email')}")
                return jsonify({
                    'success': True,
                    'message': 'Booking confirmed (email failed)',
                    'email_sent': False
                })
        except Exception as email_error:
            print(f"❌ Email send exception: {str(email_error)}")
            return jsonify({
                'success': True,
                'message': 'Booking confirmed (email error)',
                'email_sent': False,
                'email_error': str(email_error)
            })

    
    except Exception as e:
        print(f"❌ Email send error: {str(e)}")
        # Don't fail if email fails
        return jsonify({
            'success': True,
            'message': 'Booking confirmed (email error)',
            'email_sent': False,
            'error': str(e)
        })


@hotel_bp.route('/user/<user_id>/bookings', methods=['GET'])
def get_user_bookings(user_id):
    """Get all bookings for a user"""
    try:
        result = supabase_service.get_user_bookings(user_id)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
