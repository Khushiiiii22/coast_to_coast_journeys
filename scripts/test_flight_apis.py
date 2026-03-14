import requests
import json
from datetime import datetime, timedelta

def test_flight_status():
    print("Testing Flight Status API...")
    url = "https://flight-status.p-eu.rapidapi.com/flightstatus"
    
    # testing with a simpler query to see if it works
    querystring = {
        "movementType":"A",
        "pageSize":"min=0 to max=100",
        "departureCity":"AMS, JFK, HKG",
        "sorted":"true",
        "destination":"AMS, JFK, HKG",
        "serviceType[0]":"J, G",
        "timeOriginType":"S",
        "startRange":"2016-01-01T00:00:00Z",
        "carrierCode[0]":"KLM has IATA airline code 'KL'",
        "arrivalCity":"AMS, JFK, HKG",
        "timeType":"U",
        "flightNumber":"0641",
        "origin":"AMS, JFK, HKG",
        "endRange":"2016-01-01T23:59:59Z",
        "aircraftRegistration":"PHPQB",
        "consumerHost":"KL",
        "operationalSuffix":"D",
        "operatingAirlineCode[0]":"AF, KL",
        "aircraftType":"747"
    }

    headers = {
        "x-rapidapi-key": "e56a30d42dmshfe31769548df189p15e3aejsn93469e6f98cc",
        "x-rapidapi-host": "flight-status.iata.rapidapi.com",
        "Accept": "application/hal+json",
        "Accept-Language": "en-GB"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Status Code: {response.status_code}")
        print(response.json())
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

def test_customer_flight_info():
    print("Testing Customer Flight Info API...")
    url = "https://customer-flight-info.p-eu.rapidapi.com/customerflightinformation/route/LHR/DXB/2026-03-20"
    
    headers = {
        "x-rapidapi-key": "e56a30d42dmshfe31769548df189p15e3aejsn93469e6f98cc",
        "x-rapidapi-host": "customer-flight-info.iata.rapidapi.com"
        # "Authorization": "<REQUIRED>" # User's code said REQUIRED, let's see if rapidapi key is enough
    }

    try:
        response = requests.get(url, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(response.json())
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

def test_flight_schedules():
    print("Testing Flight Schedules API...")
    url = "https://flight-schedules1.p-eu.rapidapi.com/flex/schedules/rest/v1/json/from/PDX/departing/2026/03/20/14"
    
    querystring = {"extendedOptions[0]":"useHttpErrors","codeType":"FS"}

    headers = {
        "x-rapidapi-key": "e56a30d42dmshfe31769548df189p15e3aejsn93469e6f98cc",
        "x-rapidapi-host": "flight-schedules1.iata.rapidapi.com"
        # "appId": "<REQUIRED>"
    }

    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Status Code: {response.status_code}")
        print(response.json())
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    print("Starting API Tests...\n")
    test_flight_status()
    # Let's also do a realistic current search on flight status
    print("Testing Flight Status API with current dates...\n")
    today = datetime.now()
    tomorrow = today + timedelta(days=1)
    
    url = "https://flight-status.p-eu.rapidapi.com/flightstatus"
    headers = {
        "x-rapidapi-key": "e56a30d42dmshfe31769548df189p15e3aejsn93469e6f98cc",
        "x-rapidapi-host": "flight-status.iata.rapidapi.com",
        "Accept": "application/hal+json",
        "Accept-Language": "en-GB"
    }
    querystring = {
        "origin": "LHR",
        "destination": "DXB",
        "startRange": f"{today.strftime('%Y-%m-%dT00:00:00Z')}",
        "endRange": f"{tomorrow.strftime('%Y-%m-%dT23:59:59Z')}"
    }
    try:
        response = requests.get(url, headers=headers, params=querystring)
        print(f"Status Code (Current): {response.status_code}")
        print(response.text[:500])
        print("-" * 50)
    except Exception as e:
        print(f"Error: {e}")
        
    test_customer_flight_info()
    test_flight_schedules()
