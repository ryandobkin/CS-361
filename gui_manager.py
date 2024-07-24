import eel
from inbound_message_manager import InboundMessageManager
from outbound_message_manager import OutboundMessageManager
from gui_api_manager import APIManager
import threading
import time
import json

# Globals
# NO LONGER ACCURATE WITH .SVGs
graphic_dimensions_list = {"sunny": (55, 55), "partly_cloudy": (71, 60), "haze": (74, 55),
 "fog": (71, 61), "windy": (63, 40), "cloudy": (71, 44), "thunderstorm_rain": (71, 65), "light_rain": (71, 65),
 "heavy_rain": (71, 65), "drizzle_rain": (71, 58), "hail_rain": (71, 66), "snow": (61, 66)}
query_queue = [0]
IS_TEST = True


class GuiMessageController:
    """
    Manages inbound/outbound messages, as well as value updates.
    """
    def __init__(self):
        self.ip = '127.0.0.3'
        self.port = 23458
        self.outbound_ip = '127.0.0.1'
        self.outbound_port = 23456
        self.socket_list = {"frontend_manager": ["127.0.0.1", 23456]}
        self.outbound_queue = []
        self.inbound_queue = []
        self.current_prediction_list = [""]
        self.api_request_list = []
        self.api_response_list = []
        self.current_search_term = ""
        self.start_time = 0
        self.is_test = IS_TEST

    def main(self):
        """
        Main object loop
        """
        eel.spawn(self.inbound_queue_processor)
        eel.spawn(self.autocomplete_update_loop)
        eel.sleep(1)

    def inbound_queue_processor(self):
        """
        Processes the inbound queue
        """
        while True:
            try:
                if self.is_test:
                    self.is_test = False
                    self.inbound_queue.append(json.load(open('gui_forecast_example.json')))
                if len(self.inbound_queue) > 0:
                    message = self.inbound_queue.pop(0)
                    print(f"Processing Incoming Message: {message}")
                    if message["service"] == "forecast":
                        self.update_forecast(message)
            except KeyboardInterrupt as e:
                print("Inbound Processing Error:", e)
            eel.sleep(.25)

    def autocomplete_update_loop(self):
        """
        Checks for autocomplete updates
        """
        last_update = 0
        while True:
            if eel.updateSearchInFocus()() is True:
                eel.setSearchDropdownOpacity("0.9")
                recent_search = eel.updateSearchAutocomplete()()
                if recent_search == "" and self.current_search_term != recent_search:
                    self.current_search_term = recent_search
                    search_autocomplete_update()
                if self.current_search_term != recent_search and recent_search != "":
                    last_update = time.time()
                    self.current_search_term = recent_search
                time_now = time.time()
                if (time_now - last_update) > 0.15 and last_update != 0:
                    last_update = 0
                    search_autocomplete_update(self.current_search_term)
            else:
                eel.setSearchDropdownOpacity("0")
            eel.sleep(0.1)

    def update_forecast_request(self):
        """
        Sends a request to the forecast service via the frontend manager to get updates location data.
        """
        while len(self.api_response_list) < 1:
            eel.sleep(.1)
        geocoding_coordinates = self.api_response_list.pop(0)
        if geocoding_coordinates["service"] != "geocoding":
            self.api_response_list.append(geocoding_coordinates)
            print("GUI MANAGER UPDATE FORECAST REQUEST - Wrong update message received")
        else:
            request_message = {"socket": self.socket_list["frontend_manager"],
                               "type": "request",
                               "service": "forecast",
                               "data": geocoding_coordinates["data"]}
            self.outbound_queue.append(request_message)

    def update_forecast(self, forecast_message):
        """
        Calls all relevant services to update GUI based on incoming update forcast JSON message
        """
        try:
            forecast = forecast_message["data"]
            daily_forecast = forecast["daily_forecast"]
            hourly_forecast = forecast["hourly_forecast"]
            widget_forecast = forecast["widget_forecast"]
            alert_forecast = forecast["alert_forecast"]
            self.update_daily_forecasts(daily_forecast)
            self.update_widget_forecasts(widget_forecast)
            self.update_alert_forecast(alert_forecast)
        except KeyboardInterrupt as e:
            print("UpdateForecast Error:", e)

    def update_daily_forecasts(self, daily_json):
        print(daily_json)
        try:
            day = 0
            for daily_fc_top in daily_json:
                # print("day", day, daily_fc_top)
                daily_fc = daily_json[daily_fc_top]
                update_daily_date(day, daily_fc["name"])
                condition_list = daily_fc["shortForecast"].split(' ')
                if len(condition_list) >= 2:
                    update_daily_weather_condition_text(day, f"{condition_list[0]} {condition_list[1]}")
                else:
                    update_daily_weather_condition_text(day, f"{condition_list[0]}")
                update_daily_weather_condition_graphic(day, condition_list)
                update_daily_hilo(day, daily_fc["maxTemperature"], daily_fc["minTemperature"])
                if daily_fc["rainProb"] is None:
                    daily_rain = 0
                else:
                    daily_rain = daily_fc["rainProb"]
                update_daily_rain_percent(day, daily_rain)
                update_daily_wind(day, daily_fc["windDirection"], daily_fc["windSpeed"])
                if day == 6:
                    break
                day += 1
            print("UPDATE COMPLETE")
        except KeyboardInterrupt as e:
            print("UpdateDailyForecasts Error:", e)

    def update_hourly_forecasts(self, hourly_json):
        pass

    def update_widget_forecasts(self, widget_forecast):
        pass

    def update_alert_forecast(self, alert_forecast):
        """
        Updates the alert widget with incoming information when called.
        Will probably have a microservice controller eventually, for now controlled by forecast_service.
        """
        print("active alerts: ", alert_forecast)
        af = alert_forecast
        if alert_forecast:
            time_eff, time_exp = self.to_12hr_offset_time(alert_forecast['effective'], alert_forecast['expires'])
            effective_times = f"Effective {time_eff} through {time_exp}"
            alert_body_full = f"{effective_times}\n{af['headline']}\n"
            update_alert(True, af["event"], alert_body_full, af["senderName"])

        else:
            pass
            # make alert invisible

    def to_12hr_offset_time(self, time1, time2):
        """
        Translates two given 12hr y-m-dTh:m:s-utc-# to mon day 12hr time am/pm utc-# offset (PST, EST)
        TODO: Convert times to current time zone, works for now though
        """
        month_dict = {"01": "January", "02": "February", "03": "March", "04": "April", "05": "May", "06": "June",
                  "07": "July", "08": "August", "09": "September", "10": "October", "11": "November", "12": "December"}
        offset_dict = {"00": "UTC-0", "-01": "UTC-1", "-02": "UTC-2", "-03": "UTC-3", "-04": "UTC-4", "-05": "ET", "-06": "CT",
                       "-07": "MT", "-08": "PT", "-09": "AKST", "-10": "HT"}
        return_arr = []
        for ct in [time1, time2]:
            ct = ct.split('T')
            currdate = ct[0].split('-')
            date_str = f"{month_dict[currdate[1]]} {currdate[2]}"
            currtime = ct[1].split(':')
            if int(currtime[0]) > 12:
                time_str = f"{int(currtime[0]) - 12}:{currtime[1]} PM"
            else:
                time_str = f"{int(currtime[0]) - 12}:{currtime[1]} AM"
            offset = currtime[3]
            time_zone_str = offset_dict[offset]
            return_arr.append(f"{date_str} {time_str} {time_zone_str}")
        return return_arr




def run():
    """
    Starts the web page and eel loop.
    """
    try:
        eel.init('web')
        eel.start('index.html', size=(1614, 937), block=True)
    except KeyboardInterrupt:
        exit(4)


# LOCATION WIDGET VV
@eel.expose
def update_location(new_location=None):
    """
    Updates location display banner.

    Parameters:
    -----------
    new_location : str
        The new location to display in the location banner.
    """
    eel.updateLocationDisplay(new_location)


# SEARCH WIDGET QUERY
@eel.expose
def search_query(query='Default'):
    """
    Called when a search is entered via the search bar.

    Parameters:
    -----------
    query : str
        The input query.
    """
    print(f"Incoming search query: {query}")
    pred_list = gui_message_controller.current_prediction_list
    if pred_list[0] != "":
        top_query_pred = pred_list[0]
        query_out = {"service": "geocoding",
                     "data": top_query_pred}
        update_location(top_query_pred)
        gui_message_controller.api_request_list.append(query_out)
        gui_message_controller.update_forecast_request()
        return True
    else:
        return False


# SEARCH WIDGET AUTOCOMPLETE
@eel.expose
def search_autocomplete_update(partial_query=""):
    """
    Called every time the search bar is updated with typing

    Parameters:
    -----------
    partial_query : str
        The partially completed query to get autocomplete predictions
    """
    if partial_query == "":
        autocomplete_query = {"service": "autocomplete",
                              "data": [True],
                              "origin_data": ""}
        gui_message_controller.api_response_list.append(autocomplete_query)
    else:
        gui_message_controller.start_time = time.time()
        print(f"Updating search autocomplete: {partial_query}")
        autocomplete_query = {"service": "autocomplete",
                              "data": partial_query}
        gui_message_controller.api_request_list.append(autocomplete_query)
    search_display_autocomplete()


# SEARCH WIDGET DISPLAY AUTOCOMPLETE OPTIONS
@eel.expose
def search_display_autocomplete():
    """
    Updates the dropdown search menu with the autocomplete predictions.
    """
    placeholder_text = ""
    while True:
        if len(gui_message_controller.api_response_list) > 0:
            break
        eel.sleep(0.15)
    response = gui_message_controller.api_response_list.pop(0)
    if response["data"][0] is False:
        response["data"][0] = ""
        placeholder_text = "No Data Available"
    elif response["data"][0] is True:
        response["data"][0] = ""
    gui_message_controller.current_prediction_list = response["data"]
    display_list = ["", "", "", "", ""]
    list_counter = 0
    for _ in range(len(gui_message_controller.current_prediction_list)):
        display_list[_] = gui_message_controller.current_prediction_list[_]
        list_counter += 1
        if list_counter == 5:
            break
    if response["origin_data"] == gui_message_controller.current_search_term:
        if placeholder_text != "No Data Available":
            eel.updateSearchAutocompleteDropdownFields(display_list)
        else:
            eel.updateSearchAutocompleteDropdownFields([placeholder_text, "", "", "", ""])
        end_time = time.time()
        print(f"Total time: {end_time - gui_message_controller.start_time}")
    else:
        print("Discarding autocomplete set")


# DAILY WIDGET | RAIN
@eel.expose
def update_daily_rain_percent(day=0, new_percent=0):
    """
    Updates daily forecast rain value

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    new_percent : int
        The precipitation % forecasted for a given day.
    """
    daily_widget = 'rain_value_daily_' + str(day)
    value = str(new_percent) + '%'
    #print(f"RAIN | Value 1: {daily_widget} | Value 2: {value}")
    eel.updateDailyRainPercent(daily_widget, value)


# DAILY WIDGET | WIND
@eel.expose
def update_daily_wind(day=0, direction='N', speed=0):
    """
    Updates daily forecast wind value

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    direction: str
        The direction of the wind value. Should be a combination of N S E W, such as WSW, NE, etc.
    speed: int
        The speed value of the wind. Should be an int.
    """
    daily_widget_name = 'wind_value_daily_' + str(day)
    new_wind_value = f"{direction} {speed}"
    #print(f"WIND | Value 1: {daily_widget_name} | Value 2: {new_wind_value}")
    eel.updateDailyWind(daily_widget_name, new_wind_value)


# DAILY WIDGET | HILO
@eel.expose
def update_daily_hilo(day=0, hi=0, lo=0):
    """
    Updates the Hi and Lo daily forecast values

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    Hi : int
        The new Hi value to be put into the display.
    Lo : int
        The new Lo value to be put into the display.
    """
    hilo = f"{hi}{chr(176)}/{lo}{chr(176)}"
    daily_widget_name = 'hilo_daily_' + str(day)
    #print(f"HILO | Value 1: {daily_widget_name} | Value 2: {hilo}")
    eel.updateDailyHiLo(daily_widget_name, hilo)


# DAILY WIDGET | CONDITION TEXT
@eel.expose
def update_daily_weather_condition_text(day=0, weather_condition='Default'):
    """
    Updates daily forecast weather condition text

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    weather_condition : str
        The new weather condition.
    """
    daily_widget_name = 'condition_text_daily_' + str(day)
    #print(f"TEXT | Value 1: {daily_widget_name} | Value 2: {weather_condition}")
    eel.updateDailyWeatherConditionText(daily_widget_name, weather_condition)


# DAILY WIDGET | CONDITION GRAPHIC
@eel.expose
def update_daily_weather_condition_graphic(day=0, graphic='sunny'):
    """
    Updates the daily forecast weather condition graphic

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    graphic : str
        The name of the graphic to be displayed
    """
    if type(graphic) != str:
        if len(graphic) == 2:
            if graphic[1] == 'And':
                graphic_str = f"{graphic[0]}"
            else:
                graphic_str = f"{graphic[0]} {graphic[1]}"
        elif len(graphic) > 2:
            if graphic[1] == 'And':
                graphic_str = f"{graphic[0]} {graphic[2]}"
            else:
                graphic_str = f"{graphic[0]} {graphic[1]}"
        else:
            graphic_str = f"{graphic[0]}"
    else:
        graphic_str = graphic
    print(f"GRAPHIC ORIGINAL - {graphic} || GRAPHIC UPDATED - {graphic_str}", )
    #print("GRAPHIC_STR: ", graphic_str)
    short_forecast_to_graphic_dict = {
        "Sunny": 'sunny', "Partly Sunny": 'partly_cloudy', "Mostly Sunny": 'sunny',
        "Cloudy": 'cloudy', "Partly Cloudy": 'partly_cloudy', "Mostly Cloudy": 'cloudy',
        "Patchy Fog": 'fog', "Scattered Showers": 'light_rain', "Showers": 'light_rain',
        "Isolated Showers": 'light_rain', "Showers Thunderstorms": 'thunderstorm_rain', "Chance Showers": 'light_rain'}
    graphic_name = short_forecast_to_graphic_dict[graphic_str]
    daily_widget_name = 'condition_graphic_daily_' + str(day)
    graphic_directory = './Images/' + graphic_name + '_graphic.svg'
    width, height = get_graphic_dimensions(graphic_name)
    offsetx, offsety = get_graphic_offset(graphic_name, 100, 80)
    print(f"GRAPHIC | V1: {daily_widget_name} | V2: {graphic_directory} | V3 {width} | V4: {height} | V5: {offsetx} | V6: {offsety}")
    eel.updateDailyWeatherConditionGraphic(daily_widget_name, graphic_directory, width, height, offsetx, offsety)


# DAILY WIDGET | DATE
@eel.expose
def update_daily_date(day=0, date='Today'):
    """
    Updates daily forecast date display

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    date : str
        The string of the date to be displayed
    """
    daily_widget_name = 'date_daily_' + str(day)
    eel.updateDailyDate(daily_widget_name, date)


# HOURLY WIDGET | TEXT
@eel.expose
def update_hourly_temp(hour, temp):
    """
    Updates hourly temps

    Parameters:
    -----------
    hour : int
        The hour widget to be updated.
    temp : int
        The new temperature value
    """
    hourly_widget_name = 'temp_hourly_' + str(hour)
    temp_str = str(temp) + chr(176)
    eel.updateHourlyWidgetTemp(hourly_widget_name, temp_str)


# HOURLY WIDGET | TIME
@eel.expose
def update_hourly_time(hour, time):
    """
    Updates hourly times

    Parameters:
    -----------
    hour : int
        The hour widget to be updates
    time : str
        The new time to be displayed.
    """
    hourly_widget_name = 'time_hourly_' + str(hour)
    eel.updateHourlyWidgetTime(hourly_widget_name, time)


# HOURLY WIDGET | GRAPHIC
@eel.expose
def update_hourly_graphic(hour=0, graphic="hail_rain"):
    """
    Updates hourly widget graphics.

    Parameters:
    -----------
    hour : int
        The hour widget to be updates
    graphic : str
        The name of the graphic
    """
    hourly_widget_name = 'condition_graphic_hourly_' + str(hour)
    graphic_directory = './Images/' + graphic + '_graphic.png'
    width, height = get_graphic_dimensions(graphic)
    offsetx, offsety = get_graphic_offset(graphic, 72, 72)
    print(f"OFFSETX {offsetx} || OFFSETY {offsety}")
    eel.updateHourlyWidgetGraphic(hourly_widget_name, graphic_directory, width, height, offsetx, offsety)


# ALERT WIDGET
@eel.expose
def update_alert(visible=True, header="Severe Weather Alert", body="Severe Weather Alert Test", source="National Weather Service"):
    """
    Updates Alert widget with new values

    Parameters:
    -----------
    visible : bool
        Should the widget be shown or not
    header : str
        The header string text. ~20 characters. Defaults to 'Severe Weather Alert'
    body : str
        The body string text. maybe 80 characters. Defaults to 'Severe Weather Alert'
    source : str
        The source of the alert. Defaults to 'National Weather Service'
    """
    # If setting invisible, shouldn't need to run rest of text update
    if visible is False:
        eel.updateAlertWidgetVisibility(0)
    else:
        eel.updateAlertWidgetVisibility(1)
        eel.updateAlertWidget(header, body, source)


# SUN WIDGET
@eel.expose
def update_sun(sunrise=6, sunset=18, dawn=5, dusk=19):
    """
    Updates the Sunrise & Sunset widget.
    All parameter times should be given in 24-hour clock format.

    Parameters:
    -----------
    sunrise : int
        The time of sunrise
    sunset : int
        The time of sunset
    dawn : int
        The time of dawn
    dusk : int
        The time of dusk
    """
    sunrise_time, sunset_time, dawn_time, dusk_time, i = 0
    out_list = [sunrise_time, sunset_time, dawn_time, dusk_time]
    inp_list = [sunrise, sunset, dawn, dusk]
    for _ in inp_list:
        if _ % 12 > 0:
            out_list[i] = f"{_} PM"
        else:
            out_list[i] = f"{_} AM"
        i+=1
    eel.updateSunWidgetValues(sunrise, sunset, dawn, dusk)


# UV WIDGET
@eel.expose
def update_uv(uv_value=0):
    """
    Updates the UV Index Widget values.

    Parameters:
    -----------
    uv_value : int
        The value to update the uv index to
    """
    if uv_value <= 2:
        uv_status = "Low"
    elif uv_value <= 5:
        uv_status = "Moderate"
    elif uv_value <= 7:
        uv_status = "High"
    elif uv_value <= 10:
        uv_status = "Very High"
    elif uv_value > 10:
        uv_status = "Extreme"
    else:
        uv_status = "Undefined"
    eel.updateUVWidgetValues(uv_value, uv_status)


# WIND WIDGET
@eel.expose
def update_wind(speed=0, direction='N'):
    """
    Updates wind widget values

    Parameters:
    -----------
    speed : int
        The updated speed of the wind
    direction : str
        The direction of the wind
    """
    # https://www.weather.gov/mfl/beaufort
    # Check what API gives
    status = 'Calm'
    eel.updateWindWidgetValues(speed, status)


# HUMIDITY WIDGET
@eel.expose
def update_humidity(humidity=0, dew=68):
    """
    Updates the humidity widget's values

    Parameters:
    -----------
    humidity : int
        The new value to update the humidity display to
    dew : int
        The dew point
    """
    # Eventually add way to update graphics - shouldn't be that hard ngl
    eel.updateHumidityWidgetValues(humidity, dew)


# PRESSURE WIDGET
@eel.expose
def update_pressure(pressure=30):
    """
    Updates pressure widget values.

    Parameters:
    -----------
    pressure : int
        The new pressure
    """
    eel.updatePressureWidgetValues(pressure)


# NOW WIDGET
@eel.expose
def update_now(temp=80, hi=90, lo=70, condition="Partly Cloudy", graphic="partly_cloudy", feels_like="80"):
    """
    Updates the Now widget's values.

    Parameters:
    -----------
    temp : int
    hi : int
    lo : int
    condition_text : str
    graphic : str
    feels_like : int
    """
    new_temp = f"{temp}{chr(176)}"
    hilo = f"High: {hi} Low: {lo}"
    new_feels_like = f"Feels like {feels_like}{chr(176)}"
    graphic_directory = './Images/' + graphic + '_graphic.png'
    width, height = get_graphic_dimensions(graphic)
    offsetx, offsety = get_graphic_offset(graphic, 120, 95)
    eel.updateNowWidget(new_temp, hilo, condition, new_feels_like, graphic_directory, width, height, offsetx, offsety)



# HELPER FUNCTIONS
@eel.expose
def print_in_python(input="someFunction"):
    print(f"Successfully received: {input}")


def get_graphic_dimensions(graphic_name="sunny"):
    """
    Returns the graphic dimensions passed.

    Parameters:
    -----------
    graphic_name : str
        The name of the graphic to be fetched.

    Returns:
    --------
    graphic_dim[0], graphic_dim[1]
        The width and height of the graphic.
    """
    graphic_dim = graphic_dimensions_list[graphic_name]
    return graphic_dim[0], graphic_dim[1]


def get_graphic_offset(graphic_name="sunny", width=72, height=72):
    """
    Returns the graphic dimensions passed.

    Parameters:
    -----------
    graphic_name : str
        The name of the graphic to be fetched.

    Returns:
    --------
    pxoffsetx : str
        The x offset needed for the given graphic in the form of '#px'.
    pxoffsety : str
        The y offset.
    width : int
        The total container width
    height : int
        The total container height
    """
    innerx, innery = graphic_dimensions_list[graphic_name]
    offsetx = (width - innerx) / 2
    offsety = (height - innery) / 2
    pxoffsetx = str(offsetx) + 'px'
    pxoffsety = str(offsety) + 'px'
    return pxoffsetx, pxoffsety


def test():
    eel.sleep(1)
    print("START OF UNIT TEST")
    update_hourly_graphic()
    update_alert(False)
    eel.sleep(15)
    update_location("newLocation")
    eel.sleep(1)
    update_daily_rain_percent(0, 33)
    eel.sleep(1)
    update_daily_wind(0, 'NW', 14)
    eel.sleep(1)
    update_daily_hilo(0, 88, 76)
    eel.sleep(1)
    update_daily_weather_condition_text(0, "sunny")
    eel.sleep(1)
    update_daily_weather_condition_graphic(0, "partly_cloudy")
    eel.sleep(1)
    update_daily_date(0, "Tomorrow")
    eel.sleep(1)
    print("DONE WITH UNIT TEST")


if __name__ == '__main__':
    gui_message_controller = GuiMessageController()

    # Starts the incoming message loop thread
    inbound_message_manager = InboundMessageManager(gui_message_controller)
    inbound_message_manager_thread = threading.Thread(target=inbound_message_manager.run, daemon=True)
    inbound_message_manager_thread.start()

    # Starts the outgoing message loop thread
    outbound_message_manager = OutboundMessageManager(gui_message_controller)
    outbound_message_manager_thread = threading.Thread(target=outbound_message_manager.run, daemon=True)
    outbound_message_manager_thread.start()

    # Starts the api manager loop thread
    api_manager = APIManager(gui_message_controller)
    api_manager_thread = threading.Thread(target=api_manager.run, daemon=True)
    api_manager_thread.start()

    # Starts the incoming message loop thread
    eel.spawn(gui_message_controller.main)

    run()

