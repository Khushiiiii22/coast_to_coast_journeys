"""
Mock Flight Service
Generates realistic flight data for demo purposes since no live Flight API is available.
"""
import random
from datetime import datetime, timedelta
import hashlib

class FlightService:
    def __init__(self):
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
            'DXB': {'name': 'Dubai International Airport', 'city': 'Dubai', 'country': 'UAE'},
            'LHR': {'name': 'Heathrow Airport', 'city': 'London', 'country': 'UK'},
            'JFK': {'name': 'John F. Kennedy International Airport', 'city': 'New York', 'country': 'USA'},
            'SIN': {'name': 'Changi Airport', 'city': 'Singapore', 'country': 'Singapore'},
            'CDG': {'name': 'Charles de Gaulle Airport', 'city': 'Paris', 'country': 'France'},
            'FRA': {'name': 'Frankfurt Airport', 'city': 'Frankfurt', 'country': 'Germany'}
        }

    def search_flights(self, origin, destination, depart_date, return_date=None, adults=1, flight_class='economy'):
        """Search flights with realistic mock data"""
        results = {
            'outbound': self._generate_flights(origin, destination, depart_date, adults, flight_class),
            'inbound': []
        }
        
        if return_date:
            results['inbound'] = self._generate_flights(destination, origin, return_date, adults, flight_class)
            
        return {
            'success': True,
            'data': results
        }

    def suggest(self, query):
        """Autocomplete for airports"""
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
        
        # Add a generic result if query looks like a code but not in our list
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
        """Generate 5-10 realistic flight options"""
        flights = []
        num_flights = random.randint(5, 12)
        
        # Base price calculation based on distance/random
        base_price = random.randint(100, 800) if flight_class == 'economy' else random.randint(500, 2500)
        
        for i in range(num_flights):
            airline = random.choice(self.airlines)
            flight_num = f"{airline['code']}{random.randint(100, 999)}"
            
            # Times
            hour = random.randint(0, 23)
            minute = random.choice([0, 15, 30, 45])
            depart_time = f"{hour:02d}:{minute:02d}"
            
            # Duration (2h to 10h)
            duration_mins = random.randint(120, 600)
            duration_hours = duration_mins // 60
            duration_rem_mins = duration_mins % 60
            duration_str = f"{duration_hours}h {duration_rem_mins}m"
            
            # Arrival Time logic
            arrival_mins_total = hour * 60 + minute + duration_mins
            arr_hour = (arrival_mins_total // 60) % 24
            arr_min = arrival_mins_total % 60
            arrival_time = f"{arr_hour:02d}:{arr_min:02d}"
            next_day = arrival_mins_total >= 24 * 60
            
            # Stops
            stops = random.choice([0, 0, 0, 1, 1, 2]) # Weight towards direct
            price = base_price * (1.2 if stops == 0 else 0.8) # Direct flights more expensive
            price += random.randint(-50, 50)
            
            flt = {
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
                'stop_city': random.choice(list(self.airports.keys())) if stops > 0 else None,
                'price': int(price),
                'currency': 'USD',
                'class': flight_class
            }
            flights.append(flt)
            
        # Sort by price
        flights.sort(key=lambda x: x['price'])
        return flights

flight_service = FlightService()
