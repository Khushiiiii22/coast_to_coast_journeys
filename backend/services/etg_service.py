"""
C2C Journeys - ETG API Service
Handles all ETG/RateHawk API v3 operations for hotel bookings
Updated to match ETG Sandbox API documentation (23 endpoints)
"""
import requests
import base64
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import uuid
import sys
import os
import json
import logging

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config

# Setup detailed ETG API logging
etg_logger = logging.getLogger('etg_api')
etg_logger.setLevel(logging.DEBUG)

# Create logs directory if it doesn't exist
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'logs')
os.makedirs(log_dir, exist_ok=True)

# File handler for ETG API logs
log_file = os.path.join(log_dir, 'etg_api_logs.json')
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)
etg_logger.addHandler(file_handler)

# Console handler for immediate feedback
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_formatter = logging.Formatter('%(asctime)s - ETG API - %(levelname)s - %(message)s')
console_handler.setFormatter(console_formatter)
etg_logger.addHandler(console_handler)


class ETGApiService:
    """Service class for ETG/RateHawk API v3 operations"""
    
    def __init__(self):
        """Initialize ETG API service"""
        self.base_url = Config.ETG_API_BASE_URL.rstrip('/')
        self.key_id = Config.ETG_API_KEY_ID
        self.key_secret = Config.ETG_API_KEY_SECRET
        
        # Configure Proxy for Static IP (RateHawk Whitelist)
        self.proxy_url = Config.PROXY_URL
        self.proxies = None
        if self.proxy_url:
            self.proxies = {
                "http": self.proxy_url,
                "https": self.proxy_url
            }
            print(f"✅ Static IP Proxy configured")
        
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate API credentials are configured"""
        if not self.key_id or not self.key_secret:
            print("⚠️  Warning: ETG API credentials not configured")
        else:
            print(f"✅ ETG API configured: {self.base_url}")
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for ETG API"""
        if not self.key_id or not self.key_secret:
            raise ValueError("ETG API credentials not configured")
        
        credentials = f"{self.key_id}:{self.key_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _log_api_call(self, endpoint: str, request_data: dict, response_data: dict, status_code: int, duration_ms: float):
        """Log detailed API call information for debugging"""
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "endpoint": endpoint,
            "url": f"{self.base_url}{endpoint}",
            "request": request_data,
            "response": response_data,
            "status_code": status_code,
            "duration_ms": round(duration_ms, 2)
        }
        
        # Write to log file as JSON line
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry, indent=2, default=str) + "\n---\n")
        
        # Console output
        print(f"📝 ETG API LOG: {endpoint} | Status: {status_code} | Duration: {duration_ms:.0f}ms")
        
        return log_entry
    
    def _make_request(self, endpoint: str, data: dict = None, method: str = "POST") -> dict:
        """Make a request to ETG API with detailed logging"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        
        start_time = datetime.now()
        
        try:
            print(f"🔄 ETG API Request: {method} {endpoint}")
            print(f"📤 Request Data: {json.dumps(data, indent=2, default=str) if data else 'None'}")
            
            if method == "GET":
                response = requests.get(url, headers=headers, proxies=self.proxies, timeout=30)
            else:
                response = requests.post(url, json=data or {}, headers=headers, proxies=self.proxies, timeout=30)
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            response_json = response.json() if response.content else {}
            
            # Log the API call
            self._log_api_call(endpoint, data or {}, response_json, response.status_code, duration_ms)
            
            print(f"📥 Response Status: {response.status_code}")
            
            response.raise_for_status()
            return {
                "success": True,
                "data": response_json,
                "status_code": response.status_code
            }
        except requests.exceptions.Timeout:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_api_call(endpoint, data or {}, {"error": "Timeout"}, 408, duration_ms)
            return {"success": False, "error": "Request timeout", "status_code": 408}
        except requests.exceptions.HTTPError as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            error_response = None
            try:
                error_response = e.response.json() if e.response else None
            except:
                error_response = e.response.text if e.response else None
            
            self._log_api_call(endpoint, data or {}, error_response or {"error": str(e)}, 
                             e.response.status_code if e.response else 500, duration_ms)
            
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if e.response else 500,
                "response": error_response
            }
        except Exception as e:
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            self._log_api_call(endpoint, data or {}, {"error": str(e)}, 500, duration_ms)
            return {"success": False, "error": str(e), "status_code": 500}
    
    # ==========================================
    # ENDPOINT 1: GET - Retrieve API Overview
    # ==========================================
    
    def get_overview(self) -> dict:
        """
        Endpoint 1: Retrieve API endpoints overview
        GET /overview/
        """
        return self._make_request("/overview/", method="GET")
    
    # ==========================================
    # STATIC DATA ENDPOINTS (2-8)
    # ==========================================
    
    def get_hotel_dump(self, language: str = "en", inventory: str = "all") -> dict:
        """
        Endpoint 2: Retrieve hotel dump
        POST /hotel/dump/
        """
        data = {
            "inventory": inventory,
            "language": language
        }
        return self._make_request("/hotel/dump/", data)
    
    def get_hotel_incremental_dump(self, language: str = "en") -> dict:
        """
        Endpoint 3: Retrieve hotel incremental dump
        POST /hotel/dump/incremental/
        """
        data = {"language": language}
        return self._make_request("/hotel/dump/incremental/", data)
    
    def get_hotel_reviews_dump(self, language: str = "en") -> dict:
        """
        Endpoint 4: Retrieve hotel reviews' dump
        POST /hotel/reviews/dump/
        """
        data = {"language": language}
        return self._make_request("/hotel/reviews/dump/", data)
    
    def get_regions_dump(self, language: str = "en") -> dict:
        """
        Endpoint 5: Retrieve regions' dump
        POST /region/dump/
        """
        data = {"language": language}
        return self._make_request("/region/dump/", data)
    
    def get_hotel_reviews_incremental_dump(self, language: str = "en") -> dict:
        """
        Endpoint 6: Retrieve hotel reviews' incremental dump
        POST /hotel/reviews/dump/incremental/
        """
        data = {"language": language}
        return self._make_request("/hotel/reviews/dump/incremental/", data)
    
    def get_hotel_static(self, hotel_id: str, language: str = "en") -> dict:
        """
        Endpoint 7: Retrieve hotel static data
        GET /hotel/static/
        """
        return self._make_request(f"/hotel/static/?id={hotel_id}&language={language}", method="GET")
    
    def get_hotel_content(self, hotel_id: str, language: str = "en") -> dict:
        """
        Endpoint 8: Retrieve hotel content
        GET /hotel/content/
        """
        return self._make_request(f"/hotel/content/?id={hotel_id}&language={language}", method="GET")

    def get_hotels_static(self, hotel_ids: List[str], language: str = "en") -> dict:
        """
        Batch retrieve hotel static data for multiple IDs
        Used to enrich search results with names/images
        POST /hotel/info/
        """
        data = {
            "ids": hotel_ids,
            "language": language
        }
        # Assuming the batch endpoint is /hotel/info/ as per standard RateHawk V3 patterns for lists
        # If specific endpoint differs, this may need adjustment. Using content/ as fallback pattern if needed.
        # But for RateHawk V3, /hotel/info/ is often used for bulk details.
        return self._make_request("/hotel/info/", data)
    
    # ==========================================
    # SEARCH ENDPOINTS (9-14)
    # ==========================================
    
    def search_by_hotels(
        self,
        hotel_ids: List[str],
        checkin: str,
        checkout: str,
        guests: List[Dict],
        currency: str = "INR",
        residency: str = "in",
        language: str = "en"
    ) -> dict:
        """
        Endpoint 9: Search by hotel IDs
        POST /search/serp/hotels/
        """
        if len(hotel_ids) > 300:
            hotel_ids = hotel_ids[:300]
        
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guests,
            "ids": hotel_ids,
            "currency": currency
        }
        return self._make_request("/search/serp/hotels/", data)
    
    def search_by_geo(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        checkin: str,
        checkout: str,
        guests: List[Dict],
        currency: str = "USD",
        residency: str = "gb",
        language: str = "en",
        limit: int = 500
    ) -> dict:
        """
        Endpoint 10: Search by geo coordinates
        POST /search/serp/geo/
        """
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guests,
            "latitude": latitude,
            "longitude": longitude,
            "radius": radius,
            "currency": currency,
            "limit": limit,
            "page_size": limit,
            "rows": limit
        }
        return self._make_request("/search/serp/geo/", data)
    
    def search_by_region(
        self,
        region_id: int,
        checkin: str,
        checkout: str,
        guests: List[Dict],
        currency: str = "USD",
        residency: str = "gb",
        language: str = "en",
        limit: int = 500
    ) -> dict:
        """
        Endpoint 11: Search by region
        POST /search/serp/region/
        """
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guests,
            "region_id": region_id,
            "currency": currency,
            "limit": limit,
            "page_size": limit,
            "rows": limit
        }
        return self._make_request("/search/serp/region/", data)
    
    def sort_hotels(self, hotels: List[Dict], sort_by: str = "price") -> dict:
        """
        Endpoint 12: Sort hotels
        POST /search/sort/
        """
        data = {
            "hotels": hotels,
            "sort_by": sort_by
        }
        return self._make_request("/search/sort/", data)
    
    def suggest(self, query: str, language: str = "en") -> dict:
        """
        Suggest hotels and regions (autocomplete)
        POST /search/multicomplete/
        """
        data = {
            "query": query,
            "language": language
        }
        return self._make_request("/search/multicomplete/", data)
    
    def get_hotel_page(
        self,
        hotel_id: str,
        checkin: str,
        checkout: str,
        guests: List[Dict],
        currency: str = "INR",
        residency: str = "in",
        language: str = "en"
    ) -> dict:
        """
        Endpoint 14: Retrieve hotel page
        POST /search/hp/
        """
        data = {
            "id": hotel_id,
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guests,
            "currency": currency
        }
        return self._make_request("/search/hp/", data)
    
    # ==========================================
    # PREBOOK ENDPOINTS (15-17)
    # ==========================================
    
    def prebook(self, book_hash: str, price_increase_percent: int = 5) -> dict:
        """
        Prebook rate - check availability and final price
        POST /hotel/prebook/
        """
        data = {
            "hash": book_hash,
            "price_increase_percent": price_increase_percent
        }
        return self._make_request("/hotel/prebook/", data)
    
    def get_rate_info(self, book_hash: str) -> dict:
        """
        Endpoint 17: Retrieve rate info
        POST /rate/info/
        """
        data = {"hash": book_hash}
        return self._make_request("/rate/info/", data)
    
    # ==========================================
    # BOOKING ENDPOINTS (18-23)
    # ==========================================
    
    def create_booking(
        self,
        book_hash: str,
        partner_order_id: str,
        guests: List[Dict],
        user_ip: str = "127.0.0.1",
        payment_type: str = "now"
    ) -> dict:
        """
        Create booking - form order
        POST /hotel/order/booking/form/
        """
        data = {
            "hash": book_hash,
            "partner_order_id": partner_order_id,
            "payment_type": {"type": payment_type},
            "user_ip": user_ip,
            "rooms": [{"guests": guests}],
            "user": {
                "email": Config.CORPORATE_EMAIL,
                "phone": "0000000000",  # Placeholder required by some APIs
                "first_name": "C2C",
                "last_name": "Bookings"
            }
        }
        return self._make_request("/hotel/order/booking/form/", data)
    
    def finish_booking(self, partner_order_id: str) -> dict:
        """
        Finish/Start booking process
        POST /hotel/order/booking/finish/
        """
        data = {"partner_order_id": partner_order_id}
        return self._make_request("/hotel/order/booking/finish/", data)
    
    def check_booking_status(self, partner_order_id: str) -> dict:
        """
        Check booking status
        POST /hotel/order/booking/finish/status/
        """
        data = {"partner_order_id": partner_order_id}
        return self._make_request("/hotel/order/booking/finish/status/", data)
    
    def get_booking_info(self, partner_order_id: str) -> dict:
        """
        Get booking information
        POST /hotel/order/info/
        """
        data = {"partner_order_id": partner_order_id}
        return self._make_request("/hotel/order/info/", data)
    
    def cancel_booking(self, partner_order_id: str) -> dict:
        """
        Cancel booking
        POST /hotel/order/cancel/
        """
        data = {"partner_order_id": partner_order_id}
        return self._make_request("/hotel/order/cancel/", data)
    
    # ==========================================
    # UTILITY METHODS
    # ==========================================
    
    @staticmethod
    def generate_partner_order_id() -> str:
        """Generate a unique partner order ID"""
        return f"CTC-{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8].upper()}"
    
    @staticmethod
    def format_guests_for_search(adults: int, children_ages: List[int] = None) -> List[Dict]:
        """
        Format guest configuration for search API
        """
        if children_ages is None:
            children_ages = []
        
        return [{
            "adults": adults,
            "children": children_ages
        }]
    
    @staticmethod
    def format_guests_for_booking(guest_list: List[Dict]) -> List[Dict]:
        """
        Format guest details for booking API
        """
        return guest_list


# Singleton instance
etg_service = ETGApiService()
