"""
C2C Journeys - Data Refresh Service
Handles scheduled refresh of hotel static data from ETG/RateHawk dumps.

Schedule:
  - WEEKLY: Full dump via /hotel/dump/ — complete refresh of all hotel data
  - DAILY:  Incremental dump via /hotel/dump/incremental/ — captures daily changes

This avoids hammering /hotel/info/ for every search and protects RPM limits.
If a daily incremental dump is missed, the weekly full dump acts as a safety net.
"""
import json
import time
import requests
from datetime import datetime, timedelta
from typing import Optional


class DataRefreshService:
    """Service for periodically refreshing hotel cache from ETG dump files."""

    def __init__(self):
        self._last_full_dump = None
        self._last_incremental_dump = None
    
    def run_full_dump(self, max_hotels: int = 5000) -> dict:
        """
        Weekly full dump: /hotel/dump/
        Downloads the complete hotel inventory and updates the cache.
        This is the safety net — even if incremental dumps are missed,
        this brings the cache fully up to date.
        
        Args:
            max_hotels: Maximum number of hotels to process per run
        
        Returns:
            dict with success status, counts, and timing
        """
        from services.etg_service import etg_service
        from services.supabase_service import supabase_service
        
        start_time = time.time()
        stats = {
            'type': 'full_dump',
            'started_at': datetime.utcnow().isoformat(),
            'hotels_processed': 0,
            'hotels_cached': 0,
            'errors': 0,
            'skipped': 0
        }
        
        print(f"🔄 Starting WEEKLY full hotel dump refresh...")
        
        try:
            # Call ETG /hotel/dump/ endpoint
            result = etg_service.get_hotel_dump(language="en", inventory="all")
            
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error from /hotel/dump/')
                print(f"❌ Full dump failed: {error_msg}")
                stats['error'] = error_msg
                return {'success': False, 'error': error_msg, 'stats': stats}
            
            dump_data = result.get('data', {})
            inner_data = dump_data.get('data', dump_data)
            
            # The dump response typically contains a download URL or direct data
            # Handle both cases
            hotels = self._extract_hotels_from_dump(inner_data)
            
            if not hotels:
                print("⚠️ No hotels found in dump response")
                stats['error'] = 'No hotels in dump response'
                return {'success': False, 'error': 'No hotels in dump', 'stats': stats}
            
            total_hotels = len(hotels)
            process_count = min(total_hotels, max_hotels)
            print(f"📦 Full dump contains {total_hotels} hotels, processing {process_count}")
            
            # Process hotels in batches
            batch_size = 50
            for i in range(0, process_count, batch_size):
                batch = hotels[i:i + batch_size]
                
                for hotel_data in batch:
                    stats['hotels_processed'] += 1
                    hotel_id = hotel_data.get('id') or hotel_data.get('hotel_id')
                    
                    if not hotel_id:
                        stats['skipped'] += 1
                        continue
                    
                    try:
                        # Extract and normalize images
                        images = self._extract_images(hotel_data)
                        hotel_data['images'] = images
                        hotel_data['id'] = hotel_id
                        
                        # Upsert to cache
                        supabase_service.cache_hotel(str(hotel_id), hotel_data)
                        stats['hotels_cached'] += 1
                        
                    except Exception as e:
                        stats['errors'] += 1
                        if stats['errors'] <= 5:  # Only log first 5 errors
                            print(f"⚠️ Failed to cache hotel {hotel_id}: {e}")
                
                # Progress log every 500 hotels
                if (i + batch_size) % 500 == 0:
                    print(f"  📊 Progress: {min(i + batch_size, process_count)}/{process_count} hotels processed")
            
            elapsed = round(time.time() - start_time, 2)
            stats['elapsed_seconds'] = elapsed
            stats['completed_at'] = datetime.utcnow().isoformat()
            
            self._last_full_dump = datetime.utcnow()
            
            print(f"✅ Full dump complete: {stats['hotels_cached']} cached, "
                  f"{stats['errors']} errors, {stats['skipped']} skipped in {elapsed}s")
            
            return {'success': True, 'stats': stats}
            
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            stats['elapsed_seconds'] = elapsed
            stats['error'] = str(e)
            print(f"❌ Full dump failed with exception: {e}")
            return {'success': False, 'error': str(e), 'stats': stats}
    
    def run_incremental_dump(self) -> dict:
        """
        Daily incremental dump: /hotel/dump/incremental/
        Downloads only hotels that changed since the last dump.
        Much faster and lighter than a full dump.
        
        Returns:
            dict with success status, counts, and timing
        """
        from services.etg_service import etg_service
        from services.supabase_service import supabase_service
        
        start_time = time.time()
        stats = {
            'type': 'incremental_dump',
            'started_at': datetime.utcnow().isoformat(),
            'hotels_processed': 0,
            'hotels_cached': 0,
            'hotels_deleted': 0,
            'errors': 0
        }
        
        print(f"🔄 Starting DAILY incremental hotel dump refresh...")
        
        try:
            result = etg_service.get_hotel_incremental_dump(language="en")
            
            if not result.get('success'):
                error_msg = result.get('error', 'Unknown error from /hotel/dump/incremental/')
                print(f"❌ Incremental dump failed: {error_msg}")
                stats['error'] = error_msg
                return {'success': False, 'error': error_msg, 'stats': stats}
            
            dump_data = result.get('data', {})
            inner_data = dump_data.get('data', dump_data)
            
            # Incremental dump typically has 'updated' and 'deleted' lists
            updated_hotels = self._extract_hotels_from_dump(inner_data, key='updated')
            deleted_hotel_ids = inner_data.get('deleted', [])
            
            # If no 'updated' key, try treating all data as updates
            if not updated_hotels:
                updated_hotels = self._extract_hotels_from_dump(inner_data)
            
            print(f"📦 Incremental dump: {len(updated_hotels)} updated, {len(deleted_hotel_ids)} deleted")
            
            # Process updated hotels
            for hotel_data in updated_hotels:
                stats['hotels_processed'] += 1
                hotel_id = hotel_data.get('id') or hotel_data.get('hotel_id')
                
                if not hotel_id:
                    continue
                
                try:
                    images = self._extract_images(hotel_data)
                    hotel_data['images'] = images
                    hotel_data['id'] = hotel_id
                    
                    supabase_service.cache_hotel(str(hotel_id), hotel_data)
                    stats['hotels_cached'] += 1
                    
                except Exception as e:
                    stats['errors'] += 1
                    if stats['errors'] <= 5:
                        print(f"⚠️ Failed to cache hotel {hotel_id}: {e}")
            
            # Process deleted hotels (remove from cache)
            for hotel_id in deleted_hotel_ids:
                try:
                    # Delete from cache
                    if supabase_service.client:
                        supabase_service.client.table('hotel_cache').delete().eq('hotel_id', str(hotel_id)).execute()
                        stats['hotels_deleted'] += 1
                except Exception as e:
                    stats['errors'] += 1
            
            elapsed = round(time.time() - start_time, 2)
            stats['elapsed_seconds'] = elapsed
            stats['completed_at'] = datetime.utcnow().isoformat()
            
            self._last_incremental_dump = datetime.utcnow()
            
            print(f"✅ Incremental dump complete: {stats['hotels_cached']} cached, "
                  f"{stats['hotels_deleted']} deleted, {stats['errors']} errors in {elapsed}s")
            
            return {'success': True, 'stats': stats}
            
        except Exception as e:
            elapsed = round(time.time() - start_time, 2)
            stats['elapsed_seconds'] = elapsed
            stats['error'] = str(e)
            print(f"❌ Incremental dump failed with exception: {e}")
            return {'success': False, 'error': str(e), 'stats': stats}
    
    def get_refresh_status(self) -> dict:
        """Get the current status of the data refresh schedule."""
        from services.supabase_service import supabase_service
        
        # Check how many hotels are cached
        cached_count = 0
        try:
            if supabase_service.client:
                result = supabase_service.client.table('hotel_cache').select('hotel_id', count='exact').execute()
                cached_count = result.count if hasattr(result, 'count') else len(result.data or [])
        except Exception:
            pass
        
        return {
            'cached_hotels': cached_count,
            'last_full_dump': self._last_full_dump.isoformat() if self._last_full_dump else None,
            'last_incremental_dump': self._last_incremental_dump.isoformat() if self._last_incremental_dump else None,
            'schedule': {
                'full_dump': 'Weekly (every 7 days) — /hotel/dump/',
                'incremental_dump': 'Daily — /hotel/dump/incremental/',
                'note': 'Weekly full dump acts as safety net if daily incremental is missed'
            }
        }
    
    def _extract_hotels_from_dump(self, data: dict, key: str = None) -> list:
        """
        Extract hotel list from dump response.
        RateHawk dump responses can vary in format:
        - Direct list of hotels
        - Dict with 'hotels' key
        - Dict with 'updated'/'deleted' keys (incremental)
        - Download URL pointing to a file
        """
        if not data:
            return []
        
        # If a specific key is requested
        if key and isinstance(data, dict):
            hotels = data.get(key, [])
            if isinstance(hotels, list):
                return hotels
        
        # Try common keys
        if isinstance(data, list):
            return data
        
        if isinstance(data, dict):
            # Try 'hotels' key first
            hotels = data.get('hotels', [])
            if isinstance(hotels, list) and hotels:
                return hotels
            
            # Try 'items' key
            items = data.get('items', [])
            if isinstance(items, list) and items:
                return items
            
            # Check if the response contains a download URL
            url = data.get('url') or data.get('download_url')
            if url:
                return self._download_and_parse_dump(url)
            
            # If the dict itself looks like hotel data keyed by ID
            # (e.g. {"hotel_123": {...}, "hotel_456": {...}})
            if all(isinstance(v, dict) for v in data.values()):
                hotels = []
                for hid, hdata in data.items():
                    if isinstance(hdata, dict):
                        hdata['id'] = hid
                        hotels.append(hdata)
                return hotels
        
        return []
    
    def _download_and_parse_dump(self, url: str) -> list:
        """Download dump file from URL and parse hotel data."""
        try:
            print(f"📥 Downloading dump from: {url[:80]}...")
            response = requests.get(url, timeout=300, stream=True)
            response.raise_for_status()
            
            # Parse based on content type
            content_type = response.headers.get('Content-Type', '')
            
            if 'json' in content_type or url.endswith('.json'):
                data = response.json()
                return self._extract_hotels_from_dump(data)
            
            # Try to parse as JSONL (one JSON per line)
            hotels = []
            for line in response.iter_lines():
                if line:
                    try:
                        hotel = json.loads(line)
                        if isinstance(hotel, dict):
                            hotels.append(hotel)
                    except json.JSONDecodeError:
                        continue
            
            return hotels
            
        except Exception as e:
            print(f"❌ Failed to download dump: {e}")
            return []
    
    def _extract_images(self, hotel_data: dict) -> list:
        """Extract images from hotel data, handling both modern and legacy formats."""
        images = []
        
        # Modern: images_ext (categorized)
        images_ext = hotel_data.get('images_ext', {})
        if images_ext and isinstance(images_ext, dict):
            for category, img_list in images_ext.items():
                if isinstance(img_list, list):
                    for img in img_list:
                        if isinstance(img, str) and img:
                            images.append(img)
                        elif isinstance(img, dict) and img.get('url'):
                            images.append(img['url'])
        
        # Fallback: images (deprecated)
        if not images:
            raw_images = hotel_data.get('images', [])
            if isinstance(raw_images, list):
                for img in raw_images:
                    if isinstance(img, str) and img:
                        images.append(img)
                    elif isinstance(img, dict) and img.get('url'):
                        images.append(img['url'])
        
        return images


# Singleton instance
data_refresh_service = DataRefreshService()
