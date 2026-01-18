"""
Coast to Coast Journeys - Flask Backend Application
Main entry point for the API server
"""
import os
import sys

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, jsonify
from flask_cors import CORS
from config import Config, get_config

# Import routes
from routes.hotel_routes import hotel_bp
from routes.maps_routes import maps_bp
from routes.flight_routes import flight_bp


def create_app():
    """Application factory"""
    # Get parent directory for serving frontend static files
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    app = Flask(__name__, 
                static_folder=parent_dir,
                static_url_path='')
    
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
    
    # Serve frontend pages
    @app.route('/')
    def serve_index():
        return app.send_static_file('index.html')
    
    @app.route('/<path:filename>')
    def serve_static(filename):
        # Serve HTML files and other static assets
        if filename.endswith('.html') or '.' not in filename:
            try:
                return app.send_static_file(filename if filename.endswith('.html') else f'{filename}.html')
            except:
                pass
        return app.send_static_file(filename)
    
    # Health check endpoint
    @app.route('/api/health', methods=['GET'])
    def health_check():
        return jsonify({
            'status': 'healthy',
            'service': 'Coast to Coast Journeys API',
            'version': '1.0.0'
        })
    
    # API info endpoint
    @app.route('/api', methods=['GET'])
    def api_info():
        return jsonify({
            'name': 'Coast to Coast Journeys API',
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
        return jsonify({
            'success': False,
            'error': 'Endpoint not found'
        }), 404
    
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
    print("🚀 Starting Coast to Coast Journeys API Server...")
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
