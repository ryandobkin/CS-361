from inbound_message_manager import InboundMessageManager
from outbound_message_manager import OutboundMessageManager
import forecast_api_manager
import threading
import time
import json
import eel


class ForecastController:
    """
    The main manager object for the forecast service.
    """
    def __init__(self):
        self.ip = '127.0.0.2'
        self.port = 23457
        self.socket_list = {"frontend_manager": ["127.0.0.1", 23456]}
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
        self.temp_unit = 'F'
        self.is_test = True

    def run(self):
        """
        The main loop of the forecast service.
        """
        while True:
            try:
                if self.is_test:
                    self.is_test = False
                    self.inbound_queue.append({"socket": ['127.0.0.2', 23457], "type": "request",
                                               "service": "forecast", "data": [33.6041944, -117.8738554]})
                if len(self.inbound_queue) > 0:
                    self.last_request = self.inbound_queue.pop(0)
                    if self.last_request["type"] == "request" and self.last_request["service"] == "forecast":
                        self.get_general_weather_json(self.last_request)
                        self.get_general_forecast_data(self.points_json)
                        self.get_openuv_data()
                        self.parse_daily_forecast()
                        self.parse_gridpoints_forecast()
                        self.parse_openuv_data()
                        self.parse_hourly_forecast()
                        self.update_gui()
                        #self.print_all()
                time.sleep(0.5)
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

    def update_gui(self):
        """
        Updates the GUI manager by creating message with update data and sending through frontend_manager
        """
        max_min_arr = []
        for _ in self.points_data_daily_dict:
            max_min_arr.append({"maxTemperature": _['maxTemperature'], "minTemperature": _['minTemperature']})
        outbound_daily_forecast_dict = {}
        daily_arr = [self.forecast_daily_dict[0]]
        for daily_dict in self.forecast_daily_dict:
            if daily_dict["isDaytime"] is True and daily_dict != daily_arr[0]:
                daily_arr.append(daily_dict)
        for _ in range(7):
            daily_update = {
                f"day_{_}": {
                     "maxTemperature": self.points_data_daily_dict[_]['maxTemperature'],
                     "minTemperature": self.points_data_daily_dict[_]['minTemperature'],
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
                "uv_max": self.open_uv_data['uv_max'],
                "uv_index": 'GET INDEX FUNC'
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
            "pressure": {"pressure": "TODO"},
            "now": {
                "temperature": self.forecast_hourly_dict[0]['temperature'],
                "apparentTemperature": self.points_data_widget_dict['apparentTemperature'],
                "maxTemperature": self.points_data_daily_dict[0]['maxTemperature'],
                "minTemperature": self.points_data_daily_dict[0]['minTemperature'],
                "shortForecast": self.forecast_hourly_dict[0]['shortForecast']}
        }
        update_data = {
            "daily_forecast": outbound_daily_forecast_dict,
            "hourly_forecast": outbound_hourly_forecast_dict,
            "widget_forecast": outbound_widget_forecast_dict,
            "alert_forecast": self.active_alert_dict}
        outbound_update_message = {"socket": self.socket_list["frontend_manager"],
                                   "type": "response", "service": "forecast",
                                   "data": update_data}
        self.outbound_queue.append(outbound_update_message)
        outbound_update_message = json.dumps(outbound_update_message)
        print(outbound_update_message)

    def get_general_weather_json(self, incoming_data):
        """
        Gets the general weather json for a group of gridpoints.
        https://api.weather.gov/points/lat,lng
        Sets self.general_weather_json as json and self.grid_id as gridId (i.e. KLWX)
        """
        coordinates = incoming_data["data"]
        self.points_json = forecast_api_manager.request_weather_json_general(coordinates)
        self.lng_lat = coordinates
        return True

    def get_general_forecast_data(self, incoming_json):
        """
        Using general weather json, updates several values for weather service.
        """
        self.forecast_gridpoints_url = incoming_json["properties"]["forecastGridData"]
        self.forecast_daily_url = incoming_json["properties"]["forecast"]
        self.forecast_hourly_url = incoming_json["properties"]["forecastHourly"]
        self.grid_id = incoming_json["properties"]["gridId"]
        self.time_zone = incoming_json["properties"]["timeZone"]
        self.radar_station = incoming_json["properties"]["radarStation"]
        zone_id = forecast_api_manager.get_json_from_url(incoming_json["properties"]["forecastZone"])
        self.zone_id = zone_id["properties"]["id"]
        self.active_alert_url = f"api.weather.gov/alerts/active/zone/{self.zone_id}"

    def parse_daily_forecast(self):
        """
        Uses general weather forecast to get daily forecast.
        https://api.weather.gov/gridpoints/LWX/97,71/forecast
        Gets 7 days of values, broken into up to 12 hour increments in 14 periods.
        Updates self.forecast_daily_dict to:
        [{"temperature: 89, "rain_prob": 30, "wind_speed": "8 mph",
        "short_forecast": "Isolated Showers And Thunderstorms", "long_forecast": "..."}, ...]
        """
        fc_data = forecast_api_manager.get_json_from_url(self.forecast_daily_url)
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
        fc_data = forecast_api_manager.get_json_from_url(self.forecast_hourly_url)
        hourly_arr = []
        pd_pre = fc_data["properties"]["periods"]
        # for _ in pd:
        for _ in range(24):
            pd = pd_pre[_]
            hour_dict = {"startTime": pd["startTime"], "endTime": pd["endTime"], "temperature": pd["temperature"],
                         "temperatureUnit": pd["temperatureUnit"],
                         "probabilityOfPrecipitation": pd["probabilityOfPrecipitation"]["value"],
                         "dewPoint": pd["dewpoint"]["value"], "relativeHumidity": pd["relativeHumidity"]["value"],
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
        fc_data = forecast_api_manager.get_json_from_url(self.forecast_gridpoints_url)
        daily_arr = []
        pd = fc_data["properties"]
        sky_dict = self.parse_sky_cover_condition(pd["skyCover"])
        weather_dict = self.parse_weather(pd["weather"])
        for _ in pd["weather"]["values"]:
            break
        if self.temp_unit == 'F':
            for _ in range(7):
                daily_dict = {
                    "maxTemperature": int(pd["maxTemperature"]["values"][_]["value"] * 9/5 + 32),
                    "minTemperature": int(pd["minTemperature"]["values"][_]["value"] * 9/5 + 32)
                    }
                daily_arr.append(daily_dict)
            widget_dict = {
                "dewpoint": pd["dewpoint"]["values"][0]["value"] * 9/5 + 32,
                "relativeHumidity": pd["relativeHumidity"]["values"][0]["value"],
                "apparentTemperature": pd["apparentTemperature"]["values"][0]["value"] * 9/5 + 32,
                "windChill": pd["windChill"]["values"][0]["value"],
                "windDirection": pd["windDirection"]["values"][0]["value"],
                "windSpeed": pd["windSpeed"]["values"][0]["value"],
                "windGust": pd["windGust"]["values"][0]["value"],
                "transportWindSpeed": pd["transportWindSpeed"]["values"][0]["value"],
                "transportWindDirection": pd["transportWindDirection"]["values"][0]["value"],
                "hazards": pd["hazards"]["values"][0]["value"]
            }
        self.points_data_daily_dict = daily_arr
        self.points_data_widget_dict = widget_dict

    def parse_sky_cover_condition(self, dict):
        """
        When passed the skyCover dictionary of the points json, passed back relevant interpreted information.
        "values": [
            {
              "validTime": "2024-07-22T14:00:00+00:00/PT1H",
              "value": 100
            }, {...}...]
        """
        skyCover_list = []
        current_day_list = []
        current_day = ""
        for hrDict in dict["values"]:
            sky_datetime, sky_offset = hrDict["validTime"].split('/')
            sky_date, sky_time = sky_datetime.split('T')
            sky_date, sky_time = sky_date.split('-'), sky_time.split('+')
            hour_dict = {"year": sky_date[0], "month": sky_date[1], "day": sky_date[2], "hour": sky_time[0],
                         "utc_offset": sky_time[1], "duration": sky_offset}
            cloud_cover = hrDict["value"]

            if 5 <= int(hour_dict["hour"][:2]) <= 20:
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
            if hour_dict["day"] == current_day:
                current_day_list.append(hour_dict)
            else:
                current_day = hour_dict["day"]
                skyCover_list.append(current_day_list)
                current_day_list = [hour_dict]
        skyCover_list.append(current_day_list)
        skyCover_list.pop(0)
        # print("skyCover_list: ", skyCover_list)
        return skyCover_list

    def parse_weather(self, weather_dict):
        """
        Parses the weather dict from the gridpoints json.
        """
        ret_weather_dict = {}
        i = 0
        for dDict in weather_dict["values"]:
            datetime, duration = dDict["validTime"].split('/')
            date, sky_time = datetime.split('T')
            date, sky_time = date.split('-'), sky_time.split('+')
            dict = {"year": date[0], "month": date[1], "day": date[2], "hour": sky_time[0],
                    "utc_offset": sky_time[1], "duration": duration, "coverage": dDict["value"][0]["coverage"],
                    "weather": dDict["value"][0]["weather"], "intensity": dDict["value"][0]["intensity"],
                    "visibility": dDict["value"][0]["visibility"]["value"], "attributes": dDict["value"][0]["attributes"]}
            ret_weather_dict.update({i: dict})
            i += 1
        return ret_weather_dict

    def parse_alert_forecast(self):
        """
        Gets and parses the active alerts for the zoneId.
        https://api.weather.gov/alerts/active/zone/CAZ552

        Updates self.active_alert_dict with all relevant data:
        {"areaDesc": "San Diego Coastal Areas; Orange County Coastal", "effective": "2024-07-18T13:34:00-07:00",
        "ends": "2024-07-18T21:00:00-07:00", "status": "Actual", "severity": "Moderate", "certainty": "Likely",
        "urgency": "Expected", "event": "Beach Hazards Statement", "senderName": "NWS San Diego CA",
        "headline": "brief description", "description": "extensive description", "instruction": "remain out of water",
        "response": "Avoid"}
        """
        fc_data = forecast_api_manager.get_json_from_url(self.active_alert_url)
        pd = fc_data["features"]["properties"]
        alert_data = {"areaDesc": pd["areaDesc"], "effective": pd["effective"], "ends": pd["ends"],
                      "status": pd["status"], "severity": pd["severity"], "certainty": pd["certainty"],
                      "urgency": pd["certainty"], "event": pd["event"], "senderName": pd["senderName"],
                      "headline": pd["headline"], "description": pd["description"], "instruction": pd["instruction"],
                      "response": pd["response"]}
        self.active_alert_dict = alert_data

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
        response_json = forecast_api_manager.get_openuv_json(self.lng_lat)
        self.open_uv_json = response_json


if __name__ == '__main__':
    forecast_controller = ForecastController()

    # Starts the incoming message loop thread
    inbound_message_manager = InboundMessageManager(forecast_controller)
    inbound_message_manager_thread = threading.Thread(target=inbound_message_manager.run, daemon=True)
    inbound_message_manager_thread.start()

    # Starts the outgoing message loop thread
    outbound_message_manager = OutboundMessageManager(forecast_controller)
    outbound_message_manager_thread = threading.Thread(target=outbound_message_manager.run, daemon=True)
    outbound_message_manager_thread.start()

    forecast_controller.run()

