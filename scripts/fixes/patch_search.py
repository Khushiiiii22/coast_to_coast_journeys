import sys

file_path = "backend/routes/hotel_routes.py"
with open(file_path, "r") as f:
    content = f.read()

start_marker = "        # Step 1: Check if destination matches a known location"
end_marker = "        # Step 5: Final fallback - NO hotels found"
end_marker_full = "            'source': 'none'\n        })\n"

start_idx = content.find(start_marker)
end_idx = content.find(end_marker_full, start_idx) + len(end_marker_full)

if start_idx == -1 or end_idx == -1:
    print("Markers not found!")
    sys.exit(1)

replacement = """        # ──────────────────────────────────────────────────────────
        # STEP 1: Resolve destination → region_id
        # Strategy: Try hardcoded fast-path first, then ALWAYS
        # fall back to RateHawk multicomplete API for ANY destination.
        # ──────────────────────────────────────────────────────────
        hotel_ids_to_search = None
        
        # 1a. Quick match from popular destinations (speed optimization only)
        for key, loc_data in POPULAR_DESTINATIONS.items():
            if key in destination or destination in key:
                region_id = loc_data.get('region_id')
                location_name = loc_data.get('name', data['destination'])
                print(f"📍 Fast-path match: {location_name}, Region ID: {region_id}")
                break
        
        # 1b. PRIMARY: Resolve ANY destination via RateHawk multicomplete API
        #     This handles ALL destinations worldwide — not just the hardcoded list.
        if not region_id:
            print(f"🌍 Resolving '{data['destination']}' via RateHawk multicomplete API...")
            try:
                suggest_result = etg_service.suggest(data['destination'], 'en')
                if suggest_result.get('success') and suggest_result.get('data'):
                    suggest_data = suggest_result['data'].get('data', suggest_result['data'])
                    regions = suggest_data.get('regions', [])
                    hotels = suggest_data.get('hotels', [])
                    
                    if regions:
                        best_region = regions[0]
                        region_id = best_region.get('id')
                        location_name = best_region.get('name', data['destination'])
                        print(f"✅ Resolved via multicomplete: {location_name}, Region ID: {region_id}")
                    elif hotels:
                        # User typed a hotel name directly
                        hotel_ids_to_search = [h.get('id') for h in hotels[:10] if h.get('id')]
                        location_name = hotels[0].get('name', data['destination'])
                        print(f"✅ Resolved as hotel name: {location_name}, Hotel IDs: {hotel_ids_to_search[:3]}...")
            except Exception as e:
                print(f"⚠️ Multicomplete resolution failed: {e}")
        
        # ──────────────────────────────────────────────────────────
        # STEP 2: Search for hotels using resolved region_id or hotel_ids
        # ──────────────────────────────────────────────────────────
        if not region_id and not hotel_ids_to_search:
            print(f"🛑 Could not resolve destination: '{data['destination']}'")
            return jsonify({
                'success': False,
                'error': f"Could not find destination '{data['destination']}'. Please check the spelling or try a different search term.",
                'hotels': [],
                'source': 'none'
            })
        
        # Prepare search parameters
        user_currency = data.get('currency', 'USD')
        api_currency = 'USD' if user_currency == 'INR' else user_currency
        
        guests = etg_service.format_guests_for_search(
            adults=data['adults'],
            children_ages=data.get('children_ages', []),
            rooms=rooms_data
        )
        
        print(f"🏨 Searching RateHawk for: {location_name}")
        
        if hotel_ids_to_search:
            result = etg_service.search_by_hotels(
                hotel_ids=hotel_ids_to_search,
                checkin=data['checkin'],
                checkout=data['checkout'],
                rooms=guests,
                currency=api_currency,
                residency=data.get('residency', 'gb')
            )
        else:
            result = etg_service.search_by_region(
                region_id=region_id,
                checkin=data['checkin'],
                checkout=data['checkout'],
                rooms=guests,
                currency=api_currency,
                residency=data.get('residency', 'gb')
            )
        
        # ──────────────────────────────────────────────────────────
        # STEP 3: Handle errors with smart retry
        # ──────────────────────────────────────────────────────────
        if result.get('status') == 'error' or not result.get('success', True):
            error_msg = result.get('error', 'Unknown API error')
            if 'data' in result and isinstance(result['data'], dict):
                debug = result['data'].get('debug', {})
                if debug.get('validation_error'):
                    error_msg = debug['validation_error']
            
            print(f"❌ RateHawk search error: {error_msg}")
            
            # If region_id was invalid, try re-resolving via multicomplete
            if 'region' in str(error_msg).lower() or 'invalid' in str(error_msg).lower():
                print(f"🔄 Retrying with dynamic region_id from multicomplete API...")
                try:
                    suggest_result = etg_service.suggest(data['destination'], 'en')
                    if suggest_result.get('success') and suggest_result.get('data'):
                        suggest_data = suggest_result['data'].get('data', suggest_result['data'])
                        regions = suggest_data.get('regions', [])
                        if regions:
                            new_region_id = regions[0].get('id')
                            if new_region_id and new_region_id != region_id:
                                print(f"✅ Got new region_id {new_region_id} (old was {region_id}), retrying search...")
                                region_id = new_region_id
                                result = etg_service.search_by_region(
                                    region_id=region_id,
                                    checkin=data['checkin'],
                                    checkout=data['checkout'],
                                    rooms=guests,
                                    currency=api_currency,
                                    residency=data.get('residency', 'gb')
                                )
                                if result.get('status') == 'error' or not result.get('success', True):
                                    print(f"❌ Retry also failed: {result.get('error', 'Unknown')}")
                                else:
                                    print(f"✅ Retry succeeded with new region_id {new_region_id}")
                except Exception as e:
                    print(f"⚠️ Dynamic region resolution failed: {e}")
            
            # If it's a date validation error, return early with helpful message
            if any(kw in str(error_msg).lower() for kw in ['checkin', 'checkout', 'date']):
                return jsonify({
                    'success': False, 
                    'error': f"Search failed: {error_msg}. Please check your dates and try again."
                }), 400

        # ──────────────────────────────────────────────────────────
        # STEP 4: Process and return results
        # ──────────────────────────────────────────────────────────
        if result.get('success') and result.get('data'):
            inner_data = result['data'].get('data', result['data'])
            etg_hotels = inner_data.get('hotels', [])
            
            if etg_hotels and len(etg_hotels) > 0:
                print(f"✅ Found {len(etg_hotels)} hotels via RateHawk for {location_name}")

                # Bulk static data enrichment (parallel fetch)
                hotel_ids = [h.get('hotel_id') or h.get('id') for h in etg_hotels if h.get('hotel_id') or h.get('id')]
                static_hotel_map = {}
                
                if hotel_ids:
                    print(f"📦 Fetching static info for {len(hotel_ids)} hotels in parallel...")
                    static_res = etg_service.get_hotels_static(hotel_ids, language='en')
                    if static_res.get('success'):
                        static_hotel_map = static_res['data'].get('data', {})
                        print(f"✅ Successfully enriched {len(static_hotel_map)} hotels with static data")

                # Calculate nights
                from datetime import datetime
                try:
                    d1 = datetime.strptime(data['checkin'], '%Y-%m-%d')
                    d2 = datetime.strptime(data['checkout'], '%Y-%m-%d')
                    nights = (d2 - d1).days
                except:
                    nights = 1

                # Enrich hotels with static data
                for h in etg_hotels:
                    hid = h.get('hotel_id') or h.get('id')
                    if hid and hid in static_hotel_map:
                        h['static_data'] = static_hotel_map[hid]

                transformed_hotels = transform_etg_hotels(
                    hotels_data=etg_hotels, 
                    target_currency=user_currency,
                    conversion_rates=CONVERSION_RATES,
                    nights=nights,
                    use_block_markup=str(data.get('is_block_booking', '')).lower() == 'true'
                )
                
                return jsonify({
                    'success': True,
                    'data': {'hotels': transformed_hotels},
                    'location': {'name': location_name, 'region_id': region_id},
                    'hotels_count': len(transformed_hotels),
                    'real_data': True,
                    'source': 'ratehawk'
                })
            else:
                print(f"⚠️ RateHawk returned 0 hotels for {location_name}")
        
        # No hotels found after all attempts
        print(f"🛑 No hotels found for {location_name} after all attempts")
        
        return jsonify({
            'success': False,
            'error': f"No availability found for '{location_name}' on these dates. Please try different dates or a different destination.",
            'hotels': [],
            'source': 'none'
        })
"""

new_content = content[:start_idx] + replacement + content[end_idx:]

with open(file_path, "w") as f:
    f.write(new_content)

print("Patch applied successfully.")
