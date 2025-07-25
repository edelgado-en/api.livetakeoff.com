import os
import requests

class FlightawareApiService():

    def get_flight_info(self, ident, start_date):
        # start_date must be in the format of 'YYYY-MM-DD'
        # Base URL for the FlightAware API
        base_url = ''

        if start_date:
            base_url = f'https://aeroapi.flightaware.com/aeroapi/flights/{ident}?start={start_date}'

            # This will ensure we get more than 20 flights for comparison purposes
            base_url += '&max_pages=2'

        else:
            base_url = f'https://aeroapi.flightaware.com/aeroapi/flights/{ident}'
            # This will ensure we get more than 20 flights for comparison purposes
            base_url += '?max_pages=2'
        

        api_key = os.environ.get('FLIGHTAWARE_API_KEY')

        # Headers for authentication
        headers = {
            'x-apikey': f'{api_key}' 
        }

        # Make a GET request to the FlightAware API
        response = requests.get(base_url, headers=headers)

        # Check if the request was successful
        if response.status_code == 200:
            return response.json()
        else:
           print(f"Failed to retrieve data. Status code: {response.status_code}")
           print(response.text)