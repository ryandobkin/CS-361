from inbound_message_manager import InboundMessageManager
from outbound_message_manager import OutboundMessageManager
import forecast_api_manager
import threading
import time
import eel


class ForecastController:
    """
    The main manager object for the forecast service.
    """
    def __init__(self):
        self.forecast_gridpoints = None
        self.general_weather_json = None
        self.forecast_daily_url = None
        self.forecast_hourly_url = None
        self.grid_id = None
        self.radar_station = None
        self.time_zone = None
        self.last_update = None
        self.outbound_queue = []
        self.inbound_queue = []

    def run(self):
        """
        The main loop of the forecast service.
        """
        while True:
            try:
                if len(self.inbound_queue) > 0:
                    self.get_general_weather_json(self.inbound_queue.pop(0))
                    self.get_general_forecast_data(self.general_weather_json)
                    self.parse_daily_forecast()
                    self.parse_gridpoints_forecast()

                time.sleep(0.5)
            except TypeError or KeyboardInterrupt:
                print("Error")
                exit(0)

    def get_general_weather_json(self, incoming_data):
        coordinates = incoming_data["data"]
        self.general_weather_json = forecast_api_manager.request_weather_json_general(coordinates)
        self.grid_id = self.general_weather_json["properties"]["gridId"]
        return True

    def get_general_forecast_data(self, incoming_json):
        self.forecast_gridpoints = incoming_json["properties"]["forecastGridData"]
        self.forecast_daily_url = incoming_json["properties"]["forecast"]
        self.forecast_hourly_url = incoming_json["properties"]["forecastHourly"]
        self.grid_id = incoming_json["properties"]["gridId"]
        self.time_zone = incoming_json["properties"]["timeZone"]
        self.radar_station = incoming_json["properties"]["radarStation"]

    def parse_daily_forecast(self):
        fc_data = forecast_api_manager.get_json_from_url(self.forecast_daily_url)
        daily_data_arr = []
        for _ in range(14):
            prop_data = fc_data["properties"]["periods"][_]
            daily_dict = {"temperature": prop_data["temperature"],
                "rain_prob": prop_data["probabilityOfPrecipitation"]["value"],
                "wind_speed": prop_data["windSpeed"], "wind_dir": prop_data["windDirection"],
                "short_forecast": prop_data["shortForecast"], "long_forecast": ["detailedForecast"]}
            daily_data_arr.append(daily_dict)

    def parse_gridpoints_forecast(self):
        fc_data = forecast_api_manager.get_json_from_url(self.forecast_daily_url)
        general_data_arr = []
        daily_arr = []
        pd = fc_data["properties"]
        for _ in range(7):
            daily_dict = {
                "maxTemperature": pd["maxTemperature"]["values"][_]["value"],
                "minTemperature": pd["minTemperature"]["values"][_]["value"],
                "weather": pd["weather"]["values"][_]["value"],
                }
            daily_arr.append(daily_dict)
        now_dict = {
            "apparentTemperature": pd["apparentTemperature"]["values"][0]["value"],
            "heatIndex": pd["heatIndex"]["values"][0]["value"],
            "windDirection": pd["windDirection"]["values"][0]["value"],
            "windSpeed": pd["windSpeed"]["values"][0]["value"],
            "windGust": pd["windGust"]["values"][0]["value"],
            "hazards": pd["hazards"]["values"],
            "visibility": pd["visibility"]["values"]["value"]
        }





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

    # Starts the api manager loop thread
    api_manager = APIManager(forecast_controller)
    api_manager_thread = threading.Thread(target=api_manager.run, daemon=True)
    api_manager_thread.start()

    forecast_controller.run()

