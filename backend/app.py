"""
C2C Journeys - Flask Backend Application
Main entry point for the API server
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS
from config import Config, get_config

# Import routes
from routes.hotel_routes import hotel_bp
from routes.maps_routes import maps_bp
from routes.flight_routes import flight_bp
from routes.admin_routes import admin_bp
from routes.payment_routes import payment_bp
from routes.auth_routes import auth_bp
from routes.visa_routes import visa_bp


def create_app():
    """Application factory"""
    # Get parent directory for serving frontend static files
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_folder = os.path.join(parent_dir, 'templates')
    
    # Configure Flask without automatic static file serving
    # We'll handle static files manually through routes
    app = Flask(__name__, 
                static_folder=None,
                template_folder=templates_folder)
    
    # Load configuration
    config_class = get_config()
    app.config.from_object(config_class)
    
    # Validate configuration
    try:
        config_class.validate()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        sys.exit(1)
    
    # Enable CORS for all origins (development)
    CORS(app, resources={
        r"/api/*": {
            "origins": "*",
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })
    
    # Register blueprints
    app.register_blueprint(hotel_bp)
    app.register_blueprint(maps_bp)
    app.register_blueprint(flight_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(payment_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(visa_bp)
    
    # Initialize admin service
    from services.admin_service import AdminService
    from services.supabase_service import supabase_service
    
    admin_service = AdminService(supabase_service.client, app.config['SECRET_KEY'])
    app.config['ADMIN_SERVICE'] = admin_service
    app.config['SUPABASE'] = supabase_service.client
    
    # Initialize Razorpay service
    from services.razorpay_service import RazorpayService
    razorpay_key = app.config.get('RAZORPAY_KEY_ID')
    razorpay_secret = app.config.get('RAZORPAY_KEY_SECRET')
    
    if razorpay_key and razorpay_secret:
        razorpay_service = RazorpayService(razorpay_key, razorpay_secret)
        app.config['RAZORPAY_SERVICE'] = razorpay_service
        print("✅ Razorpay payment service initialized")
    else:
        print("⚠️  Warning: Razorpay credentials not found in .env")
    
    # Initialize PayPal service
    from services.paypal_service import PayPalService
    paypal_client_id = app.config.get('PAYPAL_CLIENT_ID')
    paypal_secret = app.config.get('PAYPAL_CLIENT_SECRET')
    paypal_mode = app.config.get('PAYPAL_MODE', 'sandbox')
    
    if paypal_client_id and paypal_secret:
        paypal_service = PayPalService(paypal_client_id, paypal_secret, paypal_mode)
        app.config['PAYPAL_SERVICE'] = paypal_service
        print(f"✅ PayPal payment service initialized ({paypal_mode} mode)")
    else:
        print("⚠️  Warning: PayPal credentials not found in .env")
    
    # Initialize Email service
    from services.email_service import email_service
    email_service.init_app(app)
    print(f"🔑 Resend API Key loaded: {bool(app.config.get('RESEND_API_KEY'))}")
    
    # Define directories
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    templates_dir = os.path.join(base_dir, 'templates')
    print(f"📁 Templates directory: {templates_dir}")
    print(f"📁 Templates exists: {os.path.exists(templates_dir)}")
    
    # Serve frontend pages
    @app.route('/')
    def serve_index():
        try:
            return send_from_directory(templates_dir, 'index.html')
        except Exception as e:
            print(f"❌ Error serving index.html: {e}")
            return "index.html not found in templates directory", 404
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        print(f"🔍 Requesting: {filename}")
        
        # 1. Try to serve from templates if it's an HTML file or has no extension  
        if filename.endswith('.html') or '.' not in filename:
            target = filename if filename.endswith('.html') else f"{filename}.html"
            print(f"📄 Trying to serve HTML: {target}")
            print(f"📁 From directory: {templates_dir}")
            
            full_path = os.path.join(templates_dir, target)
            print(f"🔎 Full path: {full_path}")
            print(f"✓ Exists: {os.path.exists(full_path)}")
            
            try:
                # Check if it's in admin subfolder
                if filename.startswith('admin/'):
                    return send_from_directory(os.path.join(templates_dir, 'admin'), target.replace('admin/', ''))
                else:
                    result = send_from_directory(templates_dir, target)
                    print(f"✅ Successfully served from templates")
                    return result
            except Exception as e:
                print(f"❌ Error serving from templates: {e}")
                pass # Fall through to next checks
        
        # 2. Try to serve from css, js, or assets folders
        for folder in ['css', 'js', 'assets']:
            if filename.startswith(f"{folder}/"):
                try:
                    return send_from_directory(base_dir, filename)
                except:
                    pass

        # Special handling for admin static files (css/js) which are in root/admin not templates/admin
        if filename.startswith('admin/css/') or filename.startswith('admin/js/'):
            try:
                # remove 'admin/' prefix to find in admin subdirectory of base_dir
                # actually send_from_directory(base_dir, filename) works if filename includes 'admin/...'
                # providing the folder 'admin' exists in base_dir
                return send_from_directory(base_dir, filename)
            except Exception as e:
                print(f"Error serving admin static: {e}")
                pass
        
        # 3. Last fallback: try to serve from project root
        try:
            return send_from_directory(base_dir, filename)
        except:
            return f"File '{filename}' not found", 404

    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'C2C Journeys API',
            'version': '1.0.0'
        })
    
    # Static IP Test Endpoint - IMPORTANT for RateHawk Production
    @app.route('/api/test/static-ip', methods=['GET'])
    def test_static_ip():
        """Test endpoint to verify static IP configuration for RateHawk whitelisting"""
        import requests
        
        result = {
            'proxy_configured': Config.PROXY_URL is not None,
            'proxy_url_set': bool(Config.PROXY_URL)
        }
        
        try:
            # Test without proxy
            response_no_proxy = requests.get('https://api.ipify.org?format=json', timeout=10)
            result['ip_without_proxy'] = response_no_proxy.json().get('ip')
        except Exception as e:
            result['ip_without_proxy'] = f"Error: {str(e)}"
        
        # Test with proxy if configured
        if Config.PROXY_URL:
            try:
                proxies = {
                    'http': Config.PROXY_URL,
                    'https': Config.PROXY_URL
                }
                response_with_proxy = requests.get('https://api.ipify.org?format=json', 
                                                   proxies=proxies, timeout=10)
                result['ip_with_proxy'] = response_with_proxy.json().get('ip')
                result['static_ip_working'] = True
                result['message'] = f'✅ Static IP configured: {result["ip_with_proxy"]}'
                result['instructions'] = 'Send this IP to RateHawk for production whitelisting'
            except Exception as e:
                result['ip_with_proxy'] = f"Error: {str(e)}"
                result['static_ip_working'] = False
                result['message'] = 'Proxy configured but not working'
        else:
            result['message'] = '⚠️ No proxy configured. Add QUOTAGUARDSTATIC_URL to Render environment variables.'
            result['instructions'] = 'See docs/RENDER_STATIC_IP_SETUP.md for setup guide'
        
        return jsonify(result)
    
    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        return jsonify({
            'name': 'C2C Journeys API',
            'version': '1.0.0',
            'endpoints': {
                'health': '/api/health',
                'hotels_search_region': 'POST /api/hotels/search/region',
                'hotels_search_geo': 'POST /api/hotels/search/geo',
                'hotels_search_destination': 'POST /api/hotels/search/destination',
                'hotels_details': 'POST /api/hotels/details',
                'hotels_prebook': 'POST /api/hotels/prebook',
                'hotels_book': 'POST /api/hotels/book',
                'hotels_book_finish': 'POST /api/hotels/book/finish',
                'hotels_book_status': 'POST /api/hotels/book/status',
                'hotels_cancel': 'POST /api/hotels/booking/cancel',
                'maps_geocode': 'POST /api/maps/geocode',
                'maps_search': 'POST /api/maps/search',
                'maps_distance': 'POST /api/maps/distance'
            }
        })
    
    # Error handlers
    @app.errorhandler(404)
    def not_found(error):
        # Only return JSON if it's an API request
        from flask import request
        if request.path.startswith('/api/'):
            return jsonify({
                'success': False,
                'error': 'API Endpoint not found'
            }), 404
        
        # Otherwise, serve custom 404 page
        try:
            return send_from_directory(templates_dir, '404.html'), 404
        except:
            return f"The page you are looking for ({request.path}) was not found.", 404
    
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            'success': False,
            'error': 'Internal server error'
        }), 500
    
    return app


# Create app instance
app = create_app()


if __name__ == '__main__':
    print("🚀 Starting C2C Journeys API Server...")
    print(f"📍 Running on http://{Config.HOST}:{Config.PORT}")
    print(f"🔧 Debug mode: {Config.DEBUG}")
    print("\n📚 API Documentation:")
    print("   GET  /api              - API info and endpoints")
    print("   GET  /api/health       - Health check")
    print("   POST /api/hotels/...   - Hotel endpoints")
    print("   POST /api/maps/...     - Maps endpoints")
    print()
    
    app.run(
        host=Config.HOST,
        port=Config.PORT,
        debug=Config.DEBUG
    )
