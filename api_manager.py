from inbound_message_manager import InboundMessageManager
from outbound_message_manager import OutboundMessageManager
import threading
import requests
import json
import time

# https://www.weather.gov/documentation/services-web-api#/default/alerts_active_zone
# https://weather-gov.github.io/api/general-faqs
# https://developers.google.com/maps/documentation/geocoding/start


# Resolve location to gridpointer
# use  https://api.weather.gov/points/{lat},{lon}
# Will return a json with more sub-links
# "properties" -> forecast, forecastHourly,
# For city name, need to use google maps API to geocode and turn into coords for NWS API
# https://developers.google.com/maps/documentation/geocoding/start
# For 1600 Amphitheatre Parkway, Mountain View, CA:
# https://maps.googleapis.com/maps/api/geocode/json?address=1600+Amphitheatre+Parkway,+Mountain+View,+CA&key=YOUR_API_KEY
# Google Cloud Manager
# https://console.cloud.google.com/apis/credentials?project=weatherapplicationcs361&supportedpurview=project

GOOGLE_API_KEY = 'AIzaSyC_T_HMtLF-SNwPof0CNAkkiyfKAwNQVt4'

class APIManager:
    """
    API Manager
    """
    def __init__(self):
        self.inbound_port = 23457
        self.inbound_ip = '127.0.0.2'
        self.outbound_port = 23456
        self.outbound_ip = '127.0.0.1'
        self.outbound_queue = ['API Manager Outbound 1']
        self.inbound_queue = []
        self.query_prediction_list = []
        # An array so that previous searches can be easily viewed and swapped to
        self.chosen_query = []

    def manager(self):
        while True:
            self.request_geocode_api()
            time.sleep(5)

    def request_place_autocomplete_api(self, current_search_query="Alt"):
        """
        Requests the Google places autocomplete (new) API for search query dropdown autocompletes.

        Returns a JSON including the 5 most relevant city autocomplete predictions.
        These should be displayed in the search dropdown.

        https://developers.google.com/maps/documentation/places/web-service/place-autocomplete
        """

        url = "https://places.googleapis.com/v1/places:autocomplete"
        api_key = GOOGLE_API_KEY

        params = {
            "input": current_search_query,
            "includedPrimaryTypes": "(cities)"
        }
        payload = json.dumps(params)
        headers = {
            'Content-Type': 'application/json',
            'X-Goog-Api-Key': api_key
        }

        print(f"API Request - url: {url}\npayload: {payload}\nheaders: {headers}")
        response = requests.post(url, data=payload, headers=headers)
        response = response.json()
        self.query_prediction_list = []
        for _ in range(5):
            self.query_prediction_list.append(response['suggestions'][_]['placePrediction']['text']['text'])
        print(self.query_prediction_list)

    def request_geocode_api(self, chosen_query="Newport Beach, CA"):
        """
        Requests the Google maps geocoding api for coordinates based on chosen query location.
        Returns a list of (latitude, longitude) to 7 decimal places around the center of the city.


        https://developers.google.com/maps/documentation/geocoding/requests-geocoding
        """
        base_url = "https://maps.googleapis.com/maps/api/geocode/json?address="
        api_key = GOOGLE_API_KEY

        url_query = chosen_query.replace(" ", "+")
        request_url = base_url + url_query + '&key=' + api_key

        print(f"Geocoding API Request - location: {chosen_query}\nurl: {request_url}")
        response = requests.get(request_url)
        response = response.json()
        print(response)
        if response["status"] != "OK":
            print("FAIL - RETRYING")
            self.request_geocode_api()
        query_geocode = (response["results"][0]["geometry"]["location"]["lat"],
                         response["results"][0]["geometry"]["location"]["lng"])
        print(query_geocode)
        return query_geocode



if __name__ == '__main__':
    api_manager = APIManager()

    # Starts the incoming message loop thread
    inbound_message_manager = InboundMessageManager(api_manager)
    incoming_message_manager_thread = threading.Thread(target=inbound_message_manager.run, daemon=True)
    #incoming_message_manager_thread.start()

    # Starts the outgoing message loop thread
    outbound_message_manager = OutboundMessageManager(api_manager)
    outgoing_message_manager_thread = threading.Thread(target=outbound_message_manager.run, daemon=True)
    #outgoing_message_manager_thread.start()

    api_manager.manager()
