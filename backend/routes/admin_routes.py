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
        mfa_code = data.get('mfa_code')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        from flask import current_app
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        ip_address = request.remote_addr
        result = admin_service.login(email, password, mfa_code, ip_address)
        
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
        period = request.args.get('period', 'all')
        
        result = admin_service.get_dashboard_stats(period=period)
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
        customer_id = request.args.get('customer_id')
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
        
        if customer_id:
            query = query.eq('customer_id', customer_id)
        
        query = query.order('created_at', desc=True).limit(limit).offset(offset)
        
        result = query.execute()
        
        return jsonify({
            'success': True,
            'data': result.data,
            'count': len(result.data)
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/markup/rules/block', methods=['GET', 'POST'])
@require_auth()
def manage_block_markup():
    """Handle block booking markup rules"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        if not supabase:
            return jsonify({'success': False, 'error': 'Database not initialized'}), 500

        if request.method == 'GET':
            # Simplified retrieval of hotel block-type rules
            result = supabase.table('markup_rules').select('*').in_('rule_name', ['Hotel Domestic', 'Hotel International']).execute()
            return jsonify({'success': True, 'data': result.data}), 200

        # POST logic: Upsert the rules
        data = request.json
        rules_to_update = [
            {'rule_name': 'Hotel Domestic', 'rule_type': 'block', 'apply_to': 'hotel', 'markup_type': data.get('hotel_dom_type', 'flat'), 'markup_value': data.get('hotel_dom_val', 0)},
            {'rule_name': 'Hotel International', 'rule_type': 'block', 'apply_to': 'hotel', 'markup_type': data.get('hotel_int_type', 'flat'), 'markup_value': data.get('hotel_int_val', 0)}
        ]

        for rule in rules_to_update:
            supabase.table('markup_rules').upsert(rule, on_conflict='rule_name').execute()

        return jsonify({'success': True, 'message': 'Hotel markup rules updated'}), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/api/admin/markup/rules/convenience', methods=['GET', 'POST'])
def manage_convenience_charge():
    from flask import current_app
    supabase = current_app.config.get('SUPABASE')
    if not supabase:
        return jsonify({'success': False, 'error': 'Database not initialized'}), 500

    if request.method == 'GET':
        result = supabase.table('markup_rules').select('*').eq('rule_type', 'convenience').execute()
        return jsonify({'success': True, 'data': result.data}), 200

    data = request.json
    rules_to_update = [
        {'rule_name': f"Convenience Charge {data.get('category', 'Domestic')}", 'rule_type': 'convenience', 'apply_to': 'hotel', 'target_value': data.get('category', 'Domestic'), 'markup_type': data.get('charge_type', 'flat'), 'markup_value': data.get('charge_val', 0)}
    ]

    for rule in rules_to_update:
        existing = supabase.table('markup_rules').select('id').eq('rule_name', rule['rule_name']).eq('rule_type', 'convenience').execute()
        if existing.data and len(existing.data) > 0:
            supabase.table('markup_rules').update(rule).eq('id', existing.data[0]['id']).execute()
        else:
            supabase.table('markup_rules').insert(rule).execute()

    return jsonify({'success': True, 'message': 'Convenience charge updated successfully'}), 200

@admin_bp.route('/api/admin/markup/rules/cancellation', methods=['GET', 'POST'])
def manage_cancellation_charge():
    from flask import current_app
    supabase = current_app.config.get('SUPABASE')
    if not supabase:
        return jsonify({'success': False, 'error': 'Database not initialized'}), 500

    if request.method == 'GET':
        result = supabase.table('markup_rules').select('*').eq('rule_type', 'cancellation').execute()
        return jsonify({'success': True, 'data': result.data}), 200

    data = request.json
    rules_to_update = [
        {'rule_name': 'Hotel Cancellation Domestic', 'rule_type': 'cancellation', 'apply_to': 'hotel', 'target_value': 'Domestic', 'markup_type': data.get('hotel_dom_type', 'flat'), 'markup_value': data.get('hotel_dom_val', 0)},
        {'rule_name': 'Hotel Cancellation International', 'rule_type': 'cancellation', 'apply_to': 'hotel', 'target_value': 'International', 'markup_type': data.get('hotel_int_type', 'flat'), 'markup_value': data.get('hotel_int_val', 0)}
    ]

    for rule in rules_to_update:
        existing = supabase.table('markup_rules').select('id').eq('rule_name', rule['rule_name']).eq('rule_type', 'cancellation').execute()
        if existing.data and len(existing.data) > 0:
            supabase.table('markup_rules').update(rule).eq('id', existing.data[0]['id']).execute()
        else:
            supabase.table('markup_rules').insert(rule).execute()

    return jsonify({'success': True, 'message': 'Cancellation charge updated successfully'}), 200

@admin_bp.route('/api/admin/system/general', methods=['GET', 'POST'])
def manage_general_settings():
    from flask import current_app
    supabase = current_app.config.get('SUPABASE')
    if not supabase:
        return jsonify({'success': False, 'error': 'Database not initialized'}), 500

    if request.method == 'GET':
        result = supabase.table('system_settings').select('*').eq('category', 'general').execute()
        return jsonify({'success': True, 'data': result.data}), 200

    data = request.json
    for key, value in data.items():
        existing = supabase.table('system_settings').select('id').eq('setting_key', key).execute()
        if existing.data and len(existing.data) > 0:
            supabase.table('system_settings').update({'setting_value': str(value)}).eq('id', existing.data[0]['id']).execute()
        else:
            supabase.table('system_settings').insert({
                'setting_key': key,
                'setting_value': str(value),
                'category': 'general',
                'setting_type': 'string'
            }).execute()

    return jsonify({'success': True, 'message': 'Settings updated successfully'}), 200

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


@admin_bp.route('/bookings/stats', methods=['GET'])
@require_auth()
def get_hotel_booking_stats():
    """Get aggregate stats for hotel bookings"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        if not supabase:
            return jsonify({'success': True, 'data': {'total': 0, 'confirmed': 0, 'pending': 0, 'cancelled': 0}}), 200
            
        # Overall counts
        res = supabase.table('hotel_bookings').select('status').execute()
        bookings = res.data or []
        
        stats = {
            'total': len(bookings),
            'confirmed': len([b for b in bookings if b['status'] == 'confirmed']),
            'pending': len([b for b in bookings if b['status'] == 'pending']),
            'cancelled': len([b for b in bookings if b['status'] == 'cancelled'])
        }
        
        return jsonify({'success': True, 'data': stats}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/bookings', methods=['POST'])
@require_auth(required_role=['super_admin', 'operations'])
def create_manual_hotel_booking():
    """Create a manual hotel booking"""
    try:
        data = request.get_json()
        import time, random
        
        timestamp = hex(int(time.time()))[2:].upper()
        rand_part = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=4))
        booking_ref = f"C2C-H{timestamp[-4:]}{rand_part}"
        
        booking_record = {
            'booking_id': booking_ref,
            'hotel_name': data.get('hotel_name'),
            'check_in': data.get('check_in'),
            'check_out': data.get('check_out'),
            'rooms': int(data.get('rooms', 1)),
            'customer_name': data.get('customer_name'),
            'customer_email': data.get('customer_email'),
            'customer_phone': data.get('customer_phone'),
            'total_amount': float(data.get('total_amount', 0)),
            'currency': data.get('currency', 'INR'),
            'status': data.get('status', 'confirmed'),
            'payment_status': data.get('payment_status', 'paid'),
            'booking_source': 'admin_manual',
            'hotel_star_rating': data.get('hotel_star_rating')
        }
        
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Ensure customer exists or create them
        customer_email = data.get('customer_email')
        if customer_email:
            # Check if customer exists
            cust_res = supabase.table('customers').select('id').eq('email', customer_email).execute()
            if not cust_res.data:
                # Create customer
                customer_data = {
                    'full_name': data.get('customer_name'),
                    'email': customer_email,
                    'phone': data.get('customer_phone'),
                    'status': 'active'
                }
                supabase.table('customers').insert(customer_data).execute()
        
        result = supabase.table('hotel_bookings').insert(booking_record).execute()
        
        # Log activity
        try:
            admin_service = current_app.config.get('ADMIN_SERVICE')
            admin_service.log_activity(
                admin_id=request.admin_user['admin_id'],
                action='create_hotel_booking',
                target_type='hotel_booking',
                target_id=booking_ref,
                ip_address=request.remote_addr
            )
        except Exception: pass
        
        return jsonify({
            'success': True,
            'data': result.data[0] if result.data else None,
            'booking_id': booking_ref
        }), 201
        
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


@admin_bp.route('/customers', methods=['POST'])
@require_auth(required_role=['super_admin', 'operations'])
def create_customer():
    """Create a new customer"""
    try:
        data = request.get_json()
        
        if not data.get('email') or not data.get('full_name'):
            return jsonify({'success': False, 'error': 'Full name and email required'}), 400
            
        customer_record = {
            'full_name': data.get('full_name'),
            'email': data.get('email'),
            'phone': data.get('phone'),
            'date_of_birth': data.get('date_of_birth') or None,
            'gender': data.get('gender'),
            'nationality': data.get('nationality', 'Indian'),
            'passport_number': data.get('passport_number'),
            'address': data.get('address'),
            'city': data.get('city'),
            'country': data.get('country', 'India'),
            'customer_type': data.get('customer_type', 'regular'),
            'is_active': True
        }
        
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Check if exists
        exists = supabase.table('customers').select('id').eq('email', data['email']).execute()
        if exists.data:
            return jsonify({'success': False, 'error': 'Customer with this email already exists'}), 409
            
        result = supabase.table('customers').insert(customer_record).execute()
        
        return jsonify({
            'success': True,
            'data': result.data[0] if result.data else None
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/markup-rules', methods=['GET'])
@require_auth()
def get_markup_rules():
    try:
        service_type = request.args.get('service_type')
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        if not supabase:
            return jsonify({'success': True, 'data': [], 'count': 0}), 200

        query = supabase.table('markup_rules').select('*')
        if service_type:
            query = query.eq('service_type', service_type)
            
        result = query.order('created_at', desc=True).execute()
        
        return jsonify({
            'success': True,
            'data': result.data
        }), 200
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/account/ledger', methods=['GET'])
@require_auth()
def get_ledger():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Fetch from payments table
        response = supabase.table('payments').select('*, hotel_bookings(hotel_name, hotel_city, status)').eq('booking_type', 'hotel').order('created_at', desc=True).execute()
        
        ledger_data = []
        for p in response.data:
            hotel_info = p.get('hotel_bookings') or {}
            ledger_data.append({
                "date": p['created_at'],
                "txn_id": p['payment_id'],
                "order_id": p.get('order_id', '---'),
                "description": f"Hotel Booking: {hotel_info.get('hotel_name', 'N/A')} ({hotel_info.get('hotel_city', 'N/A')})",
                "status": hotel_info.get('status', 'pending'),
                "credit": p['amount'] if p['amount'] > 0 else 0,
                "debit": 0,
                "amount": p['amount']
            })
            
        return jsonify({"status": "success", "data": ledger_data, "balance": 46640})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route('/account/invoices', methods=['GET'])
@require_auth()
def get_invoices():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        if not supabase:
            return jsonify({"status": "error", "message": "Database not initialized"}), 500
            
        # 1. Fetch confirmed hotel bookings as automated invoices
        bookings_response = supabase.table('hotel_bookings').select('*').eq('status', 'confirmed').order('created_at', desc=True).execute()
        
        # 2. Fetch manually created invoices
        manual_response = supabase.table('invoices').select('*').order('created_at', desc=True).execute()
        
        invoices = []
        seen_ref_nos = set()

        # Add manual invoices first (higher priority for custom logic)
        for m in manual_response.data:
            inv_id = f"custom_{m['id']}"
            ref_no = m['invoice_no']
            invoices.append({
                "id": inv_id,
                "booking_date": m['created_at'],
                "lead_pax": m['customer_name'],
                "lead_email": "---",
                "lead_phone": m.get('phone_number', '---'),
                "invoice_id": ref_no,
                "ref_no": ref_no,
                "hotel_name": m.get('category', 'Accommodation (Hotel)'),
                "destination": "---",
                "check_in": "---",
                "status": "confirmed",
                "total_fare": m['price'],
                "markup": 0
            })
            seen_ref_nos.add(ref_no)

        # Add automated ones, avoiding duplicates
        for b in bookings_response.data:
            ref_no = b['partner_order_id']
            # If we already have a manual invoice for this order id, skip
            if ref_no in seen_ref_nos:
                continue

            invoices.append({
                "id": b['id'],
                "booking_date": b['created_at'],
                "lead_pax": b.get('customer_email', 'Guest'),
                "lead_email": b.get('customer_email', '---'),
                "lead_phone": b.get('customer_phone', '---'),
                "invoice_id": f"INV-{b['partner_order_id'][-6:].upper()}",
                "ref_no": ref_no,
                "hotel_name": b['hotel_name'],
                "destination": b['hotel_city'],
                "check_in": b['check_in'],
                "status": b['status'],
                "total_fare": b['total_amount'],
                "markup": b.get('markup_amount', 0)
            })
            
        return jsonify({"status": "success", "data": invoices})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route('/account/invoices', methods=['POST'])
@require_auth()
def create_invoice():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        data = request.get_json()
        
        # Generate custom invoice number if not provided
        if not data.get('invoice_no'):
            import time
            data['invoice_no'] = f"INV{int(time.time())}"

        response = supabase.table('invoices').insert(data).execute()
        return jsonify({"status": "success", "data": response.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route('/queries/hotel', methods=['GET'])
@require_auth()
def get_hotel_enquiries():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        if not supabase:
            return jsonify({"status": "error", "message": "Database not initialized"}), 500

        response = supabase.table('quote_requests').select('*').eq('travel_type', 'hotel').order('created_at', desc=True).execute()
        return jsonify({"status": "success", "data": response.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

@admin_bp.route('/markup/currencies', methods=['GET'])
@require_auth()
def get_currencies():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        response = supabase.table('currencies').select('*').order('created_at', desc=True).execute()
        return jsonify({"success": True, "data": response.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/markup/currencies', methods=['POST'])
@require_auth()
def add_currency():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        data = request.get_json()
        
        # Simple mapping for common countries to fill in codes/flags automatically
        country_defaults = {
            "India": {"code": "INR", "country_code": "IN", "flag": "https://flagcdn.com/w160/in.png"},
            "Dubai": {"code": "AED", "country_code": "AE", "flag": "https://flagcdn.com/w160/ae.png"},
            "United Arab Emirates": {"code": "AED", "country_code": "AE", "flag": "https://flagcdn.com/w160/ae.png"},
            "Australia": {"code": "AUD", "country_code": "AU", "flag": "https://flagcdn.com/w160/au.png"},
            "USA": {"code": "USD", "country_code": "US", "flag": "https://flagcdn.com/w160/us.png"},
            "United States": {"code": "USD", "country_code": "US", "flag": "https://flagcdn.com/w160/us.png"},
            "Canada": {"code": "CAD", "country_code": "CA", "flag": "https://flagcdn.com/w160/ca.png"},
            "UK": {"code": "GBP", "country_code": "GB", "flag": "https://flagcdn.com/w160/gb.png"},
            "United Kingdom": {"code": "GBP", "country_code": "GB", "flag": "https://flagcdn.com/w160/gb.png"},
            "Denmark": {"code": "DKK", "country_code": "DK", "flag": "https://flagcdn.com/w160/dk.png"}
        }

        defaults = country_defaults.get(data['country_name'], {"code": "USD", "country_code": "US", "flag": "https://flagcdn.com/w160/us.png"})
        
        new_currency = {
            "country_name": data['country_name'],
            "country_code": defaults['country_code'],
            "currency_code": defaults['code'],
            "flag_url": defaults['flag'],
            "conversion_rate": float(data['conversion_rate']),
            "status": data['status']
        }

        response = supabase.table('currencies').insert(new_currency).execute()
        return jsonify({"success": True, "data": response.data})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/markup/currencies/live', methods=['GET'])
@require_auth()
def get_live_rates():
    try:
        import requests
        # Using a public API for live rates (ExchangeRate-API)
        # Note: In production you'd use a private key
        url = "https://api.exchangerate-api.com/v4/latest/INR"
        response = requests.get(url)
        rates = response.json().get('rates', {})
        return jsonify({"success": True, "rates": rates})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@admin_bp.route('/markup/currencies/update-all', methods=['POST'])
@require_auth()
def update_all_currencies():
    try:
        from flask import current_app
        import requests
        supabase = current_app.config.get('SUPABASE')
        
        # Get live rates
        url = "https://api.exchangerate-api.com/v4/latest/INR"
        res = requests.get(url)
        live_rates = res.json().get('rates', {})

        # Get existing currencies
        curr_res = supabase.table('currencies').select('id, currency_code').execute()
        
        updates = []
        for c in curr_res.data:
            code = c['currency_code']
            if code in live_rates:
                new_rate = 1 / live_rates[code] if live_rates[code] != 0 else 0
                # Wait, the UI shows INR to Conversion Rate.
                # If 1 INR = 0.012 USD, then "INR to USD" rate is 0.012.
                # If the UI label is "INR to Conversion Rate", and for USD it shows 95.67? 
                # Wait, screenshot 1 shows USD conversion rate as 95.67? 
                # No, look at screenshot 1: United States | USD | 95.67? That's weird. 1 USD = 83 INR.
                # Ah, maybe it's "Conversion Rate to INR"? 
                # Let's check Dubai: AED | 25.97. 1 AED is ~22-23 INR. 
                # So the rate is indeed "[Currency] to INR".
                
                new_rate = 1 / live_rates[code] # This gives INR per [Code] if API is "INR based"?
                # Actually v4/latest/INR returns "1 INR = X [Code]"
                # So if 1 INR = 0.044 AED, then 1 AED = 1/0.044 = 22.7 INR.
                # So rate = 1 / live_rates[code]
                
                supabase.table('currencies').update({"conversion_rate": new_rate}).eq('id', c['id']).execute()
                updates.append(code)

        return jsonify({"success": True, "updated": updates})
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500


@admin_bp.route('/queries/contact', methods=['GET'])
@require_auth()
def get_contact_enquiries():
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        if not supabase:
            return jsonify({"status": "error", "message": "Database not initialized"}), 500

        response = supabase.table('contact_messages').select('*').order('created_at', desc=True).execute()
        return jsonify({"status": "success", "data": response.data})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500


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
            'service_type': data.get('service_type', 'hotel'),
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

        # Ensure customer exists or create them
        customer_email = data.get('passenger_email') or data.get('customer_email')
        if customer_email:
            # Check if customer exists
            cust_res = supabase.table('customers').select('id').eq('email', customer_email).execute()
            if not cust_res.data:
                # Create customer
                customer_data = {
                    'full_name': data.get('passenger_name') or data.get('customer_name'),
                    'email': customer_email,
                    'phone': data.get('passenger_phone') or data.get('customer_phone'),
                    'status': 'active'
                }
                supabase.table('customers').insert(customer_data).execute()

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


@admin_bp.route('/users', methods=['GET'])
@require_auth(required_role=['super_admin'])
def get_users():
    """
    Get list of admin users
    GET /api/admin/users
    """
    try:
        role = request.args.get('role')
        search = request.args.get('search')
        
        from flask import current_app
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        result = admin_service.get_admin_users(role=role, search=search)
        return jsonify(result), 200 if result['success'] else 500
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@admin_bp.route('/users', methods=['POST'])
@require_auth(required_role=['super_admin'])
def create_admin_user():
    """Add a new admin user"""
    try:
        data = request.get_json()
        email = data.get('email')
        full_name = data.get('full_name')
        role = data.get('role', 'staff')
        
        if not email or not full_name:
            return jsonify({'success': False, 'error': 'Email and full name required'}), 400
            
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Check if already exists
        exists = supabase.table('admin_users').select('id').eq('email', email).execute()
        if exists.data:
            return jsonify({'success': False, 'error': 'Admin user already exists'}), 409
            
        user_record = {
            'email': email,
            'full_name': full_name,
            'role': role,
            'is_active': True
        }
        
        result = supabase.table('admin_users').insert(user_record).execute()
        
        return jsonify({
            'success': True,
            'data': result.data[0] if result.data else None
        }), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/finance', methods=['GET'])
@require_auth()
def get_finance():
    """Get finance data (invoices/refunds)"""
    try:
        finance_type = request.args.get('type', 'invoices')
        from flask import current_app
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        data = admin_service.get_finance_data(type=finance_type)
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/suppliers', methods=['GET'])
@require_auth()
def get_suppliers():
    """Get list of suppliers"""
    try:
        from flask import current_app
        admin_service = current_app.config.get('ADMIN_SERVICE')
        
        data = admin_service.get_suppliers()
        return jsonify({'success': True, 'data': data}), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/suppliers', methods=['POST'])
@require_auth(required_role=['super_admin', 'operations'])
def create_supplier():
    try:
        data = request.get_json()
        if not data.get('name'):
            return jsonify({'success': False, 'error': 'Supplier name required'}), 400
            
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        supplier_record = {
            'name': data.get('name'),
            'service_type': data.get('service_type', 'hotel'),
            'api_endpoint': data.get('api_endpoint'),
            'api_status': 'active',
            'balance': 0,
            'currency': 'USD'
        }
        
        result = supabase.table('suppliers').insert(supplier_record).execute()
        return jsonify({'success': True, 'data': result.data[0] if result.data else None}), 201
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@admin_bp.route('/stats', methods=['GET'])
@require_auth()
def get_detailed_stats():
    """Get detailed statistics for reports"""
    try:
        from flask import current_app
        supabase = current_app.config.get('SUPABASE')
        
        # Hotel stats
        hotels_total = supabase.table('hotel_bookings').select('id', count='exact').execute().count or 0
        hotels_revenue = 0
        try:
            res = supabase.table('hotel_bookings').select('total_amount').eq('status', 'confirmed').execute()
            hotels_revenue = sum(float(b.get('total_amount', 0) or 0) for b in res.data)
        except: pass
        
        # Flight stats
        flights_total = supabase.table('flight_bookings').select('id', count='exact').execute().count or 0
        flights_revenue = 0
        try:
            res = supabase.table('flight_bookings').select('total_amount').eq('status', 'confirmed').execute()
            flights_revenue = sum(float(b.get('total_amount', 0) or 0) for b in res.data)
        except: pass
        
        return jsonify({
            'success': True,
            'data': {
                'hotels': {
                    'total': hotels_total,
                    'revenue': round(hotels_revenue, 2)
                },
                'flights': {
                    'total': flights_total,
                    'revenue': round(flights_revenue, 2)
                }
            }
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/notifications', methods=['GET'])
@require_auth()
def get_notifications():
    """
    Get admin notifications (aggregated from recent bookings, enquiries, etc.)
    GET /api/admin/notifications?limit=20
    """
    try:
        from flask import current_app
        from datetime import datetime, timedelta
        supabase = current_app.config.get('SUPABASE')

        if not supabase:
            return jsonify({'success': True, 'data': [], 'unread_count': 0}), 200

        notifications = []
        now = datetime.utcnow()
        seven_days_ago = (now - timedelta(days=7)).isoformat()

        # 1. Recent hotel bookings (last 7 days)
        try:
            bookings = supabase.table('hotel_bookings').select(
                'id, partner_order_id, hotel_name, status, total_amount, currency, customer_email, created_at'
            ).gte('created_at', seven_days_ago).order('created_at', desc=True).limit(10).execute()

            for b in bookings.data:
                status = b.get('status', 'unknown')
                icon = 'fa-check-circle'
                ntype = 'success'
                if status == 'failed':
                    icon = 'fa-times-circle'
                    ntype = 'error'
                elif status == 'created':
                    icon = 'fa-clock'
                    ntype = 'warning'
                elif status == 'unknown':
                    icon = 'fa-question-circle'
                    ntype = 'warning'

                amount = f"{b.get('currency', 'USD')} {float(b.get('total_amount', 0)):,.0f}"
                notifications.append({
                    'id': f"booking_{b['id'][:8]}",
                    'type': ntype,
                    'icon': icon,
                    'category': 'booking',
                    'title': f"Hotel Booking {status.capitalize()}",
                    'message': f"{b.get('hotel_name', 'Hotel')} — {amount}",
                    'link': f"booking-details.html?id={b['id']}",
                    'time': b['created_at'],
                    'read': False
                })
        except Exception as e:
            print(f"Notification: bookings fetch error: {e}")

        # 2. Recent contact enquiries (last 7 days)
        try:
            contacts = supabase.table('contact_messages').select(
                'id, name, email, message, created_at'
            ).gte('created_at', seven_days_ago).order('created_at', desc=True).limit(5).execute()

            for c in contacts.data:
                notifications.append({
                    'id': f"contact_{c['id']}",
                    'type': 'info',
                    'icon': 'fa-envelope',
                    'category': 'enquiry',
                    'title': 'New Contact Enquiry',
                    'message': f"From {c.get('name', 'Unknown')} — {(c.get('message', '')[:60] + '...') if len(c.get('message', '')) > 60 else c.get('message', '')}",
                    'link': 'contact-enquiry.html',
                    'time': c['created_at'],
                    'read': False
                })
        except Exception as e:
            print(f"Notification: contacts fetch error: {e}")

        # 3. Recent hotel enquiries (last 7 days)
        try:
            enquiries = supabase.table('quote_requests').select(
                'id, name, destination, travel_date, created_at'
            ).eq('travel_type', 'hotel').gte('created_at', seven_days_ago).order('created_at', desc=True).limit(5).execute()

            for q in enquiries.data:
                notifications.append({
                    'id': f"enquiry_{q['id']}",
                    'type': 'info',
                    'icon': 'fa-bed',
                    'category': 'enquiry',
                    'title': 'New Hotel Enquiry',
                    'message': f"From {q.get('name', 'Unknown')} for {q.get('destination', 'N/A')}",
                    'link': 'hotel-enquiry.html',
                    'time': q['created_at'],
                    'read': False
                })
        except Exception as e:
            print(f"Notification: enquiries fetch error: {e}")

        # Sort all notifications by time (newest first)
        notifications.sort(key=lambda x: x.get('time', ''), reverse=True)

        # Check read status from localStorage on client side — mark unread count
        limit = int(request.args.get('limit', 20))
        notifications = notifications[:limit]

        return jsonify({
            'success': True,
            'data': notifications,
            'unread_count': len(notifications)
        }), 200

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

