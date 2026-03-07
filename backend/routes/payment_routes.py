"""
Payment Routes
API endpoints for payment processing
"""
from flask import Blueprint, request, jsonify, current_app
import hmac
import hashlib
from services.admin_service import require_auth

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

@payment_bp.route('/create-order', methods=['POST'])
def create_order():
    """
    Create Razorpay order for hotel booking
    POST /api/payment/create-order
    {
        "amount": 5000.00,
        "currency": "INR",
        "booking_details": {
            "hotel_name": "Example Hotel",
            "checkin": "2026-03-15",
            "checkout": "2026-03-18"
        }
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'amount' not in data:
            return jsonify({'success': False, 'error': 'Amount is required'}), 400
        
        from flask import current_app
        razorpay_service = current_app.config.get('RAZORPAY_SERVICE')
        
        if not razorpay_service:
            return jsonify({'success': False, 'error': 'Payment service not configured'}), 500
        
        # Create order
        result = razorpay_service.create_order(
            amount=float(data['amount']),
            currency=data.get('currency', 'INR'),
            notes=data.get('booking_details', {})
        )
        
        if result['success']:
            # Return order details + Razorpay key for frontend
            return jsonify({
                'success': True,
                'order_id': result['order_id'],
                'amount': result['amount'],
                'currency': result['currency'],
                'key_id': razorpay_service.key_id  # Frontend needs this
            }), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/verify', methods=['POST'])
def verify_payment():
    """
    Verify payment signature after checkout
    POST /api/payment/verify
    {
        "razorpay_order_id": "order_xxx",
        "razorpay_payment_id": "pay_xxx",
        "razorpay_signature": "signature_xxx",
        "booking_id": "uuid"
    }
    """
    try:
        data = request.get_json()
        
        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400
        
        from flask import current_app
        razorpay_service = current_app.config.get('RAZORPAY_SERVICE')
        supabase = current_app.config.get('SUPABASE')
        
        # Verify signature
        is_valid = razorpay_service.verify_payment_signature(
            data['razorpay_order_id'],
            data['razorpay_payment_id'],
            data['razorpay_signature']
        )
        
        if is_valid:
            # Update booking status
            if 'booking_id' in data and supabase:
                try:
                    # Update booking as confirmed
                    supabase.table('hotel_bookings').update({
                        'status': 'confirmed',
                        'updated_at': 'NOW()'
                    }).eq('id', data['booking_id']).execute()
                    
                    # Create payment record
                    supabase.table('payments').insert({
                        'booking_id': data['booking_id'],
                        'razorpay_order_id': data['razorpay_order_id'],
                        'razorpay_payment_id': data['razorpay_payment_id'],
                        'razorpay_signature': data['razorpay_signature'],
                        'status': 'paid'
                    }).execute()
                    
                    # Fetch booking details for email
                    booking_response = supabase.table('hotel_bookings').select('*').eq('id', data['booking_id']).execute()
                    if booking_response.data:
                        booking = booking_response.data[0]
                        
                        # Confirm booking with ETG
                        try:
                            from services.etg_service import etg_service
                            if booking.get('partner_order_id'):
                                print(f"Confirming booking with ETG: {booking.get('partner_order_id')}")
                                etg_service.finish_booking(booking['partner_order_id'])
                        except Exception as etg_error:
                            print(f"ETG Finish Booking Error: {etg_error}")
                        
                        # Prepare details for email
                        email_details = {
                            'booking_id': booking.get('id'),
                            'hotel_name': booking.get('hotel_name', 'Hotel'),
                            'customer_name': f"{booking.get('first_name', '')} {booking.get('last_name', '')}",
                            'customer_email': booking.get('email'),
                            'checkin': booking.get('checkin'),
                            'checkout': booking.get('checkout'),
                            'amount': booking.get('total_amount'),
                            'currency': booking.get('currency', 'INR')
                        }
                        
                        # Send confirmation email
                        from services.email_service import email_service
                        email_service.init_app(current_app)  # Ensure config is loaded
                        email_service.send_booking_confirmation(booking.get('email'), email_details)
                        
                except Exception as db_error:
                    print(f"Database/Email update error: {db_error}")
            
            return jsonify({
                'success': True,
                'message': 'Payment verified successfully'
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Invalid payment signature'
            }), 400
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/refund', methods=['POST'])
@require_auth(required_role=['super_admin', 'finance'])
def create_refund():
    """
    Create refund (Admin only)
    POST /api/payment/refund
    {
        "payment_id": "pay_xxx",
        "amount": 1000.00,  // Optional, leave empty for full refund
        "reason": "Customer request"
    }
    """
    try:
        data = request.get_json()
        
        if 'payment_id' not in data:
            return jsonify({'success': False, 'error': 'payment_id is required'}), 400
        
        from flask import current_app
        razorpay_service = current_app.config.get('RAZORPAY_SERVICE')
        
        result = razorpay_service.create_refund(
            payment_id=data['payment_id'],
            amount=data.get('amount'),
            notes={'reason': data.get('reason', 'Admin refund')}
        )
        
        if result['success']:
            # Log refund in database
            supabase = current_app.config.get('SUPABASE')
            if supabase:
                try:
                    # Update payment status
                    supabase.table('payments').update({
                        'status': 'refunded',
                        'updated_at': 'NOW()'
                    }).eq('razorpay_payment_id', data['payment_id']).execute()
                except Exception as db_error:
                    print(f"Database update error: {db_error}")
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/webhook', methods=['POST'])
def razorpay_webhook():
    """
    Razorpay webhook handler
    POST /api/payment/webhook
    
    Handles events like:
    - payment.captured
    - payment.failed
    - refund.processed
    """
    try:
        # Get webhook signature
        webhook_signature = request.headers.get('X-Razorpay-Signature')
        webhook_secret = current_app.config.get('RAZORPAY_WEBHOOK_SECRET')
        
        if not webhook_signature or not webhook_secret:
            return jsonify({'success': False, 'error': 'Invalid webhook'}), 400
        
        # Verify webhook signature
        payload = request.get_data()
        expected_signature = hmac.new(
            webhook_secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        if not hmac.compare_digest(expected_signature, webhook_signature):
            return jsonify({'success': False, 'error': 'Invalid signature'}), 400
        
        # Process webhook event
        event = request.get_json()
        event_type = event.get('event')
        
        # Handle different event types
        if event_type == 'payment.captured':
            # Payment successful
            payment = event.get('payload', {}).get('payment', {}).get('entity', {})
            # Update database, send confirmation email, etc.
            print(f"Payment captured: {payment.get('id')}")
        
        elif event_type == 'payment.failed':
            # Payment failed
            payment = event.get('payload', {}).get('payment', {}).get('entity', {})
            print(f"Payment failed: {payment.get('id')}")
        
        elif event_type == 'refund.processed':
            # Refund completed
            refund = event.get('payload', {}).get('refund', {}).get('entity', {})
            print(f"Refund processed: {refund.get('id')}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        print(f"Webhook error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# PayPal Payment Routes

@payment_bp.route('/paypal/create-order', methods=['POST'])
def create_paypal_order():
    """
    Create PayPal order for hotel booking
    POST /api/payment/paypal/create-order
    {
        "amount": 100.00,
        "currency": "USD",
        "description": "Hotel Booking",
        "return_url": "https://...",
        "cancel_url": "https://..."
    }
    """
    try:
        data = request.get_json()
        
        if 'amount' not in data:
            return jsonify({'success': False, 'error': 'Amount is required'}), 400
        
        paypal_service = current_app.config.get('PAYPAL_SERVICE')
        
        if not paypal_service:
            return jsonify({'success': False, 'error': 'PayPal service not configured'}), 500
        
        result = paypal_service.create_order(
            amount=float(data['amount']),
            currency=data.get('currency', 'USD'),
            description=data.get('description', 'Hotel Booking'),
            return_url=data.get('return_url'),
            cancel_url=data.get('cancel_url')
        )
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ===== Flight-Specific Payment Routes =====

def _create_flight_booking_record(flight, passenger, amount, payment_method, payment_id):
    """Helper: Generate a flight booking record dict with reference ID"""
    import time, random
    timestamp = hex(int(time.time()))[2:].upper()
    rand_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
    booking_ref = f"C2C-F{timestamp[-4:]}{rand_part}"
    return booking_ref, {
        'reference_id': booking_ref,
        'flight_id': flight.get('flightId', ''),
        'airline': flight.get('airline', ''),
        'flight_number': flight.get('flightNumber', ''),
        'origin': flight.get('origin', ''),
        'destination': flight.get('destination', ''),
        'date': flight.get('date', ''),
        'flight_class': flight.get('flightClass', 'economy'),
        'travelers': flight.get('travelers', 1),
        'total_amount': amount,
        'currency': flight.get('currency', 'INR'),
        'passenger_name': f"{passenger.get('firstName', '')} {passenger.get('lastName', '')}".strip(),
        'passenger_email': passenger.get('email', ''),
        'passenger_phone': passenger.get('phone', ''),
        'special_requests': passenger.get('specialRequests', ''),
        'payment_method': payment_method,
        'payment_id': payment_id,
        'status': 'confirmed'
    }


def _save_and_email_flight_booking(booking_ref, booking_record, flight, passenger, amount):
    """Helper: Save flight booking to Supabase and send confirmation email"""
    supabase = current_app.config.get('SUPABASE')
    if supabase:
        try:
            supabase.table('flight_bookings').insert(booking_record).execute()
            print(f"✅ Flight booking saved: {booking_ref}")
        except Exception as db_err:
            print(f"Flight booking DB error: {db_err}")

    try:
        from services.email_service import email_service
        email_service.init_app(current_app)
        email_details = {
            'booking_id': booking_ref,
            'airline': flight.get('airline', ''),
            'flight_number': flight.get('flightNumber', ''),
            'origin': flight.get('origin', ''),
            'destination': flight.get('destination', ''),
            'date': flight.get('date', ''),
            'flight_class': flight.get('flightClass', 'economy'),
            'travelers': flight.get('travelers', 1),
            'customer_name': booking_record.get('passenger_name', ''),
            'customer_email': passenger.get('email', ''),
            'customer_phone': passenger.get('phone', ''),
            'amount': amount,
            'currency': flight.get('currency', 'INR'),
            'depart_time': flight.get('departTime', ''),
            'arrive_time': flight.get('arriveTime', ''),
            'duration': flight.get('duration', ''),
        }
        email_service.send_flight_confirmation(passenger.get('email', ''), email_details)
        print(f"✅ Flight confirmation email sent to {passenger.get('email', '')}")
    except Exception as email_err:
        print(f"Flight email error: {email_err}")


@payment_bp.route('/flight/verify', methods=['POST'])
def verify_flight_payment():
    """
    Verify Razorpay payment for flight booking and save booking record.
    POST /api/payment/flight/verify
    {
        "razorpay_order_id": "order_xxx",
        "razorpay_payment_id": "pay_xxx",
        "razorpay_signature": "sig_xxx",
        "amount": 45000,
        "flight": { airline, flightNumber, origin, destination, date, ... },
        "passenger": { firstName, lastName, email, phone, specialRequests }
    }
    """
    try:
        data = request.get_json()

        required_fields = ['razorpay_order_id', 'razorpay_payment_id', 'razorpay_signature']
        for field in required_fields:
            if field not in data:
                return jsonify({'success': False, 'error': f'{field} is required'}), 400

        razorpay_service = current_app.config.get('RAZORPAY_SERVICE')
        if not razorpay_service:
            return jsonify({'success': False, 'error': 'Payment service not configured'}), 500

        is_valid = razorpay_service.verify_payment_signature(
            data['razorpay_order_id'],
            data['razorpay_payment_id'],
            data['razorpay_signature']
        )

        if is_valid:
            flight = data.get('flight', {})
            passenger = data.get('passenger', {})
            amount = data.get('amount', 0)

            booking_ref, booking_record = _create_flight_booking_record(
                flight, passenger, amount, 'razorpay', data['razorpay_payment_id']
            )
            _save_and_email_flight_booking(booking_ref, booking_record, flight, passenger, amount)

            return jsonify({
                'success': True,
                'booking_id': booking_ref,
                'message': 'Payment verified and flight booking confirmed'
            }), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid payment signature'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/paypal/flight/capture/<order_id>', methods=['POST'])
def capture_paypal_flight_order(order_id):
    """
    Capture PayPal order for flight booking.
    POST /api/payment/paypal/flight/capture/{order_id}
    {
        "flight": { ... },
        "passenger": { ... },
        "amount": 45000
    }
    """
    try:
        paypal_service = current_app.config.get('PAYPAL_SERVICE')
        if not paypal_service:
            return jsonify({'success': False, 'error': 'PayPal service not configured'}), 500

        result = paypal_service.capture_order(order_id)

        if result['success']:
            data = request.get_json() or {}
            flight = data.get('flight', {})
            passenger = data.get('passenger', {})
            amount = data.get('amount', 0)

            booking_ref, booking_record = _create_flight_booking_record(
                flight, passenger, amount, 'paypal', order_id
            )
            _save_and_email_flight_booking(booking_ref, booking_record, flight, passenger, amount)

            result['booking_id'] = booking_ref
            result['message'] = 'PayPal payment captured and flight booking confirmed'

        return jsonify(result), 200 if result['success'] else 500

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/paypal/capture-order/<order_id>', methods=['POST'])
def capture_paypal_order(order_id):
    """
    Capture PayPal order after customer approval
    POST /api/payment/paypal/capture-order/{order_id}
    """
    try:
        paypal_service = current_app.config.get('PAYPAL_SERVICE')
        
        if not paypal_service:
            return jsonify({'success': False, 'error': 'PayPal service not configured'}), 500
        
        result = paypal_service.capture_order(order_id)
        
        if result['success']:
            # Update booking status
            supabase = current_app.config.get('SUPABASE')
            data = request.get_json() or {}
            
            if 'booking_id' in data and supabase:
                try:
                    supabase.table('hotel_bookings').update({
                        'status': 'confirmed',
                        'updated_at': 'NOW()'
                    }).eq('id', data['booking_id']).execute()
                    
                    supabase.table('payments').insert({
                        'booking_id': data['booking_id'],
                        'paypal_order_id': order_id,
                        'status': 'paid',
                        'payment_method': 'paypal'
                    }).execute()
                except Exception as db_error:
                    print(f"Database update error: {db_error}")

                # Send confirmation email logic for PayPal
                try:
                    # Fetch booking details for email
                    booking_response = supabase.table('hotel_bookings').select('*').eq('id', data['booking_id']).execute()
                    if booking_response.data:
                        booking = booking_response.data[0]
                        
                        # Confirm booking with ETG
                        try:
                            from services.etg_service import etg_service
                            if booking.get('partner_order_id'):
                                print(f"Confirming booking with ETG: {booking.get('partner_order_id')}")
                                etg_service.finish_booking(booking['partner_order_id'])
                        except Exception as etg_error:
                             print(f"ETG Finish Booking Error: {etg_error}")

                        # Prepare details for email
                        email_details = {
                            'booking_id': booking.get('id'),
                            'hotel_name': booking.get('hotel_name', 'Hotel'),
                            'customer_name': f"{booking.get('first_name', '')} {booking.get('last_name', '')}",
                            'customer_email': booking.get('email'),
                            'checkin': booking.get('checkin'),
                            'checkout': booking.get('checkout'),
                            'amount': booking.get('total_amount'),
                            'currency': booking.get('currency', 'INR')
                        }
                        
                        # Send confirmation email
                        from services.email_service import email_service
                        email_service.init_app(current_app)  # Ensure config is loaded
                        email_service.send_booking_confirmation(booking.get('email'), email_details)
                except Exception as email_error:
                    print(f"Email sending error: {email_error}")
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@payment_bp.route('/paypal/order-details/<order_id>', methods=['GET'])
def get_paypal_order_details(order_id):
    """
    Get PayPal order details
    GET /api/payment/paypal/order-details/{order_id}
    """
    try:
        paypal_service = current_app.config.get('PAYPAL_SERVICE')
        
        if not paypal_service:
            return jsonify({'success': False, 'error': 'PayPal service not configured'}), 500
        
        result = paypal_service.get_order_details(order_id)
        
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
