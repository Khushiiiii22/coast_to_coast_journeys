from flask import Blueprint, request, jsonify
from services.flight_service import flight_service

flight_bp = Blueprint('flight', __name__, url_prefix='/api/flights')

@flight_bp.route('/search', methods=['POST'])
def search_flights():
    """
    Search for flights
    Request Body:
    {
        "from": "DEL",
        "to": "LHR",
        "departDate": "2026-02-01",
        "returnDate": "2026-02-10", (optional)
        "adults": 1,
        "class": "Economy"
    }
    """
    try:
        data = request.get_json()
        
        required = ['from', 'to', 'departDate']
        for field in required:
            if field not in data:
                return jsonify({'success': False, 'error': f'Missing field: {field}'}), 400
        
        result = flight_service.search_flights(
            origin=data['from'],
            destination=data['to'],
            depart_date=data['departDate'],
            return_date=data.get('returnDate'),
            adults=int(data.get('adults', 1)),
            flight_class=data.get('class', 'economy').lower()
        )
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@flight_bp.route('/suggest', methods=['POST'])
def suggest_airports():
    """
    Suggest airports for autocomplete
    Request Body:
    {
        "query": "New York"
    }
    """
    try:
        data = request.get_json()
        query = data.get('query', '')
        
        if len(query) < 2:
            return jsonify({'success': False, 'error': 'Query too short'}), 400
            
        result = flight_service.suggest(query)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
