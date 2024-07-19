import threading
import requests
import json
import time
import GLOBALS

OPENUV_API_KEY = GLOBALS.OPENUV_API_KEY

def request_weather_json_general(lat_lng):
    """
    Requests the first json returned from the weather.gov api.
    This json contains URLs to various subset api jsons.
    The json will be set as self.current_weather_general_json.'

    https://weather-gov.github.io/api/general-faqs
    """
    base_url = "https://api.weather.gov/points/"
    url_query = base_url + str(lat_lng[0]) + "," + str(lat_lng[1])
    print(f"NWS API Request - coordinates: {lat_lng}\nurl: {url_query}")
    response = requests.get(url_query)
    response = response.json()
    print("API REQUEST_WEATHER_JSON_GENERAL", response["properties"])
    return response


def get_json_from_url(url):
    return requests.get(url).json()


def get_openuv_json(lat_lng):
    url = f"https://api.openuv.io/api/v1/uv?lat={lat_lng[0]}&lng={lat_lng[1]}&alt=&dt="
    api_key = OPENUV_API_KEY

    headers = {
        'x-access-token': api_key,
        'Content-Type': 'application/json'
    }

    response = requests.get(url, headers=headers)
    response = response.json()
    return response
