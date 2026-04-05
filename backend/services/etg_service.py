"""
C2C Journeys - ETG API Service
Handles all ETG/RateHawk API v3 operations for hotel bookings
Updated to match ETG Sandbox API documentation (23 endpoints)
"""
import requests
import base64
from datetime import datetime, date
import traceback
import hashlib
from cachetools import TTLCache
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
            
        # Sandbox Quota Workaround (Cache for 10 minutes)
        self.search_cache = TTLCache(maxsize=100, ttl=600)
        
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
    
    def _make_request(self, endpoint: str, data: dict = None, method: str = "POST", timeout: int = 30, retry_count: int = 0) -> dict:
        """Make a request to ETG API with detailed logging"""
        
        # ⚡ Cache Interception for strict ETG Sandbox quotas
        cache_key = None
        if method == "POST" and any(ep in endpoint for ep in ["/search/serp/region/", "/search/serp/hotels/", "/search/hp/", "/search/serp/geo/"]):
            # Normalize and stringify data
            cache_key = hashlib.md5(f"{endpoint}_{json.dumps(data or {}, sort_keys=True)}".encode('utf-8')).hexdigest()
            if cache_key in self.search_cache:
                print(f"⚡ CACHE HIT: Returning cached API result for {endpoint} (Bypassing Sandbox Quota)")
                return self.search_cache[cache_key]

        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        
        start_time = datetime.now()
        
        try:
            print(f"🔄 ETG API Request: {method} {endpoint} (timeout: {timeout}s)")
            print(f"📤 Request Data: {json.dumps(data, indent=2, default=str) if data else 'None'}")
            
            if method == "GET":
                response = requests.get(url, headers=headers, proxies=self.proxies, timeout=timeout)
            else:
                response = requests.post(url, json=data or {}, headers=headers, proxies=self.proxies, timeout=timeout)
            
            duration_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            response_json = response.json() if response.content else {}
            
            # Log the API call
            self._log_api_call(endpoint, data or {}, response_json, response.status_code, duration_ms)
            
            print(f"📥 Response Status: {response.status_code}")
            
            response.raise_for_status()
            
            # --- Transparent Quota Retry Logic (Sandbox Only) ---
            if response_json.get("status") == "error" and response_json.get("error") == "too_many_requests":
                if retry_count < 2:
                    sleep_sec = 20
                    print(f"⚠️ Sandbox Quota Exceeded! Sleeping for {sleep_sec}s to automatically bypass this for QA...")
                    import time
                    time.sleep(sleep_sec)
                    print(f"🔄 Retrying {endpoint} after quota reset wait...")
                    return self._make_request(endpoint, data, method, timeout, retry_count + 1)
            # ----------------------------------------------------
            
            result = {
                "success": True,
                "data": response_json,
                "status_code": response.status_code
            }
            
            if cache_key:
                self.search_cache[cache_key] = result
                
            return result
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
        Fetch hotel static data for multiple IDs
        Used to enrich search results with names/images
        
        RateHawk /hotel/info/ takes a single 'id' per request.
        We iterate over hotel IDs and collect results.
        """
        all_hotel_data = {}
        
        for hotel_id in hotel_ids:
            try:
                data = {
                    "id": hotel_id,
                    "language": language
                }
                result = self._make_request("/hotel/info/", data, timeout=10)
                
                if result.get('success') and result.get('data'):
                    response_data = result['data']
                    # RateHawk wraps response in 'data' key
                    hotel_info = response_data.get('data', response_data)
                    
                    if isinstance(hotel_info, dict):
                        # Extract images from images_ext (modern) or images (deprecated)
                        images = []
                        
                        # Prefer images_ext (categorized images - modern field)
                        images_ext = hotel_info.get('images_ext', {})
                        if images_ext and isinstance(images_ext, dict):
                            # images_ext is a dict with categories: exterior, guest_rooms, lobby, pool, etc.
                            for category, img_list in images_ext.items():
                                if isinstance(img_list, list):
                                    for img in img_list:
                                        if isinstance(img, str) and img:
                                            images.append(img)
                                        elif isinstance(img, dict) and img.get('url'):
                                            images.append(img['url'])
                        
                        # Fallback to deprecated images field
                        if not images:
                            raw_images = hotel_info.get('images', [])
                            if isinstance(raw_images, list):
                                for img in raw_images:
                                    if isinstance(img, str) and img:
                                        images.append(img)
                                    elif isinstance(img, dict) and img.get('url'):
                                        images.append(img['url'])
                        
                        # Store hotel info with extracted images
                        hotel_info['images'] = images
                        hotel_info['id'] = hotel_id
                        all_hotel_data[hotel_id] = hotel_info
                        
                        if images:
                            print(f"📸 Got {len(images)} images for hotel {hotel_id}")
                        else:
                            print(f"⚠️ No images found for hotel {hotel_id}")
                            
            except Exception as e:
                print(f"⚠️ Failed to fetch static data for hotel {hotel_id}: {e}")
                continue
        
        # Return in a format compatible with the existing code
        return {
            'success': True,
            'data': {
                'data': all_hotel_data  # Dict keyed by hotel_id
            }
        }
    
    # ==========================================
    # SEARCH ENDPOINTS (9-14)
    # ==========================================
    
    def search_by_hotels(
        self,
        hotel_ids: List[str],
        checkin: str,
        checkout: str,
        guests: List[Dict] = None,
        rooms: List[Dict] = None,
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
        
        guest_data = guests or rooms or [{"adults": 2, "children": []}]
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guest_data,
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
        guests: List[Dict] = None,
        rooms: List[Dict] = None,
        currency: str = "USD",
        residency: str = "gb",
        language: str = "en",
        limit: int = 500
    ) -> dict:
        """
        Endpoint 10: Search by geo coordinates
        POST /search/serp/geo/
        """
        guest_data = guests or rooms or [{"adults": 2, "children": []}]
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guest_data,
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
        guests: List[Dict] = None,
        rooms: List[Dict] = None,
        currency: str = "USD",
        residency: str = "gb",
        language: str = "en",
        limit: int = 500
    ) -> dict:
        """
        Endpoint 11: Search by region
        POST /search/serp/region/
        """
        guest_data = guests or rooms or [{"adults": 2, "children": []}]
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guest_data,
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
        guests: List[Dict] = None,
        rooms: List[Dict] = None,
        currency: str = "INR",
        residency: str = "in",
        language: str = "en"
    ) -> dict:
        """
        Endpoint 14: Retrieve hotel page
        POST /search/hp/
        """
        guest_data = guests or rooms or [{"adults": 2, "children": []}]
        data = {
            "id": hotel_id,
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guest_data,
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
        guests: List[Dict] = None,
        rooms: List[Dict] = None,
        user_ip: str = "127.0.0.1",
        payment_type: str = "now",
        user_comment: str = None,
        language: str = "en"
    ) -> dict:
        """
        Create booking - form order
        POST /hotel/order/booking/form/
        
        Per ETG v3 docs, required fields:
          - partner_order_id: unique order ID (UUID format, 3-256 chars)
          - book_hash: rate ID from prebook step
        Optional:
          - rooms: list of rooms with guest details [NEW - 4th Update]
          - language: default "en"
          - user_ip: end user IP (used for CC processing with payment_type=now)
        """
        data = {
            "book_hash": book_hash,
            "partner_order_id": partner_order_id,
            "language": language,
            "user_ip": user_ip
        }
        
        # Support for multi-room guest details (4th update)
        if rooms:
            data["rooms"] = rooms
        elif guests:
            # Fallback for legacy singe-room guest list
            data["rooms"] = [{"guests": guests}]
            
        return self._make_request("/hotel/order/booking/form/", data)
    
    def finish_booking(
        self,
        partner_order_id: str,
        email: str,
        phone: str,
        guests: List[Dict] = None,
        rooms: List[Dict] = None,
        amount: float = 0,
        currency: str = "USD",
        payment_type: str = "deposit",
        user_comment: str = None,
        language: str = "en"
    ) -> dict:
        """
        Finish/Start booking process
        POST /hotel/order/booking/finish/
        """
        data = {
            "partner": {
                "partner_order_id": partner_order_id
            },
            "user": {
                "email": email,
                "phone": phone
            },
            "language": language,
            "payment_type": {
                "type": payment_type,
                "amount": str(amount),
                "currency_code": currency
            }
        }
        
        # Support for multi-room guest details (4th update)
        if rooms:
            data["rooms"] = rooms
        elif guests:
            # Fallback for legacy single-room guest list
            data["rooms"] = [{"guests": guests}]
        
        if user_comment:
            data["user"]["comment"] = user_comment
            
        return self._make_request("/hotel/order/booking/finish/", data, timeout=180)
    
    def check_booking_status(self, partner_order_id: str) -> dict:
        """
        Check booking status
        POST /hotel/order/booking/finish/status/
        Uses extended timeout (180s) as booking confirmation may take time
        """
        data = {"partner_order_id": partner_order_id}
        return self._make_request("/hotel/order/booking/finish/status/", data, timeout=180)
    
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
    def format_guests_for_search(adults: int, children_ages: List[int] = None, rooms: list = None) -> List[Dict]:
        """
        Format guest configuration for ETG v3 search API (rooms array).
        Returns a list of rooms, where each room is a dict: {"adults": N, "children": [age1, age2]}
        """
        if rooms and isinstance(rooms, list) and len(rooms) > 0 and isinstance(rooms[0], dict):
            # Formats multi-room input into ETG-compatible rooms array
            formatted_rooms = []
            for room in rooms:
                entry = {"adults": int(room.get("adults", 1))}
                child_ages = room.get("childAges", room.get("children_ages", []))
                if child_ages and isinstance(child_ages, list):
                    entry["children"] = [int(a) for a in child_ages]
                else:
                    entry["children"] = []
                formatted_rooms.append(entry)
            return formatted_rooms

        # Single-room fallback logic
        if children_ages is None:
            children_ages = []
        
        return [{
            "adults": int(adults),
            "children": [int(a) for a in children_ages]
        }]
    
    @staticmethod
    def format_guests_for_booking(guest_list: List[Dict]) -> List[Dict]:
        """
        Format guest details for booking API
        """
        return guest_list


# Singleton instance
etg_service = ETGApiService()
