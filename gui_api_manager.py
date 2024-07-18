import threading
import requests
import json
import time
import GLOBALS

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

GOOGLE_API_KEY = GLOBALS.GOOGLE_API_KEY


class APIManager:
    """
    API Manager
    """
    def __init__(self, manager):
        self.manager = manager
        self.api_request = manager.api_request_list
        self.api_response = manager.api_response_list
        self.query_prediction_list = []
        # An array so that previous searches can be easily viewed and swapped to
        self.chosen_query = []

    def run(self):
        while True:
            if len(self.api_request) > 0:
                # print("API_REQUEST > 0")
                self.call_correct_api()
            time.sleep(.1)

    def call_correct_api(self):
        """
        Determines the right API to call based on input message
        """
        message = self.api_request.pop(0)
        if message["service"] == "autocomplete":
            self.request_place_autocomplete_api(message["data"])
        elif message["service"] == "geocoding":
            self.request_geocode_api(message["data"])
        else:
            print("[Call Correct API Failed]")

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

        # print(f"API Request - url: {url}\npayload: {payload}\nheaders: {headers}")
        response = requests.post(url, data=payload, headers=headers)
        response = response.json()
        # print(f"Response Message: {response}")
        self.query_prediction_list = []
        if "suggestions" in response:
            for _ in response["suggestions"]:
                self.query_prediction_list.append(_['placePrediction']['text']['text'])
            self.api_response.append({"service": "autocomplete",
                                 "data": self.query_prediction_list,
                                 "origin_data": current_search_query})

        else:
            # print("NO VALID AUTOCOMPLETES")
            self.api_response.append({"service": "autocomplete",
                                      "data": [False],
                                      "origin_data": current_search_query})
