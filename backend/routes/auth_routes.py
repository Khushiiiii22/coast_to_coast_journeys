"""
Auth Routes
API endpoints for authentication
"""
from flask import Blueprint, request, jsonify, current_app

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/check-status', methods=['GET'])
def check_status():
    """Check if auth service is running"""
    return jsonify({'status': 'online'}), 200

@auth_bp.route('/signup', methods=['POST'])
def signup():
    """
    Sign up a new user with auto-confirmation
    POST /api/auth/signup
    {
        "email": "user@example.com",
        "password": "password123",
        "full_name": "John Doe",
        "phone": "+1234567890"
    }
    """
    try:
        data = request.get_json()
        
        # Validate required fields
        if 'email' not in data or 'password' not in data:
            return jsonify({'success': False, 'error': 'Email and password are required'}), 400
            
        email = data['email']
        password = data['password']
        full_name = data.get('full_name', '')
        phone = data.get('phone', '')
        
        # Get supabase service
        supabase = current_app.config.get('SUPABASE') # This is the client directly
        
        # We need the service wrapper for the admin method
        from services.supabase_service import supabase_service
        
        # Create user with auto-confirm
        metadata = {
            'full_name': full_name,
            'phone': phone,
            'user_type': 'customer'
        }
        
        result = supabase_service.create_user_auto_confirm(email, password, metadata)
        
        if result['success']:
            user = result['data']
            user_id = user.user.id if hasattr(user, 'user') else user.id
            
            # Create customer record in public table
            # Since we are using service role key in 'supabase_service', we can insert into customers table directly
            customer_data = {
                'user_id': user_id,
                'email': email,
                'full_name': full_name,
                'phone': phone,
                'customer_type': 'regular'
            }
            
            # Try to insert customer record
            try:
                supabase_service.client.table('customers').insert(customer_data).execute()
            except Exception as e:
                print(f"Error creating customer record: {e}")
                # Don't fail the whole request if just this part fails, but valid concern
            
            return jsonify({
                'success': True,
                'message': 'Account created successfully',
                'user': {'id': user_id, 'email': email}
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Failed to create account')
            }), 400
            
    except Exception as e:
        print(f"Signup error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
