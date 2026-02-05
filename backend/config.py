"""
C2C Journeys - Configuration
Handles all environment variables and configuration
"""
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Base configuration class"""
    
    # Flask Configuration
    SECRET_KEY = os.getenv('FLASK_SECRET_KEY', 'dev-secret-key')
    DEBUG = os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    
    # Server Configuration
    HOST = os.getenv('HOST', '0.0.0.0')
    PORT = int(os.getenv('PORT', 5000))
    
    # ETG/RateHawk API Configuration
    ETG_API_KEY_ID = os.getenv('ETG_API_KEY_ID')
    ETG_API_KEY_SECRET = os.getenv('ETG_API_KEY_SECRET')
    ETG_API_BASE_URL = os.getenv('ETG_API_BASE_URL', 'https://api.worldota.net/api/b2b/v3')
    
    # Supabase Configuration
    SUPABASE_URL = os.getenv('SUPABASE_URL')
    SUPABASE_ANON_KEY = os.getenv('SUPABASE_ANON_KEY')
    SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
    
    # Google Maps Configuration
    GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY')
    
    # Razorpay Payment Gateway Configuration
    RAZORPAY_KEY_ID = os.getenv('RAZORPAY_KEY_ID')
    RAZORPAY_KEY_SECRET = os.getenv('RAZORPAY_KEY_SECRET')
    RAZORPAY_WEBHOOK_SECRET = os.getenv('RAZORPAY_WEBHOOK_SECRET')
    
    # PayPal Payment Gateway Configuration
    PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
    PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
    PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')
    
    # Email/SMTP Configuration (GoDaddy)
    MAIL_SERVER = os.getenv('MAIL_SERVER', 'smtpout.secureserver.net')
    MAIL_PORT = int(os.getenv('MAIL_PORT', 465))
    MAIL_USE_TLS = os.getenv('MAIL_USE_TLS', 'False').lower() == 'true'
    MAIL_USE_SSL = os.getenv('MAIL_USE_SSL', 'True').lower() == 'true'
    MAIL_USERNAME = os.getenv('MAIL_USERNAME')
    MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')
    MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER')
    RESEND_API_KEY = os.getenv('RESEND_API_KEY')
    
    # Static IP Proxy Configuration (QuotaGuard Static or Fixie)
    PROXY_URL = os.getenv('QUOTAGUARDSTATIC_URL', os.getenv('FIXIE_URL'))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        required_vars = [
            ('SUPABASE_URL', cls.SUPABASE_URL),
            ('SUPABASE_ANON_KEY', cls.SUPABASE_ANON_KEY),
        ]
        
        missing = [name for name, value in required_vars if not value]
        
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")
        
        # Warn about optional but important configurations
        if not cls.ETG_API_KEY_ID or not cls.ETG_API_KEY_SECRET:
            print("⚠️  Warning: ETG API credentials not configured. Hotel booking features will be limited.")
        
        if not cls.GOOGLE_MAPS_API_KEY:
            print("⚠️  Warning: Google Maps API key not configured. Map features will be disabled.")
        
        return True


class DevelopmentConfig(Config):
    """Development configuration"""
    DEBUG = True


class ProductionConfig(Config):
    """Production configuration"""
    DEBUG = False


# Configuration dictionary
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}


def get_config():
    """Get configuration based on environment"""
    env = os.getenv('FLASK_ENV', 'development')
    return config.get(env, config['default'])
