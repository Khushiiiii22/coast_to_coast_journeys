"""
Admin Routes
API endpoints for admin panel operations
"""
from flask import Blueprint, request, jsonify
from services.admin_service import require_auth

admin_bp = Blueprint('admin', __name__, url_prefix='/api/admin')

@admin_bp.route('/login', methods=['POST'])
def login():
    """
    Admin login
    POST /api/admin/login
    {
        "email": "admin@coasttocoast.com",
        "password": "admin123"
    }
    """
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        from flask import current_app
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        ip_address = request.remote_addr
        result = admin_service.login(email, password, ip_address)
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 401
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/dashboard', methods=['GET'])
@require_auth()
def get_dashboard():
    """
    Get dashboard statistics
    GET /api/admin/dashboard
    Headers: Authorization: Bearer <token>
    """
    try:
        from flask import current_app
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        result = admin_service.get_dashboard_stats()
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/bookings', methods=['GET'])
@require_auth()
def get_bookings():
    """
    Get all bookings with filters
    GET /api/admin/bookings?status=confirmed&limit=50&offset=0
    """
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Get query params
        status = request.args.get('status')
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        # Build query
        if not supabase:
            return jsonify({
                'success': True,
                'data': [],
                'count': 0,
                'message': 'Database not initialized'
            }), 200

        query = supabase.table('hotel_bookings').select('*')
        
        if status:
            query = query.eq('status', status)
        
        query = query.order('created_at', desc=True).limit(limit).offset(offset)
        
        result = query.execute()
        
        return jsonify({
            'success': True,
            'data': result.data,
            'count': len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/bookings/<booking_id>', methods=['GET'])
@require_auth()
def get_booking_details(booking_id):
    """Get single booking details"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Get booking
        if not supabase:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500

        booking = supabase.table('hotel_bookings').select('*').eq('id', booking_id).execute()
        
        if not booking.data:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Get payment
        payment = supabase.table('payments').select('*').eq('booking_id', booking_id).execute()
        
        # Get cancellation if exists
        cancellation_data = None
        try:
            cancellation = supabase.table('cancellation_requests').select('*').eq('booking_id', booking_id).execute()
            cancellation_data = cancellation.data[0] if cancellation.data else None
        except Exception:
            pass  # Table may not exist or query may fail
        
        return jsonify({
            'success': True,
            'data': {
                'booking': booking.data[0],
                'payment': payment.data[0] if payment.data else None,
                'cancellation': cancellation_data
            }
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/customers', methods=['GET'])
@require_auth()
def get_customers():
    """Get all customers"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))
        
        if not supabase:
            return jsonify({'success': True, 'data': [], 'count': 0}), 200

        result = supabase.table('customers').select('*').order('created_at', desc=True).limit(limit).offset(offset).execute()
        
        return jsonify({
            'success': True,
            'data': result.data,
            'count': len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/markup-rules', methods=['GET'])
@require_auth()
def get_markup_rules():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        if not supabase:
            return jsonify({'success': True, 'data': [], 'count': 0}), 200

        result = supabase.table('markup_rules').select('*').order('created_at', desc=True).execute()
        
        return jsonify({
            'success': True,
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/markup-rules', methods=['POST'])
@require_auth(required_role=['super_admin', 'operations'])
def create_markup_rule():
    """Create new markup rule"""
    try:
        data = request.get_json()
        
        required = ['rule_type', 'markup_type', 'markup_value']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        # Create rule
        rule = {
            'rule_name': data.get('target_name', 'Unnamed Rule'),
            'rule_type': data['rule_type'],
            'apply_to': data.get('apply_to', data['rule_type']),
            'target_value': data.get('target_id'),
            'markup_type': data['markup_type'],
            'markup_value': float(data['markup_value']),
            'is_active': True,
            'created_by': request.admin_user.get('auth_user_id')
        }
        
        result = supabase.table('markup_rules').insert(rule).execute()
        
        # Log activity
        admin_service.log_activity(
            admin_id=request.admin_user['admin_id'],
            action='create_markup_rule',
            target_type='markup',
            target_id=result.data[0]['id'] if result.data else None,
            ip_address=request.remote_addr
        )
        
        return jsonify({
            'success': True,
            'data': result.data[0] if result.data else None
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/markup-rules/<rule_id>', methods=['PUT', 'DELETE'])
@require_auth(required_role=['super_admin', 'operations'])
def handle_markup_rule(rule_id):
    """Update or delete a markup rule"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        if request.method == 'PUT':
            data = request.get_json()
            update_data = {}
            
            if 'markup_value' in data:
                update_data['markup_value'] = float(data['markup_value'])
            if 'is_active' in data:
                update_data['is_active'] = bool(data['is_active'])
            if 'markup_type' in data:
                update_data['markup_type'] = data['markup_type']
                
            update_data['updated_at'] = 'now()'
            
            result = supabase.table('markup_rules').update(update_data).eq('id', rule_id).execute()
            
            # Log activity
            admin_service.log_activity(
                admin_id=request.admin_user['admin_id'],
                action='update_markup_rule',
                target_type='markup',
                target_id=rule_id,
                ip_address=request.remote_addr
            )
            
            return jsonify({'success': True, 'data': result.data[0] if result.data else None}), 200
            
        elif request.method == 'DELETE':
            # Instead of hard delete, we can just deactivate it or delete if user is super admin
            result = supabase.table('markup_rules').delete().eq('id', rule_id).execute()
            
            # Log activity
            admin_service.log_activity(
                admin_id=request.admin_user['admin_id'],
                action='delete_markup_rule',
                target_type='markup',
                target_id=rule_id,
                ip_address=request.remote_addr
            )
            
            return jsonify({'success': True, 'message': 'Rule deleted successfully'}), 200
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/activity-logs', methods=['GET'])
@require_auth(required_role=['super_admin'])
def get_activity_logs():
    """Get admin activity logs"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        limit = int(request.args.get('limit', 100))
        
        result = supabase.table('admin_activity_logs').select('*, admin_users(email, full_name)').order('created_at', desc=True).limit(limit).execute()
        
        return jsonify({
            'success': True,
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ─── Flight Bookings Admin Endpoints ─────────────────────────────────────────

@admin_bp.route('/flight-bookings', methods=['GET'])
@require_auth()
def get_flight_bookings():
    """
    Get all flight bookings with filters
    GET /api/admin/flight-bookings?status=confirmed&airline=AI&from_date=2026-01-01&to_date=2026-12-31&search=ABC&limit=50&offset=0
    """
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')

        if not supabase:
            return jsonify({'success': True, 'data': [], 'count': 0, 'message': 'Database not initialized'}), 200

        status = request.args.get('status')
        airline = request.args.get('airline')
        trip_type = request.args.get('trip_type')
        from_date = request.args.get('from_date')
        to_date = request.args.get('to_date')
        search = request.args.get('search', '').strip()
        limit = int(request.args.get('limit', 50))
        offset = int(request.args.get('offset', 0))

        query = supabase.table('flight_bookings').select('*', count='exact')

        if status:
            query = query.eq('status', status)
        if airline:
            query = query.eq('airline_code', airline)
        if trip_type and trip_type != 'all':
            if trip_type == 'roundtrip':
                query = query.not_.is_('return_flight_number', 'null')
            elif trip_type in ('domestic', 'international'):
                query = query.eq('trip_type', trip_type)
        if from_date:
            query = query.gte('departure_datetime', from_date)
        if to_date:
            query = query.lte('departure_datetime', to_date + 'T23:59:59')
        if search:
            # Search by booking_id, pnr, or passenger name via ilike on booking_id
            query = query.or_(
                f"booking_id.ilike.%{search}%,pnr.ilike.%{search}%,airline_name.ilike.%{search}%,flight_number.ilike.%{search}%"
            )

        query = query.order('created_at', desc=True).limit(limit).offset(offset)
        result = query.execute()

        return jsonify({
            'success': True,
            'data': result.data,
            'count': result.count or len(result.data),
            'limit': limit,
            'offset': offset
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/flight-bookings/stats', methods=['GET'])
@require_auth()
def get_flight_booking_stats():
    """Get aggregate stats for flight bookings"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')

        if not supabase:
            return jsonify({
                'success': True,
                'data': {
                    'total': 0, 'confirmed': 0, 'pending': 0,
                    'cancelled': 0, 'revenue': 0
                }
            }), 200

        # Total
        total = 0
        try:
            total_res = supabase.table('flight_bookings').select('id', count='exact').execute()
            total = total_res.count or 0
        except Exception: pass

        # Confirmed
        confirmed = 0
        try:
            confirmed_res = supabase.table('flight_bookings').select('id', count='exact').eq('status', 'confirmed').execute()
            confirmed = confirmed_res.count or 0
        except Exception: pass

        # Pending
        pending = 0
        try:
            pending_res = supabase.table('flight_bookings').select('id', count='exact').eq('status', 'pending').execute()
            pending = pending_res.count or 0
        except Exception: pass

        # Cancelled
        cancelled = 0
        try:
            cancelled_res = supabase.table('flight_bookings').select('id', count='exact').eq('status', 'cancelled').execute()
            cancelled = cancelled_res.count or 0
        except Exception: pass

        # Revenue from confirmed bookings
        revenue = 0
        try:
            revenue_res = supabase.table('flight_bookings').select('total_amount').eq('status', 'confirmed').execute()
            revenue = sum(float(b.get('total_amount', 0) or 0) for b in revenue_res.data)
        except Exception: pass

        # Domestic vs International counts
        domestic = 0
        try:
            domestic_res = supabase.table('flight_bookings').select('id', count='exact').eq('trip_type', 'domestic').execute()
            domestic = domestic_res.count or 0
        except Exception: pass
        international = max(0, total - domestic)

        # Round trip count
        roundtrip = 0
        try:
            roundtrip_res = supabase.table('flight_bookings').select('id', count='exact').not_.is_('return_flight_number', 'null').execute()
            roundtrip = roundtrip_res.count or 0
        except Exception: pass

        return jsonify({
            'success': True,
            'data': {
                'total': total,
                'confirmed': confirmed,
                'pending': pending,
                'cancelled': cancelled,
                'revenue': round(revenue, 2),
                'domestic': domestic,
                'international': international,
                'roundtrip': roundtrip
            }
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/flight-bookings/<booking_id>', methods=['GET'])
@require_auth()
def get_flight_booking_details(booking_id):
    """Get single flight booking details"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')

        if not supabase:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500

        booking = supabase.table('flight_bookings').select('*').eq('id', booking_id).execute()

        if not booking.data:
            # Try by booking_id field too
            booking = supabase.table('flight_bookings').select('*').eq('booking_id', booking_id).execute()

        if not booking.data:
            return jsonify({'success': False, 'error': 'Flight booking not found'}), 404

        return jsonify({
            'success': True,
            'data': booking.data[0]
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/flight-bookings/<booking_id>/status', methods=['PUT'])
@require_auth(required_role=['super_admin', 'operations'])
def update_flight_booking_status(booking_id):
    """Update flight booking status"""
    try:
        data = request.get_json()
        new_status = data.get('status')

        if not new_status or new_status not in ('confirmed', 'pending', 'cancelled', 'processing', 'completed'):
            return jsonify({'success': False, 'error': 'Invalid status'}), 400

        from flask import current_app
        supabase = current_app.config.get('SUPABASE')

        update_data = {'status': new_status, 'updated_at': 'now()'}

        if new_status == 'cancelled':
            import datetime as dt
            update_data['cancelled_at'] = dt.datetime.utcnow().isoformat()
            update_data['cancellation_reason'] = data.get('reason', '')

        result = supabase.table('flight_bookings').update(update_data).eq('id', booking_id).execute()

        if not result.data:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404

        return jsonify({'success': True, 'data': result.data[0]}), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/flight-bookings', methods=['POST'])
@require_auth(required_role=['super_admin', 'operations'])
def create_manual_flight_booking():
    """Create a manual flight booking from admin panel"""
    try:
        data = request.get_json()
        import time, random, json

        timestamp = hex(int(time.time()))[2:].upper()
        rand_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        booking_ref = f"C2C-F{timestamp[-4:]}{rand_part}"

        passengers_json = [{
            'first_name': data.get('passenger_name', '').split(' ')[0],
            'last_name': ' '.join(data.get('passenger_name', '').split(' ')[1:]),
            'email': data.get('passenger_email', ''),
            'phone': data.get('passenger_phone', ''),
            'type': 'adult'
        }]

        dep_dt = data.get('departure_date')
        if dep_dt and not 'T' in dep_dt:
            dep_dt = f"{dep_dt}T00:00:00"

        booking_record = {
            'booking_id': booking_ref,
            'flight_type': data.get('flight_type', 'one_way'),
            'trip_type': data.get('trip_type', 'domestic'),
            'origin_code': data.get('origin_code', ''),
            'origin_city': data.get('origin_city', data.get('origin_code', '')),
            'destination_code': data.get('destination_code', ''),
            'destination_city': data.get('destination_city', data.get('destination_code', '')),
            'airline_code': data.get('airline_code', ''),
            'airline_name': data.get('airline_name', ''),
            'flight_number': data.get('flight_number', ''),
            'departure_datetime': dep_dt,
            'arrival_datetime': dep_dt,
            'cabin_class': data.get('cabin_class', 'economy'),
            'passengers': json.dumps(passengers_json),
            'total_passengers': int(data.get('total_passengers', 1)),
            'pnr': data.get('pnr', ''),
            'base_fare': float(data.get('base_fare', 0)),
            'taxes_fees': float(data.get('taxes_fees', 0)),
            'markup_amount': float(data.get('markup_amount', 0)),
            'total_amount': float(data.get('base_fare', 0)) + float(data.get('taxes_fees', 0)) + float(data.get('markup_amount', 0)),
            'currency': data.get('currency', 'INR'),
            'status': data.get('status', 'confirmed'),
            'payment_status': data.get('payment_status', 'paid'),
            'booking_source': 'admin_manual'
        }

        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        result = supabase.table('flight_bookings').insert(booking_record).execute()

        # Log activity
        try:
            admin_service = current_app.config.get('ADMIN_SERVICE')
            admin_service.log_activity(
                admin_id=request.admin_user['admin_id'],
                action='create_flight_booking',
                target_type='flight_booking',
                target_id=booking_ref,
                ip_address=request.remote_addr
            )
        except Exception:
            pass

        return jsonify({
            'success': True,
            'data': result.data[0] if result.data else None,
            'booking_id': booking_ref
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
