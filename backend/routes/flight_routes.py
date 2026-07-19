from flask import Blueprint, request, jsonify
from services.flight_service import flight_service
from datetime import datetime
import json
import re

flight_bp = Blueprint('flight', __name__, url_prefix='/api/flights')


@flight_bp.route('/enquiry', methods=['POST'])
def submit_flight_enquiry():
    """
    Submit a flight enquiry (lead generation).
    POST /api/flights/enquiry
    {
        "full_name": "John Doe",
        "email": "john@example.com",
        "phone": "9876543210",
        "country_code": "+91",
        "travel_class": "Business Class",
        "trip_type": "Round Trip",
        "from_airport": "Kempegowda International Airport",
        "from_airport_code": "BLR",
        "from_city": "Bangalore",
        "to_airport": "Indira Gandhi International Airport",
        "to_airport_code": "DEL",
        "to_city": "New Delhi",
        "departure_date": "2026-07-24",
        "return_date": "2026-07-28",
        "adults": 2,
        "children": 0,
        "infants": 0
    }
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400
        
        # ── Validation ──
        errors = []
        
        if not data.get('full_name', '').strip():
            errors.append('Full name is required')
        
        email = data.get('email', '').strip()
        if not email or not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            errors.append('Valid email address is required')
        
        phone = data.get('phone', '').strip()
        if not phone or len(re.sub(r'\D', '', phone)) < 7:
            errors.append('Valid phone number is required')
        
        if not data.get('from_airport_code', '').strip():
            errors.append('Departure airport is required')
        
        if not data.get('to_airport_code', '').strip():
            errors.append('Arrival airport is required')
        
        if not data.get('departure_date', '').strip():
            errors.append('Departure date is required')
        
        # Validate dates
        try:
            dep_date = datetime.strptime(data['departure_date'], '%Y-%m-%d')
        except (ValueError, KeyError):
            errors.append('Invalid departure date format (YYYY-MM-DD)')
            dep_date = None
        
        if data.get('trip_type', '').lower() == 'round trip' and data.get('return_date'):
            try:
                ret_date = datetime.strptime(data['return_date'], '%Y-%m-%d')
                if dep_date and ret_date <= dep_date:
                    errors.append('Return date must be after departure date')
            except ValueError:
                errors.append('Invalid return date format (YYYY-MM-DD)')
        
        total_pax = int(data.get('adults', 0)) + int(data.get('children', 0)) + int(data.get('infants', 0))
        if total_pax < 1:
            errors.append('At least 1 passenger is required')
        
        if errors:
            return jsonify({'success': False, 'error': '; '.join(errors)}), 400
        
        # ── Build record ──
        record = {
            'full_name': data['full_name'].strip(),
            'email': email,
            'phone': phone,
            'country_code': data.get('country_code', '+91').strip(),
            'travel_class': data.get('travel_class', 'Business Class'),
            'trip_type': data.get('trip_type', 'One Way'),
            'from_airport': data.get('from_airport', '').strip(),
            'from_airport_code': data.get('from_airport_code', '').strip().upper(),
            'from_city': data.get('from_city', '').strip(),
            'to_airport': data.get('to_airport', '').strip(),
            'to_airport_code': data.get('to_airport_code', '').strip().upper(),
            'to_city': data.get('to_city', '').strip(),
            'departure_date': data['departure_date'],
            'return_date': data.get('return_date') or None,
            'adults': int(data.get('adults', 1)),
            'children': int(data.get('children', 0)),
            'infants': int(data.get('infants', 0)),
            'status': 'New Lead'
        }
        
        # ── Save to Supabase ──
        saved_id = None
        try:
            from services.supabase_service import supabase_service
            supabase = supabase_service.client
            if supabase:
                result = supabase.table('flight_enquiries').insert(record).execute()
                if result.data and len(result.data) > 0:
                    saved_id = result.data[0].get('id')
                print(f"✅ Flight enquiry saved: {record['from_airport_code']} → {record['to_airport_code']} by {record['full_name']}")
        except Exception as db_err:
            print(f"⚠️ Flight enquiry DB save error: {db_err}")
        
        # ── Send Emails (in background) ──
        try:
            from flask import current_app
            from services.email_service import email_service
            import threading
            
            email_service.init_app(current_app)
            
            def send_emails_bg(rcd, usr_email):
                try:
                    email_service.send_flight_enquiry_admin_notification(rcd)
                    email_service.send_flight_enquiry_customer_confirmation(usr_email, rcd)
                except Exception as e:
                    print(f"Background email error: {e}")
                    
            threading.Thread(target=send_emails_bg, args=(record, email)).start()
            
            print(f"✅ Flight enquiry emails sent for {record['full_name']}")
        except Exception as email_err:
            print(f"⚠️ Flight enquiry email error: {email_err}")
        
        return jsonify({
            'success': True,
            'message': 'Your flight enquiry has been submitted successfully.',
            'enquiry_id': saved_id
        })
        
    except Exception as e:
        print(f"❌ Flight enquiry error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def _build_datetime(date_str, time_str=None):
    """Build an ISO datetime string from a date and optional time."""
    if not date_str:
        return None
    try:
        if 'T' in str(date_str):  # Already ISO
            return str(date_str)
        if time_str:
            return f"{date_str}T{time_str}:00"
        return f"{date_str}T00:00:00"
    except Exception:
        return str(date_str)

@flight_bp.route('/search', methods=['POST'])
def search_flights():
    """
    Search for flights
    Request Body:
    {
        "from": "DEL",
        "to": "LHR",
        "departDate": "2026-02-01",
        "returnDate": "2026-02-10", (optional)
        "adults": 1,
        "class": "Economy"
    }
    """
    try:
        data = request.get_json()
        
        required = ['from', 'to', 'departDate']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        result = flight_service.search_flights(
            origin=data['from'],
            destination=data['to'],
            depart_date=data['departDate'],
            return_date=data.get('returnDate'),
            adults=int(data.get('adults', 1)),
            flight_class=data.get('class', 'economy').lower()
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@flight_bp.route('/suggest', methods=['GET', 'POST'])
def suggest_airports():
    """
    Suggest airports for autocomplete
    Request Body:
    {
        "query": "New York"
    }
    """
    try:
        if request.method == 'GET':
            query = request.args.get('q') or request.args.get('query') or ''
        else:
            data = request.get_json(silent=True) or {}
            query = data.get('query', '')
        
        if len(query) < 2:
            return jsonify({'success': False, 'error': 'Query too short'}), 400
            
        result = flight_service.suggest(query)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@flight_bp.route('/send-confirmation', methods=['POST'])
def send_flight_confirmation_email():
    """
    Send flight booking confirmation email (used by test card payment).
    POST /api/flights/send-confirmation
    {
        "booking_id": "C2C-F...",
        "flight": { airline, flightNumber, origin, destination, ... },
        "passenger": { firstName, lastName, email, phone },
        "amount": 45000,
        "currency": "INR"
    }
    """
    try:
        data = request.get_json()
        flight = data.get('flight', {})
        passenger = data.get('passenger', {})
        booking_id = data.get('booking_id', '')
        amount = data.get('amount', 0)
        currency = data.get('currency', 'INR')

        if not passenger.get('email'):
            return jsonify({'success': False, 'error': 'Passenger email required'}), 400

        # Save to Supabase if available
        try:
            from services.supabase_service import supabase_service
            supabase = supabase_service.client
            if supabase:
                import time, random
                timestamp = hex(int(time.time()))[2:].upper()
                rand_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
                ref = booking_id or f"C2C-F{timestamp[-4:]}{rand_part}"

                origin_code = flight.get('origin', '')
                dest_code = flight.get('destination', '')
                dep_dt = _build_datetime(flight.get('date', ''), flight.get('departTime'))
                arr_dt = _build_datetime(flight.get('date', ''), flight.get('arriveTime'))

                # Parse duration to minutes
                duration_minutes = None
                dur_str = flight.get('duration', '')
                if dur_str:
                    try:
                        parts = dur_str.replace('h', '').replace('m', '').split()
                        duration_minutes = int(parts[0]) * 60 + (int(parts[1]) if len(parts) > 1 else 0)
                    except Exception:
                        pass

                passengers_json = [{
                    'first_name': passenger.get('firstName', ''),
                    'last_name': passenger.get('lastName', ''),
                    'email': passenger.get('email', ''),
                    'phone': passenger.get('phone', ''),
                    'type': 'adult'
                }]

                supabase.table('flight_bookings').insert({
                    'booking_id': ref,
                    'flight_type': flight.get('tripType', 'one_way'),
                    'origin_code': origin_code,
                    'origin_city': flight.get('originCity', origin_code),
                    'destination_code': dest_code,
                    'destination_city': flight.get('destinationCity', dest_code),
                    'airline_code': flight.get('airlineCode', ''),
                    'airline_name': flight.get('airline', ''),
                    'flight_number': flight.get('flightNumber', ''),
                    'departure_datetime': dep_dt,
                    'arrival_datetime': arr_dt,
                    'duration_minutes': duration_minutes,
                    'stops': int(flight.get('stops', 0)),
                    'cabin_class': flight.get('flightClass', 'economy'),
                    'passengers': json.dumps(passengers_json),
                    'total_passengers': int(flight.get('travelers', 1)),
                    'base_fare': amount,
                    'total_amount': amount,
                    'currency': currency,
                    'payment_method': 'card',
                    'payment_status': 'paid',
                    'status': 'confirmed',
                    'booking_source': 'website'
                }).execute()
        except Exception as db_err:
            print(f"[Flight Confirmation] DB save skipped: {db_err}")

        # Send email
        try:
            from flask import current_app
            from services.email_service import email_service
            email_service.init_app(current_app)
            email_details = {
                'booking_id': booking_id,
                'airline': flight.get('airline', ''),
                'flight_number': flight.get('flightNumber', ''),
                'origin': flight.get('origin', ''),
                'destination': flight.get('destination', ''),
                'date': flight.get('date', ''),
                'flight_class': flight.get('flightClass', 'economy'),
                'travelers': flight.get('travelers', 1),
                'customer_name': f"{passenger.get('firstName', '')} {passenger.get('lastName', '')}".strip(),
                'customer_email': passenger.get('email', ''),
                'customer_phone': passenger.get('phone', ''),
                'amount': amount,
                'currency': currency,
                'depart_time': flight.get('departTime', ''),
                'arrive_time': flight.get('arriveTime', ''),
                'duration': flight.get('duration', ''),
            }
            email_service.send_flight_confirmation(passenger.get('email', ''), email_details)
        except Exception as email_err:
            print(f"[Flight Confirmation] Email error: {email_err}")

        return jsonify({'success': True, 'booking_id': booking_id})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@flight_bp.route('/create-booking', methods=['POST'])
def create_flight_booking():
    """
    Create a flight booking record
    Request Body:
    {
        "flight_id": "...",
        "airline": "Air India",
        "flight_number": "AI302",
        "origin": "DEL",
        "destination": "LHR",
        "date": "2026-03-15",
        "class": "economy",
        "travelers": 1,
        "total_amount": 45000,
        "currency": "INR",
        "passenger": {
            "firstName": "John",
            "lastName": "Doe",
            "email": "john@example.com",
            "phone": "+919876543210"
        }
    }
    """
    try:
        import time
        data = request.get_json()

        passenger = data.get('passenger', {})
        if not passenger.get('email') or not passenger.get('firstName'):
            return jsonify({'success': False, 'error': 'Missing passenger details'}), 400

        # Generate a booking reference
        timestamp = hex(int(time.time()))[2:].upper()
        import random as _rand
        rand_part = ''.join(_rand.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        booking_ref = f"C2C-F{timestamp[-4:]}{rand_part}"

        origin_code = data.get('origin', '')
        dest_code = data.get('destination', '')
        dep_dt = _build_datetime(data.get('date', ''), data.get('depart_time'))
        arr_dt = _build_datetime(data.get('date', ''), data.get('arrive_time'))

        passengers_json = [{
            'first_name': passenger.get('firstName', ''),
            'last_name': passenger.get('lastName', ''),
            'email': passenger.get('email', ''),
            'phone': passenger.get('phone', ''),
            'type': 'adult'
        }]

        booking_record = {
            'booking_id': booking_ref,
            'flight_type': data.get('flight_type', 'one_way'),
            'origin_code': origin_code,
            'origin_city': data.get('origin_city', origin_code),
            'destination_code': dest_code,
            'destination_city': data.get('destination_city', dest_code),
            'airline_code': data.get('airline_code', ''),
            'airline_name': data.get('airline', ''),
            'flight_number': data.get('flight_number', ''),
            'departure_datetime': dep_dt,
            'arrival_datetime': arr_dt,
            'cabin_class': data.get('class', 'economy'),
            'passengers': json.dumps(passengers_json),
            'total_passengers': int(data.get('travelers', 1)),
            'base_fare': data.get('total_amount', 0),
            'total_amount': data.get('total_amount', 0),
            'currency': data.get('currency', 'INR'),
            'status': 'confirmed',
            'payment_status': 'pending',
            'booking_source': 'website'
        }

        # Try to store in Supabase if available
        try:
            from services.supabase_service import supabase_service
            supabase = supabase_service.client
            if supabase:
                supabase.table('flight_bookings').insert(booking_record).execute()
        except Exception as db_err:
            print(f"[Flight Booking] DB save skipped: {db_err}")

        return jsonify({
            'success': True,
            'booking_id': booking_ref,
            'reference_id': booking_ref
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
