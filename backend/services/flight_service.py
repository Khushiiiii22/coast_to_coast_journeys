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
        self.access_token = Config.DUFFEL_ACCESS_TOKEN
        self.client = None
        if self.access_token:
            try:
                self.client = Duffel(access_token=self.access_token)
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
        """Perform real search using Duffel API"""
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
        
        # Create offer request
        offer_request = self.client.offer_requests.create() \
            .slices(slices) \
            .passengers(passengers) \
            .cabin_class(cabin_class_map.get(flight_class, 'economy')) \
            .execute()

        # Retrieve offers
        offers = self.client.offers.list(offer_request.id)
        
        formatted_outbound = []
        formatted_inbound = []

        for offer in offers:
            # We simplify for demo purposes, picking the first slice as outbound
            # and second as inbound if round-trip
            outbound_slice = offer.slices[0]
            inbound_slice = offer.slices[1] if len(offer.slices) > 1 else None

            price_data = offer.total_amount
            currency = offer.total_currency

            outbound_flight = self._format_duffel_slice(offer.id, outbound_slice, price_data, currency)
            formatted_outbound.append(outbound_flight)

            if inbound_slice:
                inbound_flight = self._format_duffel_slice(offer.id, inbound_slice, price_data, currency, is_inbound=True)
                formatted_inbound.append(inbound_flight)

        return {
            'success': True,
            'data': {
                'outbound': formatted_outbound,
                'inbound': formatted_inbound,
                'meta': {
                    'provider': 'duffel',
                    'offer_request_id': offer_request.id
                }
            }
        }

    def _format_duffel_slice(self, offer_id, fslice, price, currency, is_inbound=False):
        """Format Duffel slice data to match frontend expectations"""
        # For simplicity, we take the first segment's details
        segment = fslice.segments[0]
        airline = segment.marketing_carrier
        
        return {
            'id': f"{offer_id}_{'in' if is_inbound else 'out'}",
            'airline': {
                'code': airline.iata_code,
                'name': airline.name,
                'logo': f"https://res.cloudinary.com/duffel/image/upload/v1582230000/intermediary/carrier-logos/{airline.iata_code}.png"
            },
            'flight_number': f"{airline.iata_code}{segment.marketing_carrier_flight_number}",
            'origin': segment.origin.iata_code,
            'destination': segment.destination.iata_code,
            'depart_time': datetime.fromisoformat(segment.departing_at).strftime('%H:%M'),
            'arrival_time': datetime.fromisoformat(segment.arriving_at).strftime('%H:%M'),
            'duration': f"{fslice.duration[2:].lower().replace('h', 'h ')}", # Converts PT10H20M
            'next_day': False, # Could be calculated from dates
            'stops': len(fslice.segments) - 1,
            'price': float(price),
            'currency': currency,
            'class': segment.cabin_class
        }

    def suggest(self, query):
        """Autocomplete for airports - stays mock for now to avoid heavy API usage"""
        query = query.upper()
        suggestions = []
        
        for code, details in self.airports.items():
            if (query in code or 
                query in details['city'].upper() or 
                query in details['country'].upper()):
                suggestions.append({
                    'code': code,
                    'name': details['name'],
                    'city': details['city'],
                    'country': details['country'],
                    'label': f"{details['city']} ({code})"
                })
        
        if not suggestions and len(query) == 3:
            suggestions.append({
                'code': query,
                'name': f"{query} International Airport",
                'city': query,
                'country': 'Unknown',
                'label': f"{query} ({query})"
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
                'class': flight_class
            })
        flights.sort(key=lambda x: x['price'])
        return flights

flight_service = FlightService()
