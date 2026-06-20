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
    
    def generate_token(self, admin_id, email, role, auth_user_id=None):
        """Generate JWT token"""
        payload = {
            'admin_id': admin_id,
            'auth_user_id': auth_user_id,
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
    
    def login(self, email, password, mfa_code=None, ip_address=None):
        """Authenticate admin user with MFA"""
        try:
            import pyotp
            # Hardcoded admin credentials for demo
            ADMIN_CREDENTIALS = {
                'admin@coasttocoast.com': {
                    'password': 'admin123',
                    'full_name': 'Super Admin',
                    'role': 'super_admin',
                    'mfa_secret': 'JBSWY3DPEHPK3PXP' # Dummy secret for testing
                }
            }
            
            # Check hardcoded credentials
            if email in ADMIN_CREDENTIALS:
                if password == ADMIN_CREDENTIALS[email]['password']:
                    # MFA Check
                    if not mfa_code:
                        return {'success': False, 'mfa_required': True}
                        
                    totp = pyotp.TOTP(ADMIN_CREDENTIALS[email]['mfa_secret'])
                    if not totp.verify(mfa_code):
                        return {'success': False, 'error': 'Invalid Authenticator code'}
                        
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
                    token = self.generate_token(user_id, email, role, auth_user_id=user.get('user_id') if 'user' in locals() else None)
                    
                    return {
                        'success': True,
                        'data': {
                            'token': token,
                            'user': {
                                'id': user_id,
                                'auth_user_id': user.get('user_id') if 'user' in locals() else None,
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
    
    def get_admin_users(self, role=None, search=None):
        """Get list of admin users"""
        try:
            if not self.supabase:
                # Return demo data if Supabase is not available
                return {
                    'success': True,
                    'data': [
                        {
                            'id': 'admin-001',
                            'full_name': 'Super Admin',
                            'email': 'admin@coasttocoast.com',
                            'role': 'super_admin',
                            'is_active': True,
                            'created_at': datetime.datetime.now().isoformat()
                        }
                    ],
                    'count': 1
                }

            query = self.supabase.table('admin_users').select('*')
            
            if role:
                query = query.eq('role', role)
            
            if search:
                query = query.or_(f"full_name.ilike.%{search}%,email.ilike.%{search}%")
            
            query = query.order('created_at', desc=True)
            result = query.execute()
            
            return {
                'success': True,
                'data': result.data,
                'count': len(result.data)
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}

    def get_dashboard_stats(self, period='all'):
        """Get comprehensive hotel-focused dashboard statistics"""
        try:
            if not self.supabase:
                return {
                    'success': True,
                    'data': {
                        'total_bookings': 0, 'confirmed_bookings': 0, 'total_revenue': 0,
                        'pending_cancellations': 0, 'recent_bookings': [], 'new_customers': 0,
                        'avg_booking_value': 0, 'avg_nights': 0, 'total_room_nights': 0,
                        'status_breakdown': {}, 'monthly_revenue': [], 'top_destinations': [],
                        'star_rating_distribution': {}, 'currency_breakdown': {},
                        'message': 'Running in demo mode (Database offline)'
                    }
                }

            # Fetch all hotel bookings at once for efficient processing
            all_bookings = []
            try:
                query = self.supabase.table('hotel_bookings').select('*')
                
                # Apply date filter based on period
                if period == 'month':
                    start_date = (datetime.datetime.utcnow().replace(day=1)).isoformat()
                    query = query.gte('created_at', start_date)
                elif period == 'week':
                    start_date = (datetime.datetime.utcnow() - datetime.timedelta(days=7)).isoformat()
                    query = query.gte('created_at', start_date)

                res = query.order('created_at', desc=True).execute()
                all_bookings = res.data or []
            except Exception:
                pass

            total_bookings_count = len(all_bookings)

            # Status breakdown
            status_breakdown = {}
            for b in all_bookings:
                s = b.get('status', 'unknown')
                status_breakdown[s] = status_breakdown.get(s, 0) + 1

            confirmed_count = status_breakdown.get('confirmed', 0)

            # Revenue calculations
            confirmed_bookings = [b for b in all_bookings if b.get('status') == 'confirmed']
            total_revenue = sum(float(b.get('total_amount', 0) or 0) for b in confirmed_bookings)
            avg_booking_value = round(total_revenue / confirmed_count, 2) if confirmed_count > 0 else 0

            # Total revenue (all statuses for overview)
            total_revenue_all = sum(float(b.get('total_amount', 0) or 0) for b in all_bookings)

            # Average nights stayed
            total_nights = 0
            bookings_with_dates = 0
            for b in all_bookings:
                try:
                    from datetime import datetime as dt
                    ci = dt.strptime(b['check_in'], '%Y-%m-%d')
                    co = dt.strptime(b['check_out'], '%Y-%m-%d')
                    nights = (co - ci).days
                    if nights > 0:
                        total_nights += nights
                        bookings_with_dates += 1
                except Exception:
                    pass
            avg_nights = round(total_nights / bookings_with_dates, 1) if bookings_with_dates > 0 else 0

            # Total room-nights
            total_room_nights = 0
            for b in all_bookings:
                try:
                    from datetime import datetime as dt
                    ci = dt.strptime(b['check_in'], '%Y-%m-%d')
                    co = dt.strptime(b['check_out'], '%Y-%m-%d')
                    nights = max((co - ci).days, 1)
                    rooms = int(b.get('rooms', 1) or 1)
                    total_room_nights += nights * rooms
                except Exception:
                    pass

            # Monthly revenue and booking count (last 12 months)
            monthly_data = {}
            for b in all_bookings:
                try:
                    created = b.get('created_at', '')[:7]  # YYYY-MM
                    if created:
                        if created not in monthly_data:
                            monthly_data[created] = {'bookings': 0, 'revenue': 0}
                        monthly_data[created]['bookings'] += 1
                        monthly_data[created]['revenue'] += float(b.get('total_amount', 0) or 0)
                except Exception:
                    pass

            monthly_revenue = [
                {'month': k, 'bookings': v['bookings'], 'revenue': round(v['revenue'], 2)}
                for k, v in sorted(monthly_data.items())
            ]

            # Top destinations (by hotel_name since hotel_city is often null)
            destination_counts = {}
            for b in all_bookings:
                dest = b.get('hotel_city') or b.get('hotel_name') or 'Unknown'
                if dest not in destination_counts:
                    destination_counts[dest] = {'count': 0, 'revenue': 0}
                destination_counts[dest]['count'] += 1
                destination_counts[dest]['revenue'] += float(b.get('total_amount', 0) or 0)
            top_destinations = sorted(
                [{'name': k, 'bookings': v['count'], 'revenue': round(v['revenue'], 2)} for k, v in destination_counts.items()],
                key=lambda x: x['bookings'], reverse=True
            )[:10]

            # Star rating distribution
            star_distribution = {}
            for b in all_bookings:
                stars = b.get('hotel_star_rating')
                if stars:
                    key = f"{stars} Star"
                    star_distribution[key] = star_distribution.get(key, 0) + 1

            # Currency breakdown
            currency_breakdown = {}
            for b in all_bookings:
                curr = b.get('currency', 'USD')
                if curr not in currency_breakdown:
                    currency_breakdown[curr] = {'count': 0, 'revenue': 0}
                currency_breakdown[curr]['count'] += 1
                currency_breakdown[curr]['revenue'] += float(b.get('total_amount', 0) or 0)

            # Pending cancellations
            pending_cancellations_count = 0
            try:
                pending_cancellations = self.supabase.table('cancellation_requests').select('id', count='exact').eq('refund_status', 'pending').execute()
                pending_cancellations_count = pending_cancellations.count or 0
            except Exception:
                pending_cancellations_count = status_breakdown.get('cancelled', 0)

            # Recent bookings (already sorted desc)
            recent_data = all_bookings[:10]

            # Guest name extraction for recent bookings
            for b in recent_data:
                guests = b.get('guests', [])
                guest_name = 'Guest'
                if isinstance(guests, list) and guests:
                    first_room = guests[0] if isinstance(guests[0], dict) else {}
                    room_guests = first_room.get('guests', [])
                    if room_guests:
                        g = room_guests[0]
                        guest_name = f"{g.get('first_name', '')} {g.get('last_name', '')}".strip()
                b['guest_name'] = guest_name if guest_name else 'Guest'

            # New customer count (last 30 days)
            new_customers = 0
            try:
                from datetime import datetime as dt, timedelta
                thirty_days_ago = (dt.utcnow() - timedelta(days=30)).isoformat()
                cust_res = self.supabase.table('customers').select('id', count='exact').gte('created_at', thirty_days_ago).execute()
                new_customers = cust_res.count or 0
            except Exception:
                pass

            return {
                'success': True,
                'data': {
                    'total_bookings': total_bookings_count,
                    'confirmed_bookings': confirmed_count,
                    'total_revenue': round(total_revenue, 2),
                    'total_revenue_all': round(total_revenue_all, 2),
                    'avg_booking_value': avg_booking_value,
                    'pending_cancellations': pending_cancellations_count,
                    'recent_bookings': recent_data,
                    'new_customers': new_customers,
                    'avg_nights': avg_nights,
                    'total_room_nights': total_room_nights,
                    'status_breakdown': status_breakdown,
                    'monthly_revenue': monthly_revenue,
                    'top_destinations': top_destinations,
                    'star_rating_distribution': star_distribution,
                    'currency_breakdown': currency_breakdown,
                    'failed_bookings': status_breakdown.get('failed', 0),
                    'created_bookings': status_breakdown.get('created', 0)
                }
            }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    # Get finance data (invoices or refunds)
    def get_finance_data(self, type='invoices'):
        try:
            results = []
            
            # Fetch Hotels
            hotel_query = self.supabase.table('hotel_bookings').select('*')
            if type == 'invoices':
                hotel_query = hotel_query.eq('payment_status', 'paid')
            elif type == 'refunds':
                hotel_query = hotel_query.not_.is_('refund_status', 'null')
            
            hotels = hotel_query.order('created_at', desc=True).limit(50).execute()
            for h in hotels.data:
                h['service_type'] = 'hotel'
                results.append(h)
                
            # Fetch Flights
            flight_query = self.supabase.table('flight_bookings').select('*')
            if type == 'invoices':
                flight_query = flight_query.eq('payment_status', 'paid')
            elif type == 'refunds':
                flight_query = flight_query.not_.is_('refund_status', 'null')
                
            flights = flight_query.order('created_at', desc=True).limit(50).execute()
            for f in flights.data:
                f['service_type'] = 'flight'
                results.append(f)
                
            # Sort combined results by created_at
            results.sort(key=lambda x: x.get('created_at', ''), reverse=True)
            
            return results
            
        except Exception as e:
            print(f"Error getting finance data: {e}")
            return []

    # Get suppliers
    def get_suppliers(self):
        try:
            result = self.supabase.table('suppliers').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Error getting suppliers: {e}")
            return []

    # Log admin activity
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
