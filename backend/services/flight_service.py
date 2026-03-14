"""
Flight Service with Duffel Integration
Provides live flight data via Duffel API with a mock fallback.
"""
import random
from datetime import datetime, timedelta
import hashlib
from duffel_api import Duffel
from config import Config

class FlightService:
    def __init__(self):
        self.client = None
        if Config.DUFFEL_ACCESS_TOKEN:
            self.access_token = Config.DUFFEL_ACCESS_TOKEN
            try:
                # Duffel API SDK defaults to an old API version.
                # Must specify 'v2' (v1 and beta are deprecated).
                self.client = Duffel(access_token=self.access_token, api_version="v2")
                print("✅ Duffel API client initialized")
            except Exception as e:
                print(f"⚠️ Error initializing Duffel client: {e}")

        self.airlines = [
            {'code': 'AI', 'name': 'Air India', 'logo': 'https://logos-world.net/wp-content/uploads/2023/01/Air-India-Logo.png'},
            {'code': '6E', 'name': 'IndiGo', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/9/93/IndiGo_Logo_2.svg/1200px-IndiGo_Logo_2.svg.png'},
            {'code': 'UK', 'name': 'Vistara', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/22/Vistara.png/800px-Vistara.png'},
            {'code': 'SG', 'name': 'SpiceJet', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/d/d8/SpiceJet_logo.svg/1200px-SpiceJet_logo.svg.png'},
            {'code': 'QP', 'name': 'Akasa Air', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/2/29/Akasa_Air_Logo.svg/1200px-Akasa_Air_Logo.svg.png'},
            {'code': 'EK', 'name': 'Emirates', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/d/d0/Emirates_logo.svg/1024px-Emirates_logo.svg.png'},
            {'code': 'BA', 'name': 'British Airways', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/b/b3/British_Airways_2019.svg/1200px-British_Airways_2019.svg.png'},
            {'code': 'LH', 'name': 'Lufthansa', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/b/b8/Lufthansa_Logo_2018.svg/1200px-Lufthansa_Logo_2018.svg.png'},
            {'code': 'AF', 'name': 'Air France', 'logo': 'https://upload.wikimedia.org/wikipedia/commons/thumb/4/44/Air_France_Logo.svg/1200px-Air_France_Logo.svg.png'},
            {'code': 'SQ', 'name': 'Singapore Airlines', 'logo': 'https://upload.wikimedia.org/wikipedia/en/thumb/6/6b/Singapore_Airlines_Logo_2.svg/1200px-Singapore_Airlines_Logo_2.svg.png'}
        ]
        
        self.airports = {
            'DEL': {'name': 'Indira Gandhi International Airport', 'city': 'New Delhi', 'country': 'India'},
            'BOM': {'name': 'Chhatrapati Shivaji Maharaj International Airport', 'city': 'Mumbai', 'country': 'India'},
            'BLR': {'name': 'Kempegowda International Airport', 'city': 'Bangalore', 'country': 'India'},
            'MAA': {'name': 'Chennai International Airport', 'city': 'Chennai', 'country': 'India'},
            'CCU': {'name': 'Netaji Subhash Chandra Bose International Airport', 'city': 'Kolkata', 'country': 'India'},
            'HYD': {'name': 'Rajiv Gandhi International Airport', 'city': 'Hyderabad', 'country': 'India'},
            'GOI': {'name': 'Goa International Airport', 'city': 'Goa', 'country': 'India'},
            'JAI': {'name': 'Jaipur International Airport', 'city': 'Jaipur', 'country': 'India'},
            'DXB': {'name': 'Dubai International Airport', 'city': 'Dubai', 'country': 'UAE'},
            'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK'},
            'JFK': {'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA'},
            'SIN': {'name': 'Changi Airport', 'city': 'Singapore', 'country': 'Singapore'},
            'CDG': {'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'France'},
            'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany'},
            'BKK': {'name': 'Suvarnabhumi Airport', 'city': 'Bangkok', 'country': 'Thailand'},
            'MLE': {'name': 'Velana International Airport', 'city': 'Male', 'country': 'Maldives'}
        }
        
        self.city_to_code = {}
        for code, details in self.airports.items():
            city_lower = details['city'].lower()
            self.city_to_code[city_lower] = code
            if 'new delhi' in city_lower:
                self.city_to_code['delhi'] = code
            if 'bangalore' in city_lower:
                self.city_to_code['bengaluru'] = code

    def _resolve_airport_code(self, location):
        """Resolve city name or airport code to airport code"""
        if not location:
            return location
        
        location_upper = location.upper().strip()
        location_lower = location.lower().strip()
        
        if location_upper in self.airports:
            return location_upper
        
        if location_lower in self.city_to_code:
            return self.city_to_code[location_lower]
        
        for city, code in self.city_to_code.items():
            if location_lower in city or city in location_lower:
                return code
        
        return location_upper if len(location_upper) <= 4 else location_upper[:3]

    def search_flights(self, origin, destination, depart_date, return_date=None, adults=1, flight_class='economy'):
        """Search flights with Duffel or fallback to mock data"""
        origin_code = self._resolve_airport_code(origin)
        dest_code = self._resolve_airport_code(destination)

        # If Duffel is configured, try real search
        if self.client:
            try:
                return self._duffel_search(origin_code, dest_code, depart_date, return_date, adults, flight_class)
            except Exception as e:
                print(f"⚠️ Duffel search failed, falling back to mock: {e}")

        # Fallback to mock data
        results = {
            'outbound': self._generate_flights(origin_code, dest_code, depart_date, adults, flight_class),
            'inbound': [],
            'meta': {'provider': 'mock'}
        }
        
        if return_date:
            results['inbound'] = self._generate_flights(dest_code, origin_code, return_date, adults, flight_class)
            
        return {
            'success': True,
            'data': results
        }

    def _duffel_search(self, origin, destination, depart_date, return_date, adults, flight_class):
        """Perform real search using Duffel API directly via requests"""
        import requests

        headers = {
            "Duffel-Version": "v2",
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json",
            "User-Agent": "C2C-Journeys/1.0"
        }

        slices = [
            {
                "origin": origin,
                "destination": destination,
                "departure_date": depart_date,
            }
        ]
        
        if return_date:
            slices.append({
                "origin": destination,
                "destination": origin,
                "departure_date": return_date,
            })

        passengers = [{"type": "adult"} for _ in range(adults)]
        
        cabin_class_map = {
            'economy': 'economy',
            'business': 'business',
            'first': 'first',
            'premium_economy': 'premium_economy'
        }
        
        payload = {
            "data": {
                "slices": slices,
                "passengers": passengers,
                "cabin_class": cabin_class_map.get(flight_class, 'economy')
            }
        }

        # 1. Create Offer Request
        response = requests.post("https://api.duffel.com/air/offer_requests", json=payload, headers=headers)
        if not response.ok:
            raise Exception(f"Duffel offer_request failed: {response.text}")
        
        offer_request_data = response.json().get('data', {})
        offers = offer_request_data.get('offers', [])
        offer_request_id = offer_request_data.get('id')
        
        formatted_outbound = []
        formatted_inbound = []

        for offer in offers:
            try:
                outbound_slice = offer['slices'][0]
                inbound_slice = offer['slices'][1] if len(offer['slices']) > 1 else None

                price_data = offer['total_amount']
                currency = offer['total_currency']

                outbound_flight = self._format_duffel_slice(offer['id'], outbound_slice, price_data, currency)
                formatted_outbound.append(outbound_flight)

                if inbound_slice:
                    inbound_flight = self._format_duffel_slice(offer['id'], inbound_slice, price_data, currency, is_inbound=True)
                    formatted_inbound.append(inbound_flight)
            except Exception as loop_e:
                print(f"Skipping an offer due to parsing error: {loop_e}")

        return {
            'success': True,
            'data': {
                'outbound': formatted_outbound,
                'inbound': formatted_inbound,
                'meta': {
                    'provider': 'duffel',
                    'offer_request_id': offer_request_id
                }
            }
        }

    def _format_duffel_slice(self, offer_id, fslice, price, currency, is_inbound=False):
        """Format Duffel slice data to match frontend expectations using raw JSON dicts"""
        # For simplicity, we take the first segment's details
        segments_data = fslice.get('segments', [])
        if not segments_data:
            raise KeyError("No segments found in Duffel slice")

        first_segment = segments_data[0]
        airline = first_segment.get('marketing_carrier', {})

        segments = []
        for idx, seg in enumerate(segments_data):
            dep_dt = datetime.fromisoformat(seg.get('departing_at', '').replace('Z', '+00:00'))
            arr_dt = datetime.fromisoformat(seg.get('arriving_at', '').replace('Z', '+00:00'))
            dur_mins = max(0, int((arr_dt - dep_dt).total_seconds() // 60))
            dur_str = f"{dur_mins // 60}h {dur_mins % 60}m"

            layover_mins = None
            if idx < len(segments_data) - 1:
                next_dep = datetime.fromisoformat(segments_data[idx + 1].get('departing_at', '').replace('Z', '+00:00'))
                layover_mins = max(0, int((next_dep - arr_dt).total_seconds() // 60))

            carrier = seg.get('marketing_carrier', {})
            origin_info = seg.get('origin', {})
            dest_info = seg.get('destination', {})

            segments.append({
                'origin': origin_info.get('iata_code', origin_info.get('id', '')),
                'destination': dest_info.get('iata_code', dest_info.get('id', '')),
                'depart_time': dep_dt.strftime('%H:%M'),
                'arrival_time': arr_dt.strftime('%H:%M'),
                'duration': dur_str,
                'flight_number': f"{carrier.get('iata_code', '')}{seg.get('marketing_carrier_flight_number', '')}",
                'airline_name': carrier.get('name', carrier.get('iata_code', '')),
                'airline_code': carrier.get('iata_code', ''),
                'cabin_class': seg.get('cabin_class', 'economy'),
                'layover_minutes': layover_mins
            })
        
        # Duration format for whole slice (e.g. PT10H20M -> 10h 20m)
        slice_duration_str = fslice.get('duration', '')
        formatted_duration = slice_duration_str[2:].lower().replace('h', 'h ') if slice_duration_str.startswith('PT') else slice_duration_str
        
        origin_airport = first_segment.get('origin', {})
        dest_airport = segments_data[-1].get('destination', {})

        return {
            'id': f"{offer_id}_{'in' if is_inbound else 'out'}",
            'airline': {
                'code': airline.get('iata_code', ''),
                'name': airline.get('name', ''),
                'logo': f"https://res.cloudinary.com/duffel/image/upload/v1582230000/intermediary/carrier-logos/{airline.get('iata_code', '')}.png"
            },
            'flight_number': f"{airline.get('iata_code', '')}{first_segment.get('marketing_carrier_flight_number', '')}",
            'origin': origin_airport.get('iata_code', ''),
            'destination': dest_airport.get('iata_code', ''),
            'depart_time': datetime.fromisoformat(first_segment.get('departing_at', '').replace('Z', '+00:00')).strftime('%H:%M'),
            'arrival_time': datetime.fromisoformat(segments_data[-1].get('arriving_at', '').replace('Z', '+00:00')).strftime('%H:%M'),
            'duration': formatted_duration,
            'next_day': False, 
            'stops': len(segments_data) - 1,
            'price': float(price),
            'currency': currency,
            'class': first_segment.get('cabin_class', 'economy'),
            'segments': segments
        }

    def suggest(self, query):
        """Autocomplete for airports - stays mock for now to avoid heavy API usage"""
        query = query.upper()
        suggestions = []

        country_codes = {
            'India': 'IN', 'UAE': 'AE', 'UK': 'GB', 'USA': 'US', 'Singapore': 'SG',
            'France': 'FR', 'Germany': 'DE', 'Thailand': 'TH', 'Maldives': 'MV'
        }
        
        for code, details in self.airports.items():
            if (query in code or 
                query in details['city'].upper() or 
                query in details['country'].upper()):
                suggestions.append({
                    'code': code,
                    'name': details['name'],
                    'city': details['city'],
                    'country': details['country'],
                    'label': f"{code} - {details['name']}, {details['city']}, {country_codes.get(details['country'], details['country'][:2].upper())}"
                })
        
        if not suggestions and len(query) == 3:
            suggestions.append({
                'code': query,
                'name': f"{query} International Airport",
                'city': query,
                'country': 'Unknown',
                'label': f"{query} - {query} International Airport, {query}, UN"
            })
            
        return {
            'success': True,
            'data': suggestions
        }

    def _generate_flights(self, origin, destination, date_str, adults, flight_class):
        """Generate realistic mock flight options with INR pricing"""
        flights = []
        num_flights = random.randint(6, 14)
        
        # Realistic INR base prices by class
        if flight_class == 'economy':
            base_price = random.randint(3000, 12000)
        elif flight_class == 'premium':
            base_price = random.randint(8000, 20000)
        elif flight_class == 'business':
            base_price = random.randint(18000, 45000)
        else:  # first
            base_price = random.randint(35000, 80000)
        
        # International routes cost more
        domestic_codes = {'DEL', 'BOM', 'BLR', 'MAA', 'CCU', 'HYD', 'GOI', 'JAI'}
        is_international = origin not in domestic_codes or destination not in domestic_codes
        if is_international:
            base_price = int(base_price * random.uniform(2.5, 4.0))
        
        for i in range(num_flights):
            airline = random.choice(self.airlines)
            flight_num = f"{airline['code']}{random.randint(100, 999)}"
            hour = random.randint(5, 23)  # Flights between 5 AM and 11 PM
            minute = random.choice([0, 15, 30, 45])
            depart_time = f"{hour:02d}:{minute:02d}"
            
            # Duration based on domestic vs international
            if is_international:
                duration_mins = random.randint(180, 720)
            else:
                duration_mins = random.randint(90, 300)
            
            duration_hours = duration_mins // 60
            duration_rem_mins = duration_mins % 60
            duration_str = f"{duration_hours}h {duration_rem_mins}m"
            arrival_mins_total = hour * 60 + minute + duration_mins
            arr_hour = (arrival_mins_total // 60) % 24
            arr_min = arrival_mins_total % 60
            arrival_time = f"{arr_hour:02d}:{arr_min:02d}"
            next_day = arrival_mins_total >= 24 * 60
            
            # Non-stop flights more common for short routes
            if duration_mins < 180:
                stops = random.choice([0, 0, 0, 0, 1])
            else:
                stops = random.choice([0, 0, 1, 1, 2])
            
            price = base_price * (1.15 if stops == 0 else 0.85 if stops == 1 else 0.7)
            price += random.randint(-500, 2000)
            price = max(2500, int(round(price / 100) * 100))  # Round to nearest 100
            
            flights.append({
                'id': hashlib.md5(f"{flight_num}{date_str}{i}".encode()).hexdigest(),
                'airline': airline,
                'flight_number': flight_num,
                'origin': origin,
                'destination': destination,
                'depart_time': depart_time,
                'arrival_time': arrival_time,
                'duration': duration_str,
                'next_day': next_day,
                'stops': stops,
                'price': int(price),
                'currency': 'INR',
                'class': flight_class,
                'segments': self._build_mock_segments(origin, destination, date_str, depart_time, duration_mins, stops, airline['code'], flight_class)
            })
        flights.sort(key=lambda x: x['price'])
        return flights

    def _build_mock_segments(self, origin, destination, date_str, depart_time, duration_mins, stops, airline_code, cabin_class):
        """Create realistic segment-level mock details for flight details expansion."""
        legs = max(1, int(stops) + 1)
        hubs = ['DEL', 'BOM', 'BLR', 'DXB', 'SIN', 'HYD', 'MAA']
        transit = [h for h in hubs if h not in {origin, destination}][:max(0, legs - 1)]
        route = [origin] + transit + [destination]

        layover_per_stop = 75
        total_layover = max(0, legs - 1) * layover_per_stop
        flying_mins = max(legs * 45, duration_mins - total_layover)
        base_leg = flying_mins // legs
        rem = flying_mins % legs

        curr = datetime.strptime(f"{date_str} {depart_time}", "%Y-%m-%d %H:%M")
        segments = []

        for i in range(legs):
            leg_mins = base_leg + (1 if i < rem else 0)
            arr = curr + timedelta(minutes=leg_mins)
            layover = layover_per_stop if i < legs - 1 else None

            segments.append({
                'origin': route[i],
                'destination': route[i + 1],
                'depart_time': curr.strftime('%H:%M'),
                'arrival_time': arr.strftime('%H:%M'),
                'duration': f"{leg_mins // 60}h {leg_mins % 60}m",
                'flight_number': f"{airline_code}{random.randint(100, 999)}",
                'airline_name': airline_code,
                'airline_code': airline_code,
                'cabin_class': cabin_class,
                'layover_minutes': layover
            })

            curr = arr + timedelta(minutes=layover_per_stop if layover else 0)

        return segments

flight_service = FlightService()
