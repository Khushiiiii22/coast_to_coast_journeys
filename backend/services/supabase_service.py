"""
C2C Journeys - Supabase Service
Handles all Supabase database operations
"""
import os
import sys

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import Config


class SupabaseService:
    """Service class for Supabase operations"""
    
    _client = None
    
    @property
    def client(self):
        """Lazy initialization of Supabase client"""
        if self._client is None:
            try:
                from supabase import create_client, Client
                self._client = create_client(
                    Config.SUPABASE_URL,
                    Config.SUPABASE_SERVICE_ROLE_KEY
                )
            except Exception as e:
                print(f"⚠️  Warning: Could not initialize Supabase client: {e}")
                self._client = None
        return self._client
    
    def _execute_query(self, operation):
        """Execute a query with error handling"""
        if self.client is None:
            return {'success': False, 'error': 'Supabase client not initialized'}
        try:
            result = operation()
            return {'success': True, 'data': result.data[0] if result.data and len(result.data) == 1 else result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # ==========================================
    # Hotel Bookings
    # ==========================================
    
    def create_booking(self, booking_data: dict) -> dict:
        """Create a new hotel booking record"""
        def op():
            return self.client.table('hotel_bookings').insert(booking_data).execute()
        return self._execute_query(op)
    
    def update_booking(self, booking_id: str, update_data: dict) -> dict:
        """Update an existing booking"""
        def op():
            return self.client.table('hotel_bookings').update(update_data).eq('id', booking_id).execute()
        return self._execute_query(op)
    
    def update_booking_by_partner_order_id(self, partner_order_id: str, update_data: dict) -> dict:
        """Update booking by partner order ID"""
        def op():
            return self.client.table('hotel_bookings').update(update_data).eq('partner_order_id', partner_order_id).execute()
        return self._execute_query(op)
    
    def get_booking(self, booking_id: str) -> dict:
        """Get a booking by ID"""
        def op():
            return self.client.table('hotel_bookings').select('*').eq('id', booking_id).execute()
        return self._execute_query(op)
    
    def get_booking_by_partner_order_id(self, partner_order_id: str) -> dict:
        """Get a booking by partner order ID"""
        def op():
            return self.client.table('hotel_bookings').select('*').eq('partner_order_id', partner_order_id).execute()
        return self._execute_query(op)
    
    def get_user_bookings(self, user_id: str) -> dict:
        """Get all bookings for a user"""
        def op():
            return self.client.table('hotel_bookings').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        result = self._execute_query(op)
        if result.get('success') and result.get('data') is None:
            result['data'] = []
        return result
    
    # ==========================================
    # Hotel Cache (for static data)
    # ==========================================
    
    def cache_hotel(self, hotel_id: str, hotel_data: dict) -> dict:
        """Cache hotel static data"""
        def op():
            return self.client.table('hotel_cache').upsert({
                'hotel_id': hotel_id,
                'hotel_data': hotel_data
            }).execute()
        return self._execute_query(op)
    
    def get_cached_hotel(self, hotel_id: str) -> dict:
        """Get cached hotel data"""
        def op():
            return self.client.table('hotel_cache').select('*').eq('hotel_id', hotel_id).execute()
        return self._execute_query(op)
    
    def get_cached_hotels(self, hotel_ids: list) -> dict:
        """Get multiple cached hotels"""
        def op():
            return self.client.table('hotel_cache').select('*').in_('hotel_id', hotel_ids).execute()
        result = self._execute_query(op)
        if result.get('success') and result.get('data') is None:
            result['data'] = []
        return result
    
    # ==========================================
    # Search History
    # ==========================================
    
    def save_search_history(self, search_data: dict) -> dict:
        """Save search history for analytics"""
        def op():
            return self.client.table('hotel_search_history').insert(search_data).execute()
        return self._execute_query(op)
    
    # ==========================================
    # Regions (for autocomplete)
    # ==========================================
    
    def search_regions(self, query: str, limit: int = 10) -> dict:
        """Search regions by name for autocomplete"""
        def op():
            return self.client.table('regions').select('*').ilike('name', f'%{query}%').limit(limit).execute()
        result = self._execute_query(op)
        if result.get('success') and result.get('data') is None:
            result['data'] = []
        return result
    
    def get_region(self, region_id: int) -> dict:
        """Get region by ID"""
        def op():
            return self.client.table('regions').select('*').eq('id', region_id).execute()
        return self._execute_query(op)


# Singleton instance - lazy initialized
supabase_service = SupabaseService()
