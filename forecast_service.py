import inbound_message_manager
import outbound_message_manager
import forecast_api_manager
import threading
import time
import json
from datetime import datetime
import eel
import requests

# Will use sample request and will not request from OpenUV API, using sample response instead
IS_TEST = False
DATETIME = datetime


class ForecastController:
    """
    The main manager object for the forecast service.
    """
    def __init__(self):
        self.socket_port_in = '5556'
        self.socket_port_c_to_f_microservice = '5555'
        self.socket_port_api_interface_microservice = '5559'
        self.socket_port_gui_manager = '5558'
        self.forecast_gridpoints_url = None
        self.points_json = None
        self.forecast_daily_url = None
        self.forecast_daily_dict = None
        self.points_data_daily_dict = None
        self.active_alert_url = None
        self.active_alert_dict = None
        self.forecast_hourly_url = None
        self.forecast_hourly_dict = None
        self.points_data_widget_dict = None
        self.open_uv_json = None
        self.open_uv_data = None
        self.grid_id = None
        self.zone_id = None
        self.radar_station = None
        self.lng_lat = None
        self.time_zone = None
        self.last_update = None
        self.last_request = None
        self.outbound_queue = []
        self.inbound_queue = []
        self.is_test = IS_TEST
        self.disable_uv_api = True

    def run(self):
        """
        The main loop of the forecast service.
        """
        #self.parse_weather(None)
        #exit()
        while True:
            try:
                if self.is_test:
                    self.is_test = False
                    self.disable_uv_api = True
                    self.test_cord_list = {"Newport": [36.6041944, -117.8738554], "Durham": [36.0763129, -78.71559],
                                           "Palm Springs": [33.829722, -116.534434]}
                    self.inbound_queue.append({"socket": ['127.0.0.2', 23457], "type": "request",
                                               "service": "forecast", "data": self.test_cord_list["Palm Springs"]})
                if len(self.inbound_queue) > 0:
                    self.last_request = self.inbound_queue.pop(0)
                    if self.last_request["service"] == "forecast":
                        self.get_general_weather_json(self.last_request)
                        self.get_general_forecast_data(self.points_json)
                        self.get_openuv_data()
                        self.parse_daily_forecast()
                        self.parse_gridpoints_forecast()
                        self.parse_openuv_data()
                        self.parse_hourly_forecast()
                        self.parse_alert_forecast()
                        self.update_gui()
                        #self.print_all()
                time.sleep(0.1)
            except KeyboardInterrupt:
                print("Error")
                exit(0)
            time.sleep(0.5)

    def print_all(self):
        thing_list = [{"forecast_daily_dict": self.forecast_daily_dict},
                      {"points_forecast_daily_dict": self.points_data_daily_dict},
                      {"points_forecast_widget_dict": self.points_data_widget_dict},
                      {"active_alerts_dict": self.active_alert_dict}, {"open_uv_dict": self.open_uv_data},
                      {"forecast_hourly_dict": self.forecast_hourly_dict}]
        i = 0
        for _ in thing_list:
            print(i, _, '\n')
            i += 1

    def get_json_from_url(self, url):
        return requests.get(url).json()

    def update_gui(self):
        """
        Updates the GUI manager by creating message with update data and sending through frontend_manager
        """
        max_min_arr = []
        for _ in range(7):
            max_min_arr.append({"maxTemperature": self.points_data_daily_dict[f'maxTemperature_{_}'],
                                "minTemperature": self.points_data_daily_dict[f'minTemperature_{_}']})
        outbound_daily_forecast_dict = {}
        print("max_min_arr:", max_min_arr)
        daily_arr = [self.forecast_daily_dict[0]]
        for daily_dict in self.forecast_daily_dict:
            if daily_dict["isDaytime"] is True and daily_dict != daily_arr[0]:
                daily_arr.append(daily_dict)
        for _ in range(7):
            daily_update = {
                f"day_{_}": {
                     "maxTemperature": self.points_data_daily_dict[f'maxTemperature_{_}'],
                     "minTemperature": self.points_data_daily_dict[f'minTemperature_{_}'],
                     "name": daily_arr[_]['name'],
                     "startTime": daily_arr[_]['startTime'],
                     "endTime": daily_arr[_]['endTime'],
                     "isDaytime": daily_arr[_]['isDaytime'],
                     "temperature": daily_arr[_]['temperature'],
                     "rainProb": daily_arr[_]['rain_prob'],
                     "windSpeed": daily_arr[_]['wind_speed'],
                     "windDirection": daily_arr[_]['wind_dir'],
                     "shortForecast": daily_arr[_]['short_forecast']
                }
            }
            outbound_daily_forecast_dict.update(daily_update)
        outbound_hourly_forecast_dict = {}
        for _ in range(7):
            hourly_update = {
                f"hr_{_}": {
                    "startTime": self.forecast_hourly_dict[_]['startTime'],
                    "endTime": self.forecast_hourly_dict[_]['endTime'],
                    "temperature": self.forecast_hourly_dict[_]['temperature'],
                    "shortForecast": self.forecast_hourly_dict[_]['shortForecast']
                }
            }
            outbound_hourly_forecast_dict.update(hourly_update)
        outbound_widget_forecast_dict = {
            "sunrise_sunset": {
                "sunrise": self.open_uv_data['sunrise'],
                "sunset": self.open_uv_data['sunset'],
                "dawn": self.open_uv_data['dawn'],
                "dusk": self.open_uv_data['dusk']},
            "uv_index": {
                "uv": self.open_uv_data['uv'],
                "uv_max": self.open_uv_data['uv_max']
            },
            "wind": {
                "windChill": self.points_data_widget_dict['windChill'],
                "windDirection": self.points_data_widget_dict['windDirection'],
                "windSpeed": self.points_data_widget_dict['windSpeed'],
                "windGust": self.points_data_widget_dict['windGust']
            },
            "humidity": {
                "relativeHumidity": self.points_data_widget_dict['relativeHumidity'],
                "dewpoint": self.points_data_widget_dict['dewpoint']},
            "pressure": {},
            "now": {
                "temperature": self.forecast_hourly_dict[0]['temperature'],
                "apparentTemperature": self.points_data_widget_dict['apparentTemperature'],
                "maxTemperature": max_min_arr[0][f'maxTemperature'],
                "minTemperature": max_min_arr[0][f'minTemperature'],
                "shortForecast": self.forecast_hourly_dict[0]['shortForecast']}
        }
        update_data = {
            "daily_forecast": outbound_daily_forecast_dict,
            "hourly_forecast": outbound_hourly_forecast_dict,
            "widget_forecast": outbound_widget_forecast_dict,
            "alert_forecast": self.active_alert_dict}
        outbound_update_message = {"service": "forecast",
                                   "data": update_data}
        ack = outbound_message_manager.send_message(outbound_update_message, self.socket_port_gui_manager)
        print("Forecast Update ACK", ack)

    def convert_c_to_f(self, conversion_dict):
        """
        Sends an array of data to be converted from degc to degf.
        """
        converted_dict = outbound_message_manager.send_message(conversion_dict, self.socket_port_c_to_f_microservice)
        print(f"Original dict: {conversion_dict}\nConverted dict: {converted_dict}")
        return converted_dict

    def get_general_weather_json(self, incoming_data):
        """
        Gets the general weather json for a group of gridpoints.
        https://api.weather.gov/points/lat,lng
        Sets self.general_weather_json as json and self.grid_id as gridId (i.e. KLWX)
        """
        coordinates = incoming_data["data"]
        cord_req = {"service": "nws", "data": coordinates}
        self.points_json = outbound_message_manager.send_message(cord_req, self.socket_port_api_interface_microservice)
        self.lng_lat = coordinates
        return True

    def get_general_forecast_data(self, incoming_json):
        """
        Using general weather json, updates several values for weather service.
        """
        incoming_json = incoming_json["response"]
        self.forecast_gridpoints_url = incoming_json["properties"]["forecastGridData"]
        self.forecast_daily_url = incoming_json["properties"]["forecast"]
        self.forecast_hourly_url = incoming_json["properties"]["forecastHourly"]
        self.grid_id = incoming_json["properties"]["gridId"]
        self.time_zone = incoming_json["properties"]["timeZone"]
        self.radar_station = incoming_json["properties"]["radarStation"]
        zone_id = self.get_json_from_url(incoming_json["properties"]["forecastZone"])
        self.zone_id = zone_id["properties"]["id"]
        self.active_alert_url = f"https://api.weather.gov/alerts/active/zone/{self.zone_id}"

    def parse_daily_forecast(self):
        """
        Uses general weather forecast to get daily forecast.
        https://api.weather.gov/gridpoints/LWX/97,71/forecast
        Gets 7 days of values, broken into up to 12 hour increments in 14 periods.
        Updates self.forecast_daily_dict to:
        [{"temperature: 89, "rain_prob": 30, "wind_speed": "8 mph",
        "short_forecast": "Isolated Showers And Thunderstorms", "long_forecast": "..."}, ...]
        """
        fc_data = self.get_json_from_url(self.forecast_daily_url)
        daily_data_arr = []
        for _ in range(14):
            prop_data = fc_data["properties"]["periods"][_]
            daily_dict = {
                "name": prop_data["name"], "startTime": prop_data["startTime"], "isDaytime": prop_data["isDaytime"],
                "endTime": prop_data["endTime"], "temperature": prop_data["temperature"],
                "rain_prob": prop_data["probabilityOfPrecipitation"]["value"],
                "wind_speed": prop_data["windSpeed"], "wind_dir": prop_data["windDirection"],
                "short_forecast": prop_data["shortForecast"], "long_forecast": prop_data["detailedForecast"]}
            daily_data_arr.append(daily_dict)
        self.forecast_daily_dict = daily_data_arr

    def parse_hourly_forecast(self):
        """
        Parses the hourly forecast
        https://api.weather.gov/gridpoints/LWX/97,71/forecast/hourly

        Displays full week forecast in hour increments - 156 hours, currently supports 24
        Updates self.forecast_hourly_dict to:

        """
        fc_data = self.get_json_from_url(self.forecast_hourly_url)
        hourly_arr = []
        pd_pre = fc_data["properties"]["periods"]
        dewpoint_dict = {}
        # for _ in pd:
        for _ in range(24):
            dewpoint_dict.update({f"dewpoint_hour_{_}": '%.2f'%(pd_pre[_]["dewpoint"]["value"])})
        converted_dewpoint_dict = self.convert_c_to_f(dewpoint_dict)
        for _ in range(24):
            pd = pd_pre[_]
            hour_dict = {"startTime": pd["startTime"], "endTime": pd["endTime"], "temperature": pd["temperature"],
                         "temperatureUnit": pd["temperatureUnit"],
                         "probabilityOfPrecipitation": pd["probabilityOfPrecipitation"]["value"],
                         "dewPoint": converted_dewpoint_dict[f"dewpoint_hour_{_}"], "relativeHumidity": pd["relativeHumidity"]["value"],
                         "windSpeed": pd["windSpeed"], "windDirection": pd["windDirection"],
                         "shortForecast": pd["shortForecast"]}
            hourly_arr.append(hour_dict)
        self.forecast_hourly_dict = hourly_arr

    def parse_gridpoints_forecast(self):
        """
        Uses general weather json to get the gridpoints json. ~7k lines btw.
        https://api.weather.gov/gridpoints/LWX/97,71
        Breaks data into two groups: Data relevant for daily forecasts and data relevant for hourly forecasts.
        Hourly data is mostly too specific, so only used for current hour forecast data to fill widgets.

        Updates self.general_data_daily_dict to:
        [{"maxTemperature": 31.666666668, "minTemperature": 24.4444444443,
        "weather": {"validTime": "2024-07-18T18:00:00+00:00/PT1H", "value":
        {"coverage": "isolated", "weather": "rain_showers", "intensity": "light",
        "visibility": {"unitCode": "wmoUnit:km", "value": null"}, "attributes": []}, {...}, ...]

        Updates self.general_data_now_dict to get current hour data. Currently, does not have source
        for UV Index or  Pressure data.
        {"dewpoint": 0degC, "relativeHumidity": 0%, "apparentTemperature": 0degC, "windChill",
        "windDirection": 0deg, "windSpeed": 0kmh, "windGust": 0kmh, "visibility": 0m,
        "transportWindSpeeds": 20kmh, "transportWindDirection": 0deg, "hazards": null}
        {

        https://github.com/weather-gov/api/discussions/453
        Would like to add air quality
        """
        fc_data = self.get_json_from_url(self.forecast_gridpoints_url)
        max_min_dict = {}
        pd = fc_data["properties"]
        sky_arr = self.parse_sky_cover(pd["skyCover"])
        weather_arr = self.parse_weather(pd["weather"])
        self.forecast_generator(sky_arr, weather_arr)

        for _ in pd["weather"]["values"]:
            break
        for _ in range(7):
            max_min_dict.update({f"maxTemperature_{_}": '%.2f'%(pd["maxTemperature"]["values"][_]["value"])})
            max_min_dict.update({f"minTemperature_{_}": '%.2f'%(pd["minTemperature"]["values"][_]["value"])})
        converted_max_min_dict = self.convert_c_to_f(max_min_dict)
        converted_dew_app = self.convert_c_to_f({"dewpoint": '%.2f'%(pd["dewpoint"]["values"][0]["value"]),
                             "apparentTemperature": '%.2f'%(pd["apparentTemperature"]["values"][0]["value"])})
        widget_dict = {
            "dewpoint": converted_dew_app["dewpoint"],
            "apparentTemperature": converted_dew_app["apparentTemperature"],
            "relativeHumidity": pd["relativeHumidity"]["values"][0]["value"],
            "windChill": pd["windChill"]["values"][0]["value"],
            "windDirection": pd["windDirection"]["values"][0]["value"],
            "windSpeed": pd["windSpeed"]["values"][0]["value"],
            "windGust": pd["windGust"]["values"][0]["value"],
            "transportWindSpeed": pd["transportWindSpeed"]["values"][0]["value"],
            "transportWindDirection": pd["transportWindDirection"]["values"][0]["value"]
        }
        self.points_data_daily_dict = converted_max_min_dict
        self.points_data_widget_dict = widget_dict

    def forecast_generator(self, sky, weather):
        """
        ---not yet working---
        Creates a custom forecast based on skyCondition and weather data.
        Will create two forecasts, one will be a graphic id, and the other will be for display as shortForecast.

        Does not return anything but sets self.custom_hourly_graphic_forecast and self.custom_hourly_short_forecast.
        Will probably set it as a dict

        Parameters:
        -----------
        sky : arr
            The skyCover parsed forecast.
            [{'dateTime': datetime, 'timePeriodInHr': time_period', 'condition': condition}, {}...]
        weather : arr
            The weather parsed forecast.
            [{0: {'coverage': 'slight_chance', 'weather': 'thunderstorms', 'intensity': 'light',
            'attributes': ['small_hail', 'flooding'], 'dateTime': datetime, 'timePeriodInHr': 12}, 1: {}}, {}...]
        """
        forecast_list = {}
        valid_datetime = None
        for weather_entry in weather:
            # Loads a given values entry into weather_entry - {0:{}, 1:{}}
            i = 0
            period_forecast = {}
            for weather_sub_entry in weather_entry:
                entry_value = weather_entry[weather_sub_entry]
                # Loads a given sub entry into weather_sub_entry - {0:{}}
                coverage = entry_value["coverage"]
                weather = entry_value["weather"]
                intensity = entry_value["intensity"]
                condition = None

                for sky_entry in sky:
                    if sky_entry["dateTime"] == entry_value["dateTime"]:
                        condition = sky_entry["condition"]

                # condition and weather are the only two values that are considered for graphic
                weather_valid_dict = {"blowing_dust": None, "blowing_sand": None, "blowing_snow": 'snow',
                "drizzle": 'light_rain', "fog": 'fog', "freezing_fog": 'fog', "freezing_drizzle": 'snow_rain',
                "freezing_rain": 'snow_rain', "freezing_spray": 'snow_rain', "frost": None, "hail": 'hail',
                "haze": 'haze', "ice_crystals": None, "ice_fog": 'fog', "rain": 'rain', "rain_showers": 'rain',
                "sleet": None, "smoke": 'haze', "snow": 'snow', "snow_showers": 'snow_rain',
                "thunderstorms": 'thunderstorm_rain', "volcanic_ash": None, "water_spouts": None}
                # Values: None, snow, fog, snow_rain, haze, hail, rain, thunderstorm_rain, light_rain
                # IM SORRY I KNOW THIS IS SO BAD
                forecast_str = None
                forecast_graphic = None
                if weather:
                    if weather_valid_dict[weather] is None:
                        forecast_str = condition
                        forecast_graphic = condition
                    elif weather_valid_dict[weather] == 'snow':
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny and Snowing'
                            forecast_graphic = 'sunny_snow'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny and Snowing'
                            forecast_graphic = 'part_sunny_snow'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny and Snowing'
                            forecast_graphic = 'part_sunny_snow'
                        elif condition == "cloudy":
                            forecast_str = 'Snowing'
                            forecast_graphic = 'snow'
                    elif weather_valid_dict[weather] == ('rain' or 'light_rain'):
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny and Raining'
                            forecast_graphic = 'sunny_rain'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny and Raining'
                            forecast_graphic = 'part_sunny_rain'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny and Raining'
                            forecast_graphic = 'part_sunny_rain'
                        elif condition == "cloudy":
                            forecast_str = 'Raining'
                            forecast_graphic = 'rain'
                    elif weather_valid_dict[weather] == 'snow_rain':
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny with Freezing Rain'
                            forecast_graphic = 'sunny_snow_rain'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny with Freezing Rain'
                            forecast_graphic = 'part_sunny_snow_rain'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny with Freezing Rain'
                            forecast_graphic = 'part_sunny_snow_rain'
                        elif condition == "cloudy":
                            forecast_str = 'Overcast with Freezing Rain'
                            forecast_graphic = 'snow_rain'
                    elif weather_valid_dict[weather] == 'thunderstorm_rain':
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny with Thunderstorms'
                            forecast_graphic = 'sunny_thunderstorm'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny with Thunderstorms'
                            forecast_graphic = 'part_sunny_thunderstorm'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny with Thunderstorms'
                            forecast_graphic = 'part_sunny_thunderstorms'
                        elif condition == "cloudy":
                            forecast_str = 'Overcast Thunderstorms'
                            forecast_graphic = 'thunderstorms'
                    elif weather_valid_dict[weather] == 'hail':
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny with Hail'
                            forecast_graphic = 'sunny_hail'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny with Hail'
                            forecast_graphic = 'part_hail'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny with Hail'
                            forecast_graphic = 'part_hail'
                        elif condition == "cloudy":
                            forecast_str = 'Overcast and Hailing'
                            forecast_graphic = 'hail'
                    elif weather_valid_dict[weather] == 'haze':
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny Haze'
                            forecast_graphic = 'sunny_haze'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny Haze'
                            forecast_graphic = 'part_sunny_haze'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny Haze'
                            forecast_graphic = 'part_sunny_haze'
                        elif condition == "cloudy":
                            forecast_str = 'Cloudy Haze'
                            forecast_graphic = 'haze'
                    elif weather_valid_dict[weather] == 'fog':
                        if condition == ("sunny" or "clear"):
                            forecast_str = 'Sunny Fog'
                            forecast_graphic = 'sunny_fog'
                        elif condition == ("mostly_sunny" or "mostly_clear"):
                            forecast_str = 'Mostly Sunny and Foggy'
                            forecast_graphic = 'part_sunny_fog'
                        elif condition == ("partly_sunny" or "partly_cloudy"):
                            forecast_str = 'Partly Sunny and Foggy'
                            forecast_graphic = 'part_sunny_fog'
                        elif condition == "cloudy":
                            forecast_str = 'Overcast and Foggy'
                            forecast_graphic = 'fog'

                period_forecast.update({i: {"forecast_str": forecast_str, "forecast_graphic": forecast_graphic,
                                        "datetime": entry_value["dateTime"], "period": entry_value["timePeriodInHr"]}})
                valid_datetime = entry_value["dateTime"]
            forecast_list.update({valid_datetime: period_forecast})
        # print("AAA", forecast_list)

    def parse_sky_cover(self, sky_condition_dict):
        """
        When passed the skyCover dictionary of the points json, passed back relevant interpreted information.

        Parameters:
        -----------
        """
        sky_cover_arr = []
        for hrDict in sky_condition_dict["values"]:
            datetime_obj, time_period = self.parse_iso_time(hrDict["validTime"])
            hour_dict = {"dateTime": datetime_obj, "timePeriodInHr": time_period}
            cloud_cover = hrDict["value"]

            if 5 <= int(datetime_obj.hour) <= 20:
                is_day = True
            else:
                is_day = False

            if cloud_cover <= 12.5:
                if is_day:
                    condition = "sunny"
                else:
                    condition = "clear"
            elif cloud_cover <= 37.5:
                if is_day:
                    condition = "mostly_sunny"
                else:
                    condition = "mostly_clear"
            elif cloud_cover <= 62.5:
                if is_day:
                    condition = "partly_sunny"
                else:
                    condition = "partly_cloudy"
            elif cloud_cover <= 87.5:
                condition = "mostly_cloudy"
            elif cloud_cover <= 100:
                condition = "cloudy"
            else:
                condition = -1
            hour_dict.update({"condition": condition})
            sky_cover_arr.append(hour_dict)
        return sky_cover_arr

    def parse_weather(self, weather_dict):
        """
        Parses the weather section of the gridpoints dict.
        - "A value object representing expected weather phenomena." -
        Specifically, takes each of the values within the array, of which there can be up to 7*24, and each value
        can hold multiple sub values, and records them all. Each value is broken into an effective time period,
        typically 1h, 3h, 6h, 12h, 1d, 2d, etc.

        Parameters:
        -----------
        weather_dict
            The value of the weather: values : arr json pair from the gridpoints json.

        Returns:
        --------
        parsed_weather_arr = [{datetime_obj: {0: {'coverage': 'slight_chance', 'weather': 'thunderstorms',
        'intensity': 'light', 'attributes': ['small_hail, 'flooding'], 'dateTime': dateTimeObj, 'timePeriodInHr': 12}]
        """
        parsed_weather_arr = []
        # Iterates through values array
        for entry in weather_dict["values"]:
            weather_data_entry_dict = {}
            i = 0
            valid_time, period_time_hr = self.parse_iso_time(entry["validTime"])
            for entry_value in entry["value"]:
                w_dict = {"coverage": entry_value["coverage"], "weather": entry_value["weather"],
                          "intensity": entry_value["intensity"], "attributes": entry_value['attributes'],
                          "dateTime": valid_time, "timePeriodInHr": period_time_hr}
                weather_data_entry_dict.update({i: w_dict})
                i += 1
            parsed_weather_arr.append(weather_data_entry_dict)
        return parsed_weather_arr

    def parse_iso_time(self, incoming_time):
        """
        Parses a passed ISO format time string into a datetime object, and an int representing the period duration.

        Parameters:
        -----------
        validTime : str
            The ISO format time string. 'YYYY:DD:MM T HH:MM:SS+UTCOFFSET/P0DT0H0M'

        Returns:
        --------
        valid_time : datetime obj
            DateTime object containing the corresponding date data.
        period_time_hr : int
            Integer representing the hours of duration the time period is representing.
        """
        input_time, time_period = incoming_time.split('/')
        # input_time, time_period = '2024-07-29T21:00:00+00:00/P2DT11H'.split('/')
        valid_time = DATETIME.fromisoformat(input_time)
        # Converts period into hours - 'PT3H' or 'P1D5TH' - ignores minutes
        period_time_hr = 0
        # sets day_val to result
        if day_val := time_period.find('D'):
            if day_val != -1:
                # adds number of days * 24h to period_time_hr counter
                period_time_hr += (int(time_period[day_val - 1]) * 24)
        if hour_val := time_period.find('H'):
            if hour_val != -1:
                period_time_hr += (int(time_period[hour_val - 1]))
                if time_period[hour_val - 2] != 'T':
                    period_time_hr += (int(time_period[hour_val - 2]) * 10)
        return valid_time, period_time_hr

    def parse_alert_forecast(self):
        """
        Gets and parses the active alerts for the zoneId.
        https://api.weather.gov/alerts/active/zone/CAZ552

        Updates self.active_alert_dict with all relevant data:
        {"areaDesc": "San Diego Coastal Areas; Orange County Coastal", "effective": "2024-07-18T13:34:00-07:00",
        "expires": "2024-07-18T21:00:00-07:00", "status": "Actual", "severity": "Moderate", "certainty": "Likely",
        "urgency": "Expected", "event": "Beach Hazards Statement", "senderName": "NWS San Diego CA",
        "headline": "brief description", "description": "extensive description", "instruction": "remain out of water",
        "response": "Avoid"}
        """
        fc_data = self.get_json_from_url(self.active_alert_url)
        print(self.active_alert_url)
        if len(fc_data["features"]) != 0:
            pd = fc_data["features"][0]["properties"]
            alert_data = {"areaDesc": pd["areaDesc"], "effective": pd["effective"], "expires": pd["expires"],
                          "status": pd["status"], "severity": pd["severity"], "certainty": pd["certainty"],
                          "urgency": pd["urgency"], "event": pd["event"], "senderName": pd["senderName"],
                          "headline": pd["headline"], "description": pd["description"], "instruction": pd["instruction"],
                          "response": pd["response"]}
            self.active_alert_dict = alert_data
        else:
            self.active_alert_dict = None

    def parse_openuv_data(self):
        """
        Gets OpenUV.io API UV Forecast data.
        https://www.openuv.io/dashboard - limit to 50 requests a day
        uv-index categories: https://www.weather.gov/abr/uv-index
        could also use EPA API, not sure
        https://www.epa.gov/data/application-programming-interface-api

        Updates self.open_uv_data to:
        {"uv": 0, "uv_max": 0, "ozone": 0, "safe_exposure_time": {"st1": 0, "st2": 0, ...},
        "sunrise": "2024-07-18T12:54:53.919Z", "sunset": ""2024-07-19T03:01:16.102Z",
        "dawn": "2024-07-18T12:26:48.137Z", "dusk": "2024-07-19T03:29:21.884Z"}
        """
        open_uv_json = self.open_uv_json
        ouv = open_uv_json["result"]
        open_uv_data = {
            "uv": ouv["uv"], "uv_max": ouv["uv_max"], "ozone": ouv["ozone"],
            "safe_exposure_time": ouv["safe_exposure_time"], "sunrise": ouv["sun_info"]["sun_times"]["sunrise"],
            "sunset": ouv["sun_info"]["sun_times"]["sunset"], "dawn": ouv["sun_info"]["sun_times"]["dawn"],
            "dusk": ouv["sun_info"]["sun_times"]["dusk"]
        }
        self.open_uv_data = open_uv_data

    def get_openuv_data(self):
        """
        Gets the relevant json from OpenUV.io API.
        https://www.openuv.io/dashboard
        """
        if self.disable_uv_api:
            f = open('openuv_example.json')
            response_json = json.load(f)
            f.close()
        else:
            response_json = forecast_api_manager.get_openuv_json(self.lng_lat)
        self.open_uv_json = response_json


if __name__ == '__main__':
    forecast_controller = ForecastController()

    # Starts the incoming message loop thread
    InboundMessageManager = inbound_message_manager.InboundMessageManager(forecast_controller)
    inbound_message_manager_thread = threading.Thread(target=InboundMessageManager.receive_message, daemon=True)
    inbound_message_manager_thread.start()

    forecast_controller.run()

