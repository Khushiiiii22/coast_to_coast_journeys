from flask import Blueprint, request, jsonify
from services.flight_service import flight_service

flight_bp = Blueprint('flight', __name__, url_prefix='/api/flights')

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


@flight_bp.route('/suggest', methods=['POST'])
def suggest_airports():
    """
    Suggest airports for autocomplete
    Request Body:
    {
        "query": "New York"
    }
    """
    try:
        data = request.get_json()
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
            from config import Config
            if hasattr(Config, 'SUPABASE_URL') and Config.SUPABASE_URL:
                from supabase import create_client
                supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
                import time, random
                timestamp = hex(int(time.time()))[2:].upper()
                rand_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
                ref = booking_id or f"C2C-F{timestamp[-4:]}{rand_part}"
                supabase.table('flight_bookings').insert({
                    'reference_id': ref,
                    'airline': flight.get('airline', ''),
                    'flight_number': flight.get('flightNumber', ''),
                    'origin': flight.get('origin', ''),
                    'destination': flight.get('destination', ''),
                    'date': flight.get('date', ''),
                    'flight_class': flight.get('flightClass', 'economy'),
                    'travelers': flight.get('travelers', 1),
                    'total_amount': amount,
                    'currency': currency,
                    'passenger_name': f"{passenger.get('firstName', '')} {passenger.get('lastName', '')}".strip(),
                    'passenger_email': passenger.get('email', ''),
                    'passenger_phone': passenger.get('phone', ''),
                    'special_requests': passenger.get('specialRequests', ''),
                    'payment_method': 'card',
                    'status': 'confirmed'
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

        booking_record = {
            'reference_id': booking_ref,
            'flight_id': data.get('flight_id', ''),
            'airline': data.get('airline', ''),
            'flight_number': data.get('flight_number', ''),
            'origin': data.get('origin', ''),
            'destination': data.get('destination', ''),
            'date': data.get('date', ''),
            'flight_class': data.get('class', 'economy'),
            'travelers': data.get('travelers', 1),
            'total_amount': data.get('total_amount', 0),
            'currency': data.get('currency', 'INR'),
            'passenger_name': f"{passenger.get('firstName', '')} {passenger.get('lastName', '')}".strip(),
            'passenger_email': passenger.get('email', ''),
            'passenger_phone': passenger.get('phone', ''),
            'special_requests': passenger.get('specialRequests', ''),
            'status': 'confirmed'
        }

        # Try to store in Supabase if available
        try:
            from config import Config
            if hasattr(Config, 'SUPABASE_URL') and Config.SUPABASE_URL:
                from supabase import create_client
                supabase = create_client(Config.SUPABASE_URL, Config.SUPABASE_KEY)
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
