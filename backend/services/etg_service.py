"""
Coast to Coast Journeys - ETG API Service
Handles all ETG/RateHawk API v3 operations for hotel bookings
"""
import requests
import base64
from datetime import datetime, date
from typing import Optional, List, Dict, Any
import uuid
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class ETGApiService:
    """Service class for ETG/RateHawk API v3 operations"""
    
    def __init__(self):
        """Initialize ETG API service"""
        self.base_url = Config.ETG_API_BASE_URL
        self.key_id = Config.ETG_API_KEY_ID
        self.key_secret = Config.ETG_API_KEY_SECRET
        self._validate_credentials()
    
    def _validate_credentials(self):
        """Validate API credentials are configured"""
        if not self.key_id or not self.key_secret:
            print("⚠️  Warning: ETG API credentials not configured")
    
    def _get_auth_header(self) -> str:
        """Generate Basic Auth header for ETG API"""
        if not self.key_id or not self.key_secret:
            raise ValueError("ETG API credentials not configured")
        
        credentials = f"{self.key_id}:{self.key_secret}"
        encoded = base64.b64encode(credentials.encode()).decode()
        return f"Basic {encoded}"
    
    def _make_request(self, endpoint: str, data: dict) -> dict:
        """Make a POST request to ETG API"""
        url = f"{self.base_url}{endpoint}"
        
        headers = {
            "Authorization": self._get_auth_header(),
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(url, json=data, headers=headers, timeout=30)
            response.raise_for_status()
            return {
                "success": True,
                "data": response.json(),
                "status_code": response.status_code
            }
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Request timeout", "status_code": 408}
        except requests.exceptions.HTTPError as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": e.response.status_code if e.response else 500,
                "response": e.response.json() if e.response else None
            }
        except Exception as e:
            return {"success": False, "error": str(e), "status_code": 500}
    
    # ==========================================
    # 1. STATIC DATA ENDPOINTS
    # ==========================================
    
    def get_hotel_dump(self, language: str = "en", inventory: str = "all") -> dict:
        """
        1.1 Retrieve hotel dump
        Download complete hotel static data for mapping
        Endpoint: /hotel/info/dump/
        """
        data = {
            "inventory": inventory,  # "all", "direct", or "resale"
            "language": language
        }
        return self._make_request("/hotel/info/dump/", data)
    
    def get_hotel_info(self, hotel_id: str, language: str = "en") -> dict:
        """
        1.2 Retrieve hotel content
        Get information for a specific hotel (when not in dump)
        Endpoint: /hotel/info/
        """
        data = {
            "id": hotel_id,
            "language": language
        }
        return self._make_request("/hotel/info/", data)
    
    def get_incremental_dump(self, language: str = "en") -> dict:
        """
        1.3 Retrieve hotel incremental dump
        Get daily updates to hotel static data
        Endpoint: /hotel/info/incremental_dump/
        """
        data = {
            "language": language
        }
        return self._make_request("/hotel/info/incremental_dump/", data)
    
    # ==========================================
    # 2. SEARCH ENDPOINTS
    # ==========================================
    
    def search_by_region(
        self,
        region_id: int,
        checkin: str,
        checkout: str,
        guests: List[Dict],
        currency: str = "INR",
        residency: str = "in",
        language: str = "en"
    ) -> dict:
        """
        2.1 Search by Region
        Search hotels by region ID
        Endpoint: /search/serp/region/
        
        Args:
            region_id: ETG region ID
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            guests: List of guest configurations per room
                    e.g., [{"adults": 2, "children": []}]
            currency: Currency code (default: INR)
            residency: Guest residency country code (default: in)
        """
        data = {
            "checkin": checkin,
            "checkout": checkout,
            "residency": residency,
            "language": language,
            "guests": guests,
            "region_id": region_id,
            "currency": currency
        }
        return self._make_request("/search/serp/region/", data)
    
    def search_by_geo(
        self,
        latitude: float,
        longitude: float,
        radius: int,
        checkin: str,
        checkout: str,
        guests: List[Dict],
        currency: str = "INR",
        residency: str = "in",
        language: str = "en"
    ) -> dict:
        """
        2.1 Search by Geo coordinates
        Search hotels by latitude/longitude
        Endpoint: /search/serp/geo/
        
        Args:
            latitude: Latitude coordinate
            longitude: Longitude coordinate
            radius: Search radius in meters (max 30000)
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            guests: List of guest configurations
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
            "currency": currency
        }
        return self._make_request("/search/serp/geo/", data)
    
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
        2.1 Search by Hotel IDs
        Search specific hotels (max 300 per request)
        Endpoint: /search/serp/hotels/
        
        Args:
            hotel_ids: List of hotel IDs (max 300)
            checkin: Check-in date (YYYY-MM-DD)
            checkout: Check-out date (YYYY-MM-DD)
            guests: List of guest configurations
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
        2.2 Retrieve Hotel Page
        Get detailed hotel information with all room rates
        Endpoint: /search/hp/
        
        Use this when user selects a specific hotel from search results
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
    
    def prebook_rate(
        self,
        book_hash: str,
        price_increase_percent: int = 5
    ) -> dict:
        """
        2.3 Prebook Rate
        Check rate availability and get final price before booking
        Endpoint: /hotel/prebook
        
        Args:
            book_hash: The book_hash from hotel page rate
            price_increase_percent: Acceptable price increase (0-100)
        
        Returns price changes if any, must notify user of changes
        """
        data = {
            "hash": book_hash,
            "price_increase_percent": price_increase_percent
        }
        return self._make_request("/hotel/prebook", data)
    
    # ==========================================
    # 4. BOOKING ENDPOINTS
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
        4.1 Create Booking
        Create a booking on ETG system
        Endpoint: /hotel/order/booking/form/
        
        Args:
            book_hash: The book_hash from prebook step
            partner_order_id: Your unique order ID
            guests: Guest details [{"first_name": "John", "last_name": "Doe"}...]
            user_ip: End user's IP address
            payment_type: "now" or "hotel" (pay at hotel)
        """
        data = {
            "hash": book_hash,
            "partner_order_id": partner_order_id,
            "payment_type": {"type": payment_type},
            "user_ip": user_ip,
            "rooms": [{"guests": guests}]
        }
        return self._make_request("/hotel/order/booking/form/", data)
    
    def finish_booking(self, partner_order_id: str) -> dict:
        """
        4.2 Start/Finish Booking Process
        Complete the booking process
        Endpoint: /hotel/order/booking/finish/
        
        After calling this, booking status will be "in progress"
        Must poll finish_status until final status is received
        """
        data = {
            "partner_order_id": partner_order_id
        }
        return self._make_request("/hotel/order/booking/finish/", data)
    
    def check_booking_status(self, partner_order_id: str) -> dict:
        """
        4.3 Check Booking Status
        Poll this endpoint until status changes from "processing"
        Endpoint: /hotel/order/booking/finish/status/
        
        Poll every 2-3 seconds until status is:
        - "ok": Booking confirmed
        - Any other status: Check error codes for failure reason
        """
        data = {
            "partner_order_id": partner_order_id
        }
        return self._make_request("/hotel/order/booking/finish/status/", data)
    
    # ==========================================
    # 5. POST-BOOKING ENDPOINTS
    # ==========================================
    
    def get_booking_info(self, partner_order_id: str) -> dict:
        """
        5.1 Retrieve Booking Info
        Get details of a completed booking
        Endpoint: /hotel/order/info/
        
        Do NOT use immediately after booking - wait for confirmation first
        """
        data = {
            "partner_order_id": partner_order_id
        }
        return self._make_request("/hotel/order/info/", data)
    
    def cancel_booking(self, partner_order_id: str) -> dict:
        """
        5.2 Cancel Booking
        Cancel an existing booking
        Endpoint: /hotel/order/cancel/
        """
        data = {
            "partner_order_id": partner_order_id
        }
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
        
        Args:
            adults: Number of adults
            children_ages: List of children ages (e.g., [5, 8])
        
        Returns:
            List in format required by ETG API
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
        
        Args:
            guest_list: List of {"first_name": "...", "last_name": "..."}
        
        Returns:
            Formatted guest list
        """
        return guest_list


# Singleton instance
etg_service = ETGApiService()
