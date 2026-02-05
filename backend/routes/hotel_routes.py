"""
C2C Journeys - Hotel Routes
API routes for hotel search and booking
"""
from flask import Blueprint, request, jsonify
from services.etg_service import etg_service
from services.supabase_service import supabase_service
from services.google_maps_service import google_maps_service
import time

hotel_bp = Blueprint('hotels', __name__, url_prefix='/api/hotels')


# ==========================================
# DEBUG ENDPOINT (Temporary) - v1.3
# ==========================================

@hotel_bp.route('/debug/email-test', methods=['GET'])
def debug_email_test():
    """Test email configuration and connectivity"""
    try:
        from flask import current_app
        import smtplib
        import socket
        import ssl
        
        # Get config
        server = current_app.config.get('MAIL_SERVER')
        port = int(current_app.config.get('MAIL_PORT', 465))
        username = current_app.config.get('MAIL_USERNAME')
        # Mask password
        password = current_app.config.get('MAIL_PASSWORD')
        password_masked = f"{password[:2]}...{password[-2:]}" if password else "None"
        use_ssl = current_app.config.get('MAIL_USE_SSL', True)
        resend_api_key = current_app.config.get('RESEND_API_KEY')
        
        # Check os.environ directly for deeper diagnosis
        import os as os_lib
        env_resend_key = os_lib.getenv('RESEND_API_KEY')
        env_resend_masked = f"{env_resend_key[:5]}...{env_resend_key[-5:]}" if env_resend_key else "None"
        
        results = {
            "config": {
                "server": server,
                "port": port,
                "username": username,
                "password_configured": bool(password),
                "ssl": use_ssl,
                "resend_api_key_configured_in_flask": bool(resend_api_key),
                "resend_api_key_found_in_os_environ": bool(env_resend_key),
                "os_environ_key_masked": env_resend_masked
            },
            "steps": []
        }

        # Step 0: Test Resend API if configured
        if resend_api_key:
            try:
                results['steps'].append("Testing Resend API connectivity...")
                import resend
                resend.api_key = resend_api_key
                
                # ATTEMPT A REAL TEST SEND
                results['steps'].append(f"Attempting test email via Resend to {username}...")
                test_send = resend.Emails.send({
                    "from": f"C2C Debug <onboarding@resend.dev>",
                    "to": username,
                    "subject": "C2C Journeys - Email Test",
                    "text": "This is a test email from your Render deployment to verify the Resend API."
                })
                results['steps'].append(f"✅ Resend API Test Sent (ID: {test_send.get('id')})")
                results['steps'].append("👉 Note: Using 'onboarding@resend.dev' works for testing even if your domain isn't verified.")
            except Exception as e:
                results['steps'].append(f"❌ Resend API Test Failed: {str(e)}")
                results['steps'].append("👉 Common cause: Invalid API key or unverified domain/email.")
        
        # Step 1: DNS Resolution
        try:
            results['steps'].append(f"Resolving {server}...")
            ip = socket.gethostbyname(server)
            results['steps'].append(f"✅ Resolved to {ip}")
        except Exception as e:
            results['steps'].append(f"❌ DNS Resolution failed: {str(e)}")
            # Don't return yet if Resend is configured, as SMTP might just be a fallback
            if not resend_api_key:
                return jsonify(results), 500
            
        # Step 2: Connection
        try:
            results['steps'].append(f"Connecting to {server}:{port}...")
            # Create a socket connection first to test reachability
            sock = socket.create_connection((server, port), timeout=10)
            results['steps'].append("✅ TCP Connection successful")
            sock.close()
        except Exception as e:
            results['steps'].append(f"❌ Connection failed: {str(e)}")
            if not resend_api_key:
                return jsonify(results), 500

        # Step 3: SMTP Handshake
        try:
            results['steps'].append("Starting SMTP session...")
            
            if use_ssl:
                results['steps'].append("Using SMTP_SSL...")
                smtp = smtplib.SMTP_SSL(server, port, timeout=10)
            else:
                results['steps'].append("Using SMTP (TLS)...")
                smtp = smtplib.SMTP(server, port, timeout=10)
                smtp.starttls()
            
            results['steps'].append("✅ SMTP Connected & Hello received")
            
            # Step 4: Login
            results['steps'].append(f"Attempting login as {username}...")
            smtp.login(username, password)
            results['steps'].append("✅ Login successful")
            
            smtp.quit()
            
            return jsonify({
                "success": True, 
                "message": "Email system is fully operational!",
                "debug_info": results
            })
            
        except smtplib.SMTPAuthenticationError as e:
             results['steps'].append(f"❌ Authentication Failed: {str(e)}")
             results['steps'].append("👉 Check your MAIL_USERNAME and MAIL_PASSWORD")
        except Exception as e:
            results['steps'].append(f"❌ SMTP Error: {str(e)}")
            
        # If we got here, maybe Resend worked but SMTP failed
        if resend_api_key and "Resend API key configured" in str(results['steps']):
            return jsonify({
                "success": True,
                "message": "Email system operational via Resend API (SMTP failed but it's a fallback)",
                "debug_info": results
            })

        return jsonify({
            "success": False,
            "error": "Email Test Failed",
            "debug_info": results
        }), 500
        
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
        
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', [])
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
    # NOTE: RateHawk Sandbox only supports limited destinations (Paris, Dubai, etc.)
    # For production, request RateHawk to activate your production API credentials
    POPULAR_DESTINATIONS = {
        # SANDBOX SUPPORTED DESTINATIONS (Real hotel data available)
        'paris': {'latitude': 48.8566, 'longitude': 2.3522, 'region_id': 2734, 'name': 'Paris', 'sandbox': True},
        'dubai': {'latitude': 25.2048, 'longitude': 55.2708, 'region_id': 6053839, 'name': 'Dubai', 'sandbox': True},
        'moscow': {'latitude': 55.7558, 'longitude': 37.6173, 'region_id': 2395, 'name': 'Moscow', 'sandbox': True},
        
        # INDIAN DESTINATIONS (Will need production API for real data)
        # These region IDs are for production API - sandbox will return empty
        'goa': {'latitude': 15.2993, 'longitude': 74.1240, 'region_id': 6308855, 'name': 'Goa', 'sandbox': False},
        'delhi': {'latitude': 28.6139, 'longitude': 77.2090, 'region_id': 6308838, 'name': 'New Delhi', 'sandbox': False},
        'mumbai': {'latitude': 19.0760, 'longitude': 72.8777, 'region_id': 6308862, 'name': 'Mumbai', 'sandbox': False},
        'bangalore': {'latitude': 12.9716, 'longitude': 77.5946, 'region_id': 6308822, 'name': 'Bangalore', 'sandbox': False},
        'bengaluru': {'latitude': 12.9716, 'longitude': 77.5946, 'region_id': 6308822, 'name': 'Bangalore', 'sandbox': False},
        'chennai': {'latitude': 13.0827, 'longitude': 80.2707, 'region_id': 6308834, 'name': 'Chennai', 'sandbox': False},
        'kolkata': {'latitude': 22.5726, 'longitude': 88.3639, 'region_id': 6308856, 'name': 'Kolkata', 'sandbox': False},
        'jaipur': {'latitude': 26.9124, 'longitude': 75.7873, 'region_id': 6308849, 'name': 'Jaipur', 'sandbox': False},
        'udaipur': {'latitude': 24.5854, 'longitude': 73.7125, 'region_id': 6308883, 'name': 'Udaipur', 'sandbox': False},
        'agra': {'latitude': 27.1767, 'longitude': 78.0081, 'region_id': 6308815, 'name': 'Agra', 'sandbox': False},
        'hyderabad': {'latitude': 17.3850, 'longitude': 78.4867, 'region_id': 6308846, 'name': 'Hyderabad', 'sandbox': False},
        'pune': {'latitude': 18.5204, 'longitude': 73.8567, 'region_id': 6308870, 'name': 'Pune', 'sandbox': False},
        'kerala': {'latitude': 10.8505, 'longitude': 76.2711, 'region_id': 6308854, 'name': 'Kerala', 'sandbox': False},
        'kochi': {'latitude': 9.9312, 'longitude': 76.2673, 'region_id': 6308855, 'name': 'Kochi', 'sandbox': False},
        'manali': {'latitude': 32.2396, 'longitude': 77.1887, 'region_id': 6308859, 'name': 'Manali', 'sandbox': False},
        'shimla': {'latitude': 31.1048, 'longitude': 77.1734, 'region_id': 6308876, 'name': 'Shimla', 'sandbox': False},
        'rishikesh': {'latitude': 30.0869, 'longitude': 78.2676, 'region_id': 6308872, 'name': 'Rishikesh', 'sandbox': False},
        'varanasi': {'latitude': 25.3176, 'longitude': 82.9739, 'region_id': 6308885, 'name': 'Varanasi', 'sandbox': False},
        'amritsar': {'latitude': 31.6340, 'longitude': 74.8723, 'region_id': 6308818, 'name': 'Amritsar', 'sandbox': False},
        'darjeeling': {'latitude': 27.0410, 'longitude': 88.2663, 'region_id': 6308837, 'name': 'Darjeeling', 'sandbox': False},
        'ooty': {'latitude': 11.4102, 'longitude': 76.6950, 'region_id': 6308866, 'name': 'Ooty', 'sandbox': False},
    }
    
    try:
        data = request.get_json()
        
        required = ['destination', 'checkin', 'checkout', 'adults']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        destination = data['destination'].lower().strip()
        region_id = None
        location_name = data['destination']
        is_sandbox_supported = False
        
        print(f"🔍 Hotel Search Request: {data['destination']}")
        
        # Step 1: Check if destination matches a known sandbox-supported location
        for key, loc_data in POPULAR_DESTINATIONS.items():
            if key in destination or destination in key:
                region_id = loc_data.get('region_id')
                location_name = loc_data['name']
                is_sandbox_supported = loc_data.get('sandbox', False)
                print(f"📍 Matched destination: {location_name}, Sandbox: {is_sandbox_supported}")
                break
        
        # Step 2: For non-sandbox destinations, skip RateHawk and go to Google directly
        # This avoids unnecessary API calls that will return empty results
        if region_id and not is_sandbox_supported:
            print(f"⚠️ {location_name} is not sandbox-supported, using Google Places")
            google_hotels = search_hotels_via_google(data['destination'], data['checkin'], data['checkout'])
            
            if google_hotels:
                print(f"✅ Found {len(google_hotels)} hotels via Google Places for {location_name}")
                return jsonify({
                    'success': True,
                    'data': {'hotels': google_hotels},
                    'location': {'name': location_name},
                    'hotels_count': len(google_hotels),
                    'real_data': True,
                    'source': 'google_places'
                })
        
        # Step 3: If sandbox-supported, try RateHawk first
        if region_id and is_sandbox_supported:
            print(f"🏨 Searching RateHawk for sandbox destination: {location_name}")
            
            guests = etg_service.format_guests_for_search(
                adults=data['adults'],
                children_ages=data.get('children_ages', [])
            )
            
            # Search using region API with sandbox-compatible parameters
            result = etg_service.search_by_region(
                region_id=region_id,
                checkin=data['checkin'],
                checkout=data['checkout'],
                guests=guests,
                currency='USD',
                residency=data.get('residency', 'gb')  # Use user selected residency
            )
            
            # Check if RateHawk returned hotels
            if result.get('success') and result.get('data'):
                inner_data = result['data'].get('data', result['data'])
                etg_hotels = inner_data.get('hotels', [])
                
                if etg_hotels and len(etg_hotels) > 0:
                    print(f"✅ Found {len(etg_hotels)} hotels via RateHawk for {location_name}")
                    transformed_hotels = transform_etg_hotels(etg_hotels, location_name)
                    
                    # Add ₹1 TEST hotel at the beginning for payment testing (only in dev mode)
                    import os
                    if os.getenv('FLASK_DEBUG', 'False').lower() == 'true':
                        test_hotel = {
                            'id': 'test_payment_1_rupee',
                            'name': '💳 PAYMENT TEST - ₹1 Only Hotel',
                            'star_rating': 5,
                            'guest_rating': 5.0,
                            'review_count': 999,
                            'address': f'{location_name} - Test Hotel for Razorpay/UPI Verification',
                            'image': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600',
                            'price': 1,
                            'original_price': 5000,
                            'currency': 'INR',
                            'amenities': ['wifi', 'pool', 'parking', 'restaurant', 'spa', 'gym'],
                            'meal_plan': 'breakfast',
                            'rates': [{'book_hash': 'test_hash_1_rupee', 'room_name': 'Test Room - Razorpay Verification', 'price': 1}],
                            'discount': 99
                        }
                        transformed_hotels.insert(0, test_hotel)
                    
                    return jsonify({
                        'success': True,
                        'data': {'hotels': transformed_hotels},
                        'location': {'name': location_name, 'region_id': region_id},
                        'hotels_count': len(transformed_hotels),
                        'real_data': True,
                        'source': 'ratehawk'
                    })
                else:
                    print(f"⚠️ RateHawk returned 0 hotels for {location_name}, trying Google")
        
        # Step 4: If not in predefined list, try ETG suggest API to find the region
        if not region_id:
            print(f"🔎 Trying RateHawk suggest API for: {data['destination']}")
            suggest_result = etg_service.suggest(data['destination'])
            if suggest_result.get('success') and suggest_result.get('data'):
                inner_data = suggest_result['data'].get('data', suggest_result['data'])
                regions = inner_data.get('regions', [])
                if regions:
                    region_id = regions[0].get('id')
                    location_name = regions[0].get('name', data['destination'])
                    is_sandbox_supported = True
                    print(f"✅ Found region via suggest API: {location_name} (ID: {region_id})")
                    
                    # Try searching with the found region
                    guests = etg_service.format_guests_for_search(
                        adults=data['adults'],
                        children_ages=data.get('children_ages', [])
                    )
                    
                    result = etg_service.search_by_region(
                        region_id=region_id,
                        checkin=data['checkin'],
                        checkout=data['checkout'],
                        guests=guests,
                        currency='USD',
                        residency='gb'
                    )
                    
                    if result.get('success') and result.get('data'):
                        search_data = result['data'].get('data', result['data'])
                        etg_hotels = search_data.get('hotels', [])
                        
                        if etg_hotels and len(etg_hotels) > 0:
                            print(f"✅ Found {len(etg_hotels)} hotels via RateHawk suggest")
                            transformed_hotels = transform_etg_hotels(etg_hotels, location_name)
                            return jsonify({
                                'success': True,
                                'data': {'hotels': transformed_hotels},
                                'location': {'name': location_name, 'region_id': region_id},
                                'hotels_count': len(transformed_hotels),
                                'real_data': True,
                                'source': 'ratehawk'
                            })
        
        # Step 5: Final fallback to Google Places API
        print(f"🌐 Falling back to Google Places for: {data['destination']}")
        google_hotels = search_hotels_via_google(data['destination'], data['checkin'], data['checkout'])
        
        if google_hotels:
            print(f"✅ Found {len(google_hotels)} hotels via Google Places")
            return jsonify({
                'success': True,
                'data': {'hotels': google_hotels},
                'location': {'name': location_name},
                'hotels_count': len(google_hotels),
                'real_data': True,
                'source': 'google_places'
            })
        
        # All methods failed
        print(f"❌ No hotels found for {data['destination']}")
        return jsonify({
            'success': False,
            'error': f"Could not find hotels for '{data['destination']}'. Please try Paris, Dubai, or Moscow for best results.",
            'sandbox_mode': True,
            'supported_destinations': ['Paris', 'Moscow', 'Dubai']
        }), 400
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def transform_etg_hotels(etg_hotels, destination):
    """Transform ETG hotel response to frontend format"""
    transformed = []
    
    # Sample hotel images for demo
    hotel_images = [
        'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=600',
        'https://images.unsplash.com/photo-1520250497591-112f2f40a3f4?w=600',
        'https://images.unsplash.com/photo-1571896349842-33c89424de2d?w=600',
        'https://images.unsplash.com/photo-1582719508461-905c673771fd?w=600',
        'https://images.unsplash.com/photo-1564501049412-61c2a3083791?w=600',
        'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=600',
        'https://images.unsplash.com/photo-1542314831-068cd1dbfeeb?w=600',
        'https://images.unsplash.com/photo-1549294413-26f195471c9e?w=600',
    ]
    
    for idx, hotel in enumerate(etg_hotels):
        rates = hotel.get('rates', [])
        
        # Get lowest price from rates
        lowest_price = 0
        best_rate = None
        meal_plan = 'nomeal'
        
        for rate in rates:
            payment_types = rate.get('payment_options', {}).get('payment_types', [])
            for pt in payment_types:
                amount = float(pt.get('amount', 0))
                # Apply 15% Commission
                amount = amount * 1.15
                
                if lowest_price == 0 or amount < lowest_price:
                    lowest_price = amount
                    best_rate = rate
                    meal_plan = rate.get('meal', 'nomeal')
        
        # Extract star rating from rg_ext
        rg_ext = rates[0].get('rg_ext', {}) if rates else {}
        star_rating = rg_ext.get('class', 3)
        
        # Create transformed hotel object
        transformed_hotel = {
            'id': hotel.get('id', f'hotel_{idx}'),
            'hid': hotel.get('hid'),
            'name': hotel.get('name', best_rate.get('room_name', 'Hotel') if best_rate else 'Hotel'),
            'star_rating': star_rating if star_rating else 4,
            'guest_rating': round(3.5 + (star_rating or 3) * 0.3, 1),  # Estimated rating
            'review_count': 50 + (idx * 23) % 500,  # Demo review count
            'address': destination.title(),
            'image': hotel_images[idx % len(hotel_images)],
            'price': round(lowest_price, 2),
            'original_price': round(lowest_price * 1.25, 2),  # Fake higher price
            'currency': 'USD',
            'amenities': extract_amenities(rates),
            'meal_plan': meal_plan,
            'discount': 15,
            'rates': [
                {
                    'book_hash': rate.get('match_hash', ''),
                    'room_name': rate.get('room_name', rate.get('room_data_trans', {}).get('main_name', 'Standard Room')),
                    'price': round(float(rate.get('payment_options', {}).get('payment_types', [{}])[0].get('amount', 0)) * 1.15, 2),
                    'meal': rate.get('meal', 'nomeal')
                }
                for rate in rates[:3]  # Limit to 3 rates per hotel
            ] if rates else []
        }
        
        transformed.append(transformed_hotel)
    
    return transformed


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


def search_hotels_via_google(destination: str, checkin: str, checkout: str) -> list:
    """
    Search for hotels using Google Places API as fallback
    Returns real hotel data for ANY destination worldwide
    
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
        
        # Sample hotel images for variety
        hotel_images = [
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
            # Real prices would require additional API or booking data
            base_price = 2000 + (rating * 1500) + (idx * 200)
            
            hotel = {
                'id': f"google_{place.get('place_id', idx)}",
                'google_place_id': place.get('place_id'),
                'name': place.get('name', 'Hotel'),
                'star_rating': star_rating,
                'guest_rating': rating,
                'review_count': review_count,
                'address': place.get('address', destination),
                'image': hotel_images[idx % len(hotel_images)],
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


@hotel_bp.route('/policies/<hotel_id>', methods=['GET'])
def get_hotel_policies(hotel_id):
    """
    Get hotel policies from static data
    Returns metapolicy_extra_info and metapolicy_struct fields
    
    IMPORTANT: policy_struct is deprecated and should be ignored (per RateHawk)
    """
    try:
        # Fetch static hotel data
        result = etg_service.get_hotel_static(hotel_id)
        
        if not result.get('success'):
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to fetch hotel static data')
            }), 400
        
        hotel_data = result.get('data', {})
        if isinstance(hotel_data, dict) and hotel_data.get('data'):
            hotel_data = hotel_data['data']
        
        # Extract policy information
        # NOTE: policy_struct is deprecated - we only use metapolicy_struct and metapolicy_extra_info
        policies = {
            'metapolicy_struct': hotel_data.get('metapolicy_struct', {}),
            'metapolicy_extra_info': hotel_data.get('metapolicy_extra_info', {}),
            # Additional useful info
            'check_in_time': hotel_data.get('check_in_time'),
            'check_out_time': hotel_data.get('check_out_time'),
        }
        
        # Format policies for frontend display
        formatted_policies = format_hotel_policies(policies)
        
        return jsonify({
            'success': True,
            'data': {
                'raw_policies': policies,
                'formatted_policies': formatted_policies
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def format_hotel_policies(policies):
    """
    Format raw policy data into user-friendly display format
    
    metapolicy_struct contains structured policy information like:
    - check_in, check_out times
    - add_fee (extra beds, cots, etc.)
    - children policies
    - pets policies
    - shuttle services
    - deposit requirements
    - internet policies
    - parking policies
    
    metapolicy_extra_info contains additional policy text
    """
    formatted = {
        'check_in_out': [],
        'children': [],
        'pets': [],
        'payments': [],
        'internet': [],
        'parking': [],
        'meals': [],
        'extra_beds': [],
        'other': []
    }
    
    metapolicy = policies.get('metapolicy_struct', {})
    extra_info = policies.get('metapolicy_extra_info', {})
    
    # Check-in/Check-out times
    if policies.get('check_in_time'):
        formatted['check_in_out'].append({
            'icon': 'fa-sign-in-alt',
            'label': 'Check-in Time',
            'value': policies['check_in_time']
        })
    if policies.get('check_out_time'):
        formatted['check_in_out'].append({
            'icon': 'fa-sign-out-alt',
            'label': 'Check-out Time',
            'value': policies['check_out_time']
        })
    
    # Process metapolicy_struct
    if metapolicy:
        # Children policies
        children_policy = metapolicy.get('children')
        if children_policy:
            if isinstance(children_policy, list):
                for item in children_policy:
                    formatted['children'].append({
                        'icon': 'fa-child',
                        'label': 'Children Policy',
                        'value': item.get('text', str(item))
                    })
            elif isinstance(children_policy, dict):
                for key, value in children_policy.items():
                    formatted['children'].append({
                        'icon': 'fa-child',
                        'label': f'Children - {key.replace("_", " ").title()}',
                        'value': str(value)
                    })
        
        # Pets policy
        pets_policy = metapolicy.get('pets')
        if pets_policy:
            if isinstance(pets_policy, list):
                for item in pets_policy:
                    formatted['pets'].append({
                        'icon': 'fa-paw',
                        'label': 'Pets Policy',
                        'value': item.get('text', str(item))
                    })
            elif isinstance(pets_policy, dict):
                allowed = pets_policy.get('pets_allowed', pets_policy.get('allowed'))
                if allowed is not None:
                    formatted['pets'].append({
                        'icon': 'fa-paw',
                        'label': 'Pets',
                        'value': 'Pets Allowed' if allowed else 'No Pets Allowed'
                    })
                if pets_policy.get('fee'):
                    formatted['pets'].append({
                        'icon': 'fa-money-bill',
                        'label': 'Pet Fee',
                        'value': str(pets_policy.get('fee'))
                    })
            elif isinstance(pets_policy, str):
                formatted['pets'].append({
                    'icon': 'fa-paw',
                    'label': 'Pets Policy',
                    'value': pets_policy
                })
        
        # Internet policy
        internet_policy = metapolicy.get('internet')
        if internet_policy:
            if isinstance(internet_policy, list):
                for item in internet_policy:
                    formatted['internet'].append({
                        'icon': 'fa-wifi',
                        'label': 'Internet',
                        'value': item.get('text', str(item))
                    })
            elif isinstance(internet_policy, dict):
                for key, value in internet_policy.items():
                    formatted['internet'].append({
                        'icon': 'fa-wifi',
                        'label': f'Internet - {key.replace("_", " ").title()}',
                        'value': str(value)
                    })
        
        # Parking policy
        parking_policy = metapolicy.get('parking')
        if parking_policy:
            if isinstance(parking_policy, list):
                for item in parking_policy:
                    formatted['parking'].append({
                        'icon': 'fa-parking',
                        'label': 'Parking',
                        'value': item.get('text', str(item))
                    })
            elif isinstance(parking_policy, dict):
                for key, value in parking_policy.items():
                    formatted['parking'].append({
                        'icon': 'fa-parking',
                        'label': f'Parking - {key.replace("_", " ").title()}',
                        'value': str(value)
                    })
        
        # Deposit/Payment policies
        deposit = metapolicy.get('deposit')
        if deposit:
            if isinstance(deposit, list):
                for item in deposit:
                    formatted['payments'].append({
                        'icon': 'fa-credit-card',
                        'label': 'Deposit',
                        'value': item.get('text', str(item))
                    })
            elif isinstance(deposit, dict):
                formatted['payments'].append({
                    'icon': 'fa-credit-card',
                    'label': 'Deposit Required',
                    'value': f"Amount: {deposit.get('amount', 'Varies')}"
                })
        
        # Extra beds/cots
        add_fee = metapolicy.get('add_fee')
        if add_fee:
            if isinstance(add_fee, list):
                for item in add_fee:
                    formatted['extra_beds'].append({
                        'icon': 'fa-bed',
                        'label': 'Extra Bed/Cot',
                        'value': item.get('text', str(item))
                    })
            elif isinstance(add_fee, dict):
                for key, value in add_fee.items():
                    formatted['extra_beds'].append({
                        'icon': 'fa-bed',
                        'label': f'{key.replace("_", " ").title()}',
                        'value': str(value)
                    })
    
    # Process metapolicy_extra_info (additional text-based policies)
    if extra_info:
        if isinstance(extra_info, dict):
            for category, info in extra_info.items():
                if info:
                    # Map to appropriate category or put in 'other'
                    target_category = 'other'
                    icon = 'fa-info-circle'
                    
                    if 'child' in category.lower():
                        target_category = 'children'
                        icon = 'fa-child'
                    elif 'pet' in category.lower():
                        target_category = 'pets'
                        icon = 'fa-paw'
                    elif 'internet' in category.lower() or 'wifi' in category.lower():
                        target_category = 'internet'
                        icon = 'fa-wifi'
                    elif 'parking' in category.lower():
                        target_category = 'parking'
                        icon = 'fa-parking'
                    elif 'payment' in category.lower() or 'deposit' in category.lower():
                        target_category = 'payments'
                        icon = 'fa-credit-card'
                    elif 'meal' in category.lower() or 'breakfast' in category.lower():
                        target_category = 'meals'
                        icon = 'fa-utensils'
                    
                    if isinstance(info, list):
                        for item in info:
                            formatted[target_category].append({
                                'icon': icon,
                                'label': category.replace('_', ' ').title(),
                                'value': str(item)
                            })
                    else:
                        formatted[target_category].append({
                            'icon': icon,
                            'label': category.replace('_', ' ').title(),
                            'value': str(info)
                        })
    
    return formatted


# ==========================================
# ROOM GROUPS ENDPOINT (ETG Room Static Data)
# ==========================================

@hotel_bp.route('/room-groups/<hotel_id>', methods=['GET'])
def get_room_groups(hotel_id):
    """
    Get room groups from hotel static data for matching with rates
    
    This endpoint fetches room static data and returns room groups
    with images and amenities that can be matched to rates using
    the rg_ext.rg parameter.
    
    Matching Process:
    - Rate's rg_ext.rg (room group hash) -> room_groups[].rg_hash
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
        
        # 1. Fetch hotel rates
        rates_result = etg_service.get_hotel_page(
            hotel_id=data['hotel_id'],
            checkin=data['checkin'],
            checkout=data['checkout'],
            guests=guests,
            currency=data.get('currency', 'USD')
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
            
            # Build room groups lookup by rg_hash
            for rg in static_data.get('room_groups', []):
                rg_hash = rg.get('rg_hash')
                if rg_hash:
                    room_groups[rg_hash] = {
                        'name': rg.get('name', rg.get('room_name', '')),
                        'name_struct': rg.get('name_struct', {}),
                        'images': rg.get('images', []),
                        'room_amenities': rg.get('room_amenities', []),
                        'rg_hash': rg_hash
                    }
        
        # 3. Enrich rates with room group data
        rates_data = rates_result.get('data', {})
        if isinstance(rates_data, dict) and rates_data.get('data'):
            rates_data = rates_data['data']
        
        hotels = rates_data.get('hotels', [])
        enriched_hotels = []
        
        for hotel in hotels:
            enriched_rates = []
            for rate in hotel.get('rates', []):
                enriched_rate = enrich_rate_with_room_data(rate, room_groups)
                enriched_rates.append(enriched_rate)
            
            hotel['rates'] = enriched_rates
            enriched_hotels.append(hotel)
        
        return jsonify({
            'success': True,
            'data': {
                'hotels': enriched_hotels,
                'room_groups_count': len(room_groups)
            }
        })
    
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


def format_room_groups(room_groups):
    """
    Format room groups for frontend consumption
    
    Room groups contain:
    - rg_hash: Unique identifier to match with rate's rg_ext.rg
    - name: Room group name
    - images: Array of room images
    - room_amenities: Array of amenity codes
    """
    formatted = []
    
    for rg in room_groups:
        formatted_rg = {
            'rg_hash': rg.get('rg_hash', ''),
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
                formatted_rg['images'].append(img)
            elif isinstance(img, dict):
                # Handle different image format
                img_url = img.get('url', img.get('src', ''))
                if img_url:
                    formatted_rg['images'].append(img_url)
        
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
    Enrich a rate with room static data by matching rg_ext.rg with room group hash
    Also extracts tax data for proper display to customers
    
    Matching parameter: rg_ext.rg <-> room_groups[rg_hash]
    
    Tax handling:
    - tax_data.taxes contains all taxes
    - included_by_supplier: true = already in price
    - included_by_supplier: false = must be shown separately (paid at check-in)
    """
    enriched_rate = dict(rate)
    
    # Calculate Price with Commission
    # ETG returns NET price. We must add our markup.
    try:
        net_price = float(rate.get('payment_options', {}).get('payment_types', [{}])[0].get('amount', 0))
        sales_price = net_price * (1 + COMMISSION_PERCENT / 100)
        enriched_rate['price'] = round(sales_price, 2)
        enriched_rate['net_price'] = net_price  # Keep original for reference
        
        # Calculate original price (fake higher price for discount display)
        enriched_rate['original_price'] = round(sales_price * 1.25, 2)
    except Exception:
        enriched_rate['price'] = 0
    
    # Get rg_ext from rate (contains room group matching info)
    rg_ext = rate.get('rg_ext', {})
    rg_hash = rg_ext.get('rg')  # This is the room group hash for matching
    
    # Try to find matching room group
    room_data = room_groups.get(rg_hash, {})
    
    if room_data:
        # Add enriched room data
        enriched_rate['room_static'] = {
            'matched': True,
            'rg_hash': rg_hash,
            'room_name': room_data.get('name', ''),
            'images': room_data.get('images', [])[:5],  # Limit to 5 images
            'amenities': room_data.get('room_amenities', [])[:10]  # Limit to 10 amenities
        }
    else:
        # No match found - use rate's own data
        enriched_rate['room_static'] = {
            'matched': False,
            'rg_hash': rg_hash,
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
    
    # Extract cancellation policies
    # ETG API sends cancellation_penalties with:
    # - free_cancellation_before: timestamp for free cancellation deadline (UTC+0)
    # - policies: array of cancellation tiers with penalties
    cancellation_penalties = rate.get('cancellation_penalties', {})
    free_cancellation_before = cancellation_penalties.get('free_cancellation_before')
    policies = cancellation_penalties.get('policies', [])
    
    # Format cancellation info for frontend
    cancellation_info = extract_cancellation_info(free_cancellation_before, policies)
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
    
    return {
        'code': meal_code,
        'display_name': display_name,
        'has_breakfast': has_breakfast,
        'no_child_meal': no_child_meal,
        'includes_child': not no_child_meal
    }


def extract_cancellation_info(free_cancellation_before, policies):
    """
    Extract and format cancellation policy information
    
    Parameters:
    - free_cancellation_before: ISO timestamp for free cancellation deadline (UTC+0)
      - null means no free cancellation (non-refundable)
    - policies: array of cancellation tiers
    
    Returns formatted cancellation info for frontend display
    """
    cancellation_info = {
        'is_free_cancellation': free_cancellation_before is not None,
        'free_cancellation_before': free_cancellation_before,
        'free_cancellation_formatted': None,
        'policies': [],
        'summary': 'Non-refundable'
    }
    
    if free_cancellation_before:
        # Parse and format the deadline
        try:
            # Format: "2025-10-21T08:59:00"
            from datetime import datetime
            deadline = datetime.fromisoformat(free_cancellation_before.replace('Z', ''))
            
            # Format for display
            cancellation_info['free_cancellation_formatted'] = {
                'date': deadline.strftime('%d %b %Y'),  # e.g., "21 Oct 2025"
                'time': deadline.strftime('%H:%M'),     # e.g., "08:59"
                'datetime': deadline.strftime('%d %b %Y, %H:%M UTC'),  # Full format
                'iso': free_cancellation_before
            }
            
            cancellation_info['summary'] = f"Free cancellation until {deadline.strftime('%d %b %Y, %H:%M')} UTC"
        except Exception:
            # If parsing fails, use raw value
            cancellation_info['free_cancellation_formatted'] = {
                'date': free_cancellation_before,
                'time': '',
                'datetime': free_cancellation_before,
                'iso': free_cancellation_before
            }
            cancellation_info['summary'] = f"Free cancellation until {free_cancellation_before} UTC"
    
    # Process cancellation policies (tiers)
    for policy in policies:
        start_at = policy.get('start_at')
        end_at = policy.get('end_at')
        amount_show = policy.get('amount_show', '0')
        amount_charge = policy.get('amount_charge', '0')
        
        # Determine policy type
        if start_at is None and float(amount_show) == 0:
            # Free cancellation period
            policy_type = 'free'
        elif end_at is None:
            # Full penalty (no refund)
            policy_type = 'full_penalty'
        else:
            # Partial penalty
            policy_type = 'partial_penalty'
        
        formatted_policy = {
            'type': policy_type,
            'start_at': start_at,
            'end_at': end_at,
            'penalty_amount': amount_show,
            'penalty_amount_internal': amount_charge
        }
        
        # Format dates for display
        if start_at:
            try:
                from datetime import datetime
                start = datetime.fromisoformat(start_at.replace('Z', ''))
                formatted_policy['start_formatted'] = start.strftime('%d %b %Y, %H:%M UTC')
            except:
                formatted_policy['start_formatted'] = start_at
        
        if end_at:
            try:
                from datetime import datetime
                end = datetime.fromisoformat(end_at.replace('Z', ''))
                formatted_policy['end_formatted'] = end.strftime('%d %b %Y, %H:%M UTC')
            except:
                formatted_policy['end_formatted'] = end_at
        
        cancellation_info['policies'].append(formatted_policy)
    
    return cancellation_info


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
        
        result = etg_service.prebook(
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
        
        book_hash = data['book_hash']
        
        # Check for demo/test/google bookings - skip ETG API for these
        if book_hash.startswith('demo_') or book_hash.startswith('test_') or book_hash.startswith('google_'):
            # Generate local booking ID for demo/test bookings
            partner_order_id = etg_service.generate_partner_order_id()
            
            # Save demo booking to Supabase
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
                'status': 'confirmed',  # Demo bookings are auto-confirmed
                'booking_response': {'demo': True, 'message': 'Demo/Test booking created successfully'}
            }
            
            db_result = supabase_service.create_booking(booking_data)
            
            return jsonify({
                'success': True,
                'partner_order_id': partner_order_id,
                'booking_id': db_result.get('data', {}).get('id'),
                'demo': True,
                'message': 'Demo booking created successfully'
            })
        
        # For real ETG bookings, call prebook first to validate the hash
        print(f"📋 Calling prebook to validate hash: {book_hash[:50]}...")
        prebook_result = etg_service.prebook(book_hash)
        
        if not prebook_result.get('success'):
            error_msg = prebook_result.get('error', 'Unknown prebook error')
            print(f"❌ Prebook failed: {error_msg}")
            
            # Return user-friendly error message
            if '400' in str(error_msg) or 'Bad Request' in str(error_msg):
                return jsonify({
                    'success': False,
                    'error': 'This room rate has expired or is no longer available. Please go back and select a different room.',
                    'error_code': 'RATE_EXPIRED'
                }), 400
            
            return jsonify({
                'success': False,
                'error': f'Rate validation failed: {error_msg}',
                'error_code': 'PREBOOK_FAILED'
            }), 400
        
        print(f"✅ Prebook successful, proceeding with booking...")
        
        # Generate unique partner order ID
        partner_order_id = etg_service.generate_partner_order_id()
        
        # Get user IP
        user_ip = request.environ.get('HTTP_X_REAL_IP', request.remote_addr)
        
        # Create booking in ETG using the validated hash
        etg_result = etg_service.create_booking(
            book_hash=book_hash,
            partner_order_id=partner_order_id,
            guests=data['guests'],
            user_ip=user_ip
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
        "total_amount": 5000
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
        
        email_details = {
            'booking_id': data.get('partner_order_id'),
            'customer_name': data.get('guests', 'Valued Customer'),
            'customer_email': data.get('email'),
            'hotel_name': data.get('hotel_name', 'Hotel'),
            'checkin': data.get('checkin'),
            'checkout': data.get('checkout'),
            'amount': data.get('total_amount', 0),
            'currency': 'INR'
        }
        
        print(f"📧 Sending booking confirmation to {data.get('email')}")
        email_sent = email_service.send_booking_confirmation(data.get('email'), email_details)
        
        if email_sent:
            return jsonify({
                'success': True,
                'message': 'Confirmation email sent successfully'
            })
        else:
            # Email not configured, but don't fail the request
            return jsonify({
                'success': True,
                'message': 'Booking confirmed (email service not configured)',
                'email_sent': False
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
