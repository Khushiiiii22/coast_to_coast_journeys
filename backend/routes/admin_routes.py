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

        query = supabase.table('bookings').select('*')
        
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

        booking = supabase.table('bookings').select('*').eq('id', booking_id).execute()
        
        if not booking.data:
            return jsonify({'success': False, 'error': 'Booking not found'}), 404
        
        # Get payment
        payment = supabase.table('payments').select('*').eq('booking_id', booking_id).execute()
        
        # Get cancellation if exists
        cancellation = supabase.table('cancellation_requests').select('*').eq('booking_id', booking_id).execute()
        
        return jsonify({
            'success': True,
            'data': {
                'booking': booking.data[0],
                'payment': payment.data[0] if payment.data else None,
                'cancellation': cancellation.data[0] if cancellation.data else None
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
    """Get all markup rules"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        result = supabase.table('markup_rules').select('*').eq('is_active', True).order('created_at', desc=True).execute()
        
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
            'rule_type': data['rule_type'],
            'target_id': data.get('target_id'),
            'target_name': data.get('target_name'),
            'markup_type': data['markup_type'],
            'markup_value': float(data['markup_value']),
            'is_active': True,
            'created_by': request.admin_user['admin_id']
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
