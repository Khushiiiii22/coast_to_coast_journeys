"""
Flight Service with Duffel Integration
Provides live flight data via Duffel API with a mock fallback.
"""
import random
from datetime import datetime, timedelta
import hashlib
import requests
from config import Config

class FlightService:
    def __init__(self):
        self.air_iq_url = Config.AIR_IQ_BASE_URL
        self.air_iq_login_id = Config.AIR_IQ_LOGIN_ID
        self.air_iq_password = Config.AIR_IQ_PASSWORD
        self.air_iq_api_key = Config.AIR_IQ_API_KEY
        self.token = None
        if self.air_iq_api_key:
            self._authenticate()

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

    def _authenticate(self):
        url = f"{self.air_iq_url}/login"
        payload = {"Username": self.air_iq_login_id, "Password": self.air_iq_password}
        headers = {"Content-Type": "application/json", "api-key": self.air_iq_api_key}
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.ok:
                data = res.json()
                self.token = data.get("token")
                print("✅ AIR iQ API client initialized")
            else:
                print(f"⚠️ Error initializing AIR iQ client: {res.text}")
        except Exception as e:
            print(f"⚠️ Error initializing AIR iQ client: {e}")

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

        # If AIR iQ is configured, try real search
        if self.token:
            try:
                res = self._air_iq_search(origin_code, dest_code, depart_date, return_date, adults, flight_class)
                if res and res.get('success'): 
                    return res
                else:
                    print("⚠️ AIR iQ search returned no results, falling back to mock.")
            except Exception as e:
                print(f"⚠️ AIR iQ search failed, falling back to mock: {e}")

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

    def _air_iq_search(self, origin, destination, depart_date, return_date, adults, flight_class):
        """Perform real search using AIR iQ API"""
        # AIR iQ date format is YYYY/MM/DD
        # Input date comes typically as YYYY-MM-DD
        formatted_date = depart_date.replace('-', '/')
        
        headers = {
            "Authorization": self.token,
            "Content-Type": "application/json",
            "api-key": self.air_iq_api_key
        }

        payload = {
            "origin": origin,
            "destination": destination,
            "departure_date": formatted_date,
            "adult": adults,
            "child": 0,
            "infant": 0
        }
        
        # Flight classes might need mapping, default to Economy mostly.
        # AIR iQ doesn't strictly have this in the basic payload uncovered so leaving it default.

        response = requests.post(f"{self.air_iq_url}/search", json=payload, headers=headers, timeout=30)
        if not response.ok:
            raise Exception(f"AIR iQ search failed: {response.text}")
        
        resp_json = response.json()
        if resp_json.get('status') != 'success' or not resp_json.get('data'):
            return {'success': False}
            
        flights_data = resp_json.get('data', [])
        
        formatted_outbound = []
        
        for flight in flights_data:
            try:
                outbound_flight = self._format_air_iq_flight(flight)
                formatted_outbound.append(outbound_flight)
            except Exception as loop_e:
                print(f"Skipping a flight due to parsing error: {loop_e}")

        # Currently mock inbound due to missing AIR iQ dual slice format details
        formatted_inbound = []
        if return_date:
             formatted_inbound = self._generate_flights(destination, origin, return_date, adults, flight_class)

        return {
            'success': True,
            'data': {
                'outbound': formatted_outbound,
                'inbound': formatted_inbound,
                'meta': {
                    'provider': 'air_iq',
                }
            }
        }

    def _format_air_iq_flight(self, flight):
        """Format AIR iQ slice data to match frontend expectations"""
        
        ticket_id = flight.get('ticket_id', str(random.randint(1000, 9999)))
        price = float(flight.get('total_price', 0))
        if price == 0 and flight.get('fares'):
             price = float(flight['fares'].get('total', 0))
             
        segments_data = flight.get('segments', [])
        
        segments = []
        
        if not segments_data:
             # Basic structure if segments are flat
             dep_time = flight.get('departure_time', '10:00')
             arr_time = flight.get('arrival_time', '12:00')
             duration_str = flight.get('duration', '2h 0m')
             airline_code = flight.get('airline_code', 'AI')
             airline_name = flight.get('airline_name', 'Air India')
             flight_number = flight.get('flight_number', f"{airline_code}123")
             
             segments.append({
                  'origin': flight.get('origin', ''),
                  'destination': flight.get('destination', ''),
                  'depart_time': dep_time,
                  'arrival_time': arr_time,
                  'duration': duration_str,
                  'flight_number': flight_number,
                  'airline_name': airline_name,
                  'airline_code': airline_code,
                  'cabin_class': flight.get('cabin_class', 'Economy'),
                  'layover_minutes': None
             })
             
             return {
                 'id': ticket_id,
                 'airline': {
                     'code': airline_code,
                     'name': airline_name,
                     'logo': flight.get('airline_logo', f"https://logos-world.net/wp-content/uploads/2023/01/Air-India-Logo.png")
                 },
                 'flight_number': flight_number,
                 'origin': flight.get('origin', ''),
                 'destination': flight.get('destination', ''),
                 'depart_time': dep_time,
                 'arrival_time': arr_time,
                 'duration': duration_str,
                 'next_day': False,
                 'stops': 0,
                 'price': price,
                 'currency': 'INR',
                 'class': flight.get('cabin_class', 'Economy'),
                 'segments': segments
             }
        else:
             # Handling rich segments
             for seg in segments_data:
                  segments.append({
                       'origin': seg.get('origin', ''),
                       'destination': seg.get('destination', ''),
                       'depart_time': seg.get('departure_time', ''),
                       'arrival_time': seg.get('arrival_time', ''),
                       'duration': seg.get('duration', ''),
                       'flight_number': seg.get('flight_number', ''),
                       'airline_name': seg.get('airline_name', ''),
                       'airline_code': seg.get('airline_code', ''),
                       'cabin_class': seg.get('cabin_class', 'Economy'),
                       'layover_minutes': seg.get('layover_time')
                  })
             
             first_seg = segments_data[0]
             last_seg = segments_data[-1]
             airline_code = first_seg.get('airline_code', 'AI')
             
             return {
                 'id': ticket_id,
                 'airline': {
                     'code': airline_code,
                     'name': first_seg.get('airline_name', 'Airline'),
                     'logo': first_seg.get('airline_logo', f"https://logos-world.net/wp-content/uploads/2023/01/Air-India-Logo.png")
                 },
                 'flight_number': first_seg.get('flight_number', ''),
                 'origin': first_seg.get('origin', ''),
                 'destination': last_seg.get('destination', ''),
                 'depart_time': first_seg.get('departure_time', ''),
                 'arrival_time': last_seg.get('arrival_time', ''),
                 'duration': flight.get('total_duration', ''),
                 'next_day': False,
                 'stops': len(segments_data) - 1,
                 'price': price,
                 'currency': 'INR',
                 'class': first_seg.get('cabin_class', 'Economy'),
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
