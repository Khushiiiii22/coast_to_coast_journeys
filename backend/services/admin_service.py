"""
Admin Service
Handles authentication, authorization, and core admin operations
"""
import bcrypt
import jwt
import datetime
from functools import wraps
from flask import request, jsonify

class AdminService:
    def __init__(self, supabase_client, secret_key):
        self.supabase = supabase_client
        self.secret_key = secret_key
        self.token_expiry = 24  # hours
    
    def hash_password(self, password):
        """Hash password using bcrypt"""
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    def verify_password(self, password, password_hash):
        """Verify password against hash"""
        return bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
    
    def generate_token(self, admin_id, email, role):
        """Generate JWT token"""
        payload = {
            'admin_id': admin_id,
            'email': email,
            'role': role,
            'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=self.token_expiry)
        }
        return jwt.encode(payload, self.secret_key, algorithm='HS256')
    
    def verify_token(self, token):
        """Verify JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=['HS256'])
            return {'success': True, 'data': payload}
        except jwt.ExpiredSignatureError:
            return {'success': False, 'error': 'Token expired'}
        except jwt.InvalidTokenError:
            return {'success': False, 'error': 'Invalid token'}
    
    def login(self, email, password, ip_address=None):
        """Authenticate admin user"""
        try:
            # Hardcoded admin credentials for demo
            ADMIN_CREDENTIALS = {
                'admin@coasttocoast.com': {
                    'password': 'admin123',
                    'full_name': 'Super Admin',
                    'role': 'super_admin'
                }
            }
            
            # Check hardcoded credentials
            if email in ADMIN_CREDENTIALS:
                if password == ADMIN_CREDENTIALS[email]['password']:
                    # Use hardcoded user data (don't require database)
                    user_id = 'admin-001'
                    full_name = ADMIN_CREDENTIALS[email]['full_name']
                    role = ADMIN_CREDENTIALS[email]['role']
                    
                    # Try to get from database if Supabase is available
                    if self.supabase:
                        try:
                            result = self.supabase.table('admin_users').select('*').eq('email', email).eq('is_active', True).execute()
                            if result.data and len(result.data) > 0:
                                user = result.data[0]
                                user_id = user['id']
                                full_name = user['full_name']
                                role = user['role']
                        except:
                            pass  # Use hardcoded values if DB fails
                    
                    # Generate token
                    token = self.generate_token(user_id, email, role)
                    
                    return {
                        'success': True,
                        'data': {
                            'token': token,
                            'user': {
                                'id': user_id,
                                'email': email,
                                'full_name': full_name,
                                'role': role
                            }
                        }
                    }
                else:
                    return {'success': False, 'error': 'Invalid credentials'}
            
            return {'success': False, 'error': 'Invalid credentials'}
            
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_dashboard_stats(self):
        """Get dashboard statistics"""
        try:
            if not self.supabase:
                # Return demo data if Supabase is not available
                return {
                    'success': True,
                    'data': {
                        'total_bookings': 0,
                        'confirmed_bookings': 0,
                        'total_revenue': 0,
                        'pending_cancellations': 0,
                        'recent_bookings': [],
                        'new_customers': 0,
                        'message': 'Running in demo mode (Database offline)'
                    }
                }

            # Total bookings
            total_bookings = self.supabase.table('bookings').select('id', count='exact').execute()
            
            # Confirmed bookings
            confirmed = self.supabase.table('bookings').select('id', count='exact').eq('status', 'confirmed').execute()
            
            # Total revenue (sum of total_price for confirmed bookings)
            revenue_result = self.supabase.table('bookings').select('total_price').eq('status', 'confirmed').execute()
            total_revenue = sum(float(b.get('total_price', 0) or 0) for b in revenue_result.data)
            
            # Pending cancellations
            pending_cancellations = self.supabase.table('cancellation_requests').select('id', count='exact').eq('refund_status', 'pending').execute()
            
            # Recent bookings
            recent = self.supabase.table('bookings').select('*').order('created_at', desc=True).limit(10).execute()
            
            return {
                'success': True,
                'data': {
                    'total_bookings': total_bookings.count or 0,
                    'confirmed_bookings': confirmed.count or 0,
                    'total_revenue': round(total_revenue, 2),
                    'pending_cancellations': pending_cancellations.count or 0,
                    'recent_bookings': recent.data,
                    'new_customers': 0 # Fallback
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def log_activity(self, admin_id, action, target_type=None, target_id=None, details=None, ip_address=None):
        """Log admin activity"""
        try:
            if not self.supabase:
                return
            self.supabase.table('admin_activity_logs').insert({
                'admin_id': admin_id,
                'action': action,
                'target_type': target_type,
                'target_id': target_id,
                'details': details,
                'ip_address': ip_address
            }).execute()
        except:
            pass  # Don't fail the main operation if logging fails


def require_auth(required_role=None):
    """Decorator to require authentication"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            token = request.headers.get('Authorization', '').replace('Bearer ', '')
            
            if not token:
                return jsonify({'success': False, 'error': 'No token provided'}), 401
            
            from flask import current_app
            admin_service = current_app.config.get('ADMIN_SERVICE')
            
            result = admin_service.verify_token(token)
            if not result['success']:
                return jsonify(result), 401
            
            # Check role if specified
            if required_role and result['data']['role'] not in required_role:
                return jsonify({'success': False, 'error': 'Insufficient permissions'}), 403
            
            # Attach user info to request
            request.admin_user = result['data']
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator
