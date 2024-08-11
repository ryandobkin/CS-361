import eel
import inbound_message_manager
import outbound_message_manager
import threading
import time

# Globals
# NO LONGER ACCURATE WITH .SVGs
graphic_dimensions_list = {"sunny": (55, 55), "partly_cloudy": (71, 60), "haze": (74, 55),
 "fog": (71, 61), "windy": (63, 40), "cloudy": (71, 44), "thunderstorm_rain": (71, 65), "light_rain": (71, 65),
 "heavy_rain": (71, 65), "drizzle_rain": (71, 58), "hail_rain": (71, 66), "snow": (61, 66)}
query_queue = [0]
IS_TEST = False


class GuiMessageController:
    """
    Manages inbound/outbound messages, as well as value updates.
    """
    def __init__(self):
        self.socket_port_in = '5558'
        self.socket_port_forecast_service = '5556'
        self.socket_port_api_interface = '5559'
        self.socket_port_hourly_forecast_microservice = '5560'
        self.socket_port_location_determination_microservice = '5561'
        self.socket_port_detailed_weather_microservice = '5562'
        self.inbound_queue = []
        self.current_prediction_list = [""]
        self.api_request_list = []
        self.api_response_list = []
        self.current_search_term = ""
        self.start_time = 0
        self.is_test = IS_TEST
        self.current_day_selection = 0
        self.timer_start = 0
        self.inbound_mm = inbound_message_manager

    def main(self):
        """
        Main object loop
        """
        eel.spawn(self.inbound_queue_processor)
        eel.spawn(self.autocomplete_update_loop)
        outbound_message_manager.send_message({"service": "location", "type": "coords"}, '5563')

        eel.sleep(.5)

    def inbound_queue_processor(self):
        """
        Processes the inbound queue
        """
        while True:
            try:
                if len(self.inbound_queue) > 0:
                    message = self.inbound_queue.pop(0)
                    print(f"Processing Incoming Message: {message}")
                    if message["service"] == "forecast":
                        self.update_forecast(message)
                    if message["service"] == 'locate_me':
                        self.update_forecast_request(message)
            except KeyboardInterrupt as e:
                print("Inbound Processing Error:", e)
            eel.sleep(.1)

    def autocomplete_update_loop(self):
        """
        Checks for autocomplete updates
        """
        last_update = 0
        while True:
            if eel.updateSearchInFocus()() is True:
                eel.setSearchDropdownOpacity("0.95")
                recent_search = eel.updateSearchAutocomplete()()
                if recent_search != 'Search for a City':
                    if recent_search == "" and self.current_search_term != recent_search:
                        self.current_search_term = recent_search
                        search_autocomplete_update()
                    if self.current_search_term != recent_search and recent_search != "":
                        last_update = time.time()
                        self.current_search_term = recent_search
                    time_now = time.time()
                    if (time_now - last_update) > 0.1 and last_update != 0:
                        last_update = 0
                        search_autocomplete_update(self.current_search_term)
            else:
                eel.setSearchDropdownOpacity("0")
                #search_autocomplete_update(None)
            eel.sleep(0.1)

    def update_forecast_request(self, request):
        """
        Sends a request to the forecast service via the frontend manager to get updates location data.
        """
        print(request)
        request_message = {"service": "forecast", "data": request["response"]}
        ack = outbound_message_manager.send_message(request_message, self.socket_port_forecast_service)
        self.timer_start = time.time()
        print("GUI ACK", ack)

    def update_forecast(self, forecast_message):
        """
        Calls all relevant services to update GUI based on incoming update forcast JSON message
        """
        try:
            print(f"Forecast req+res time: {time.time() - self.timer_start}")
            update_location(forecast_message["data"]["location"])
            forecast = forecast_message["data"]
            daily_forecast = forecast["daily_forecast"]
            hourly_forecast = forecast["hourly_forecast"]
            widget_forecast = forecast["widget_forecast"]
            alert_forecast = forecast["alert_forecast"]
            if "location" in forecast_message:
                update_location(forecast_message["location"])
            self.update_daily_forecasts(daily_forecast)
            self.update_widget_forecasts(widget_forecast)
            self.update_alert_forecast(alert_forecast)
            print(f"Forecast update time: {time.time() - self.timer_start}")
        except KeyboardInterrupt as e:
            print("UpdateForecast Error:", e)

    def update_daily_forecasts(self, daily_json):
        try:
            day = 0
            for daily_fc_top in daily_json:
                # print("day", day, daily_fc_top)
                daily_fc = daily_json[daily_fc_top]
                update_daily_date(day, daily_fc["name"])
                update_daily_weather_condition_text(day, daily_fc["shortForecast"])
                update_daily_weather_condition_graphic(day, daily_fc["shortForecast"], 'day')
                update_daily_hilo(day, daily_fc["maxTemperature"], daily_fc["minTemperature"])
                if day == 6:
                    break
                day += 1
        except KeyboardInterrupt as e:
            print("UpdateDailyForecasts Error:", e)

    def update_hourly_forecasts(self, hourly_json):
        pass

    def update_widget_forecasts(self, widget_forecast):
        wf = widget_forecast["now"]
        # Only updating NOW forecast for time being
        update_daily_weather_condition_graphic(0, wf["shortForecast"], 'now')
        update_now(wf['temperature'], wf['maxTemperature'], wf['minTemperature'], wf['shortForecast'], wf['apparentTemperature'])

        # for the cc widgets
        cc_data = outbound_message_manager.send_message(widget_forecast, self.socket_port_detailed_weather_microservice)

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
            # update_alert(True, af["event"], alert_body_full, af["senderName"])
            updated_description = af["description"]
            updated_description = updated_description.replace('\n\n', '$')
            updated_description = updated_description.replace('\n', ' ')
            updated_description = updated_description.replace('...', ':  ')
            updated_description = updated_description.replace('$', '\n\n')
            updated_instruction = f"INSTRUCTIONS: {af['instruction']}"
            update_alert(af["event"], af["headline"], updated_description, updated_instruction, af["senderName"])
        else:
            update_alert("No Alerts")

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
        eel.start('index.html', size=(1294, 756), block=True)
    except:
        exit(4)


# UPDATES CURRENT DAY SELECTED
@eel.expose
def update_current_day(day):
    """
    Updates the current day selection as self.current_day_selection.
    """
    gui_message_controller.current_day_selection = day


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
    eel.updateSearchLocationDisplay(new_location)


# SEARCH WIDGET QUERY
@eel.expose
def search_query(query='Default', type="enter"):
    """
    Called when a search is entered via the search bar.

    Parameters:
    -----------
    query : str
        The input query.
    type : str
        The input type. Either "enter", or "click".
    """
    gmc = gui_message_controller
    print(f"Incoming search query: {query} | type {type}")
    pred_list = gui_message_controller.current_prediction_list
    if type == "enter":
        if pred_list[0] != "":
            top_query_pred = pred_list[0]
            gui_message_controller.current_search_term = top_query_pred
            query_out = {"service": "geocoding",
                         "data": top_query_pred}
            update_location(top_query_pred)
            gmc.update_forecast_request(outbound_message_manager.send_message(query_out, gmc.socket_port_api_interface))
            return True
        else:
            return False
    elif type == "click":
        last_update_hl = query
        gui_message_controller.current_search_term = last_update_hl
        query_out = {"service": "geocoding",
                     "data": last_update_hl}
        update_location(last_update_hl)
        gmc.update_forecast_request(outbound_message_manager.send_message(query_out, gmc.socket_port_api_interface))
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
        search_display_autocomplete(outbound_message_manager.
                                    send_message(autocomplete_query, gui_message_controller.socket_port_api_interface))
    else:
        gui_message_controller.start_time = time.time()
        print(f"Updating search autocomplete: {partial_query}")
        autocomplete_query = {"service": "autocomplete",
                              "data": partial_query,
                              "origin_data": partial_query}
        search_display_autocomplete(outbound_message_manager.
                                    send_message(autocomplete_query, gui_message_controller.socket_port_api_interface))


# SEARCH WIDGET DISPLAY AUTOCOMPLETE OPTIONS
@eel.expose
def search_display_autocomplete(response_inp):
    """
    Updates the dropdown search menu with the autocomplete predictions.
    """
    gmc = gui_message_controller
    placeholder_text = ""
    gmc.current_prediction_list = response_inp["response"]
    if gmc.current_prediction_list[0] is False:
        placeholder_text = "No Data Available"
        gmc.current_prediction_list[0] = ""
    display_list = ["", "", "", "", ""]
    list_counter = 0
    for _ in range(len(gmc.current_prediction_list)):
        display_list[_] = gmc.current_prediction_list[_]
        list_counter += 1
        if list_counter == 5:
            break
    if response_inp["request"]["origin_data"] == gmc.current_search_term:
        if placeholder_text != "No Data Available":
            eel.updateSearchAutocompleteDropdownFields(display_list)
        else:
            eel.updateSearchAutocompleteDropdownFields([placeholder_text, "", "", "", ""])
        print(f"Autocomplete time: {time.time() - gui_message_controller.start_time}")
    else:
        print("Discarding autocomplete set")


# UPDATES LAST HIGHLIGHTED TRACKER
@eel.expose
def last_highlight_update(element):
    """
    Updates the self.last_highlighted element.

    Parameters:
    -----------
    element : int
        An integer 1 - 5 representing the last highlighted autocomplete query from top to bottom.
    """
    gui_message_controller.last_highlighted = element


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
    hi = f"{hi}{chr(176)}"
    lo = f"{lo}{chr(176)}"
    daily_hi_widget_name = 'hi_daily_' + str(day)
    daily_lo_widget_name = 'lo_daily_' + str(day)
    eel.updateDailyHi(daily_hi_widget_name, hi)
    eel.updateDailyLo(daily_lo_widget_name, lo)


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
    #weather_condition = correct_condition_terms(weather_condition)
    daily_widget_name = 'condition_text_daily_' + str(day)
    #print(f"TEXT | Value 1: {daily_widget_name} | Value 2: {weather_condition}")
    eel.updateDailyWeatherConditionText(daily_widget_name, weather_condition)


# DAILY WIDGET | CONDITION GRAPHIC
@eel.expose
def update_daily_weather_condition_graphic(day=0, graphic_str='sunny', type='day'):
    """
    Updates the daily forecast weather condition graphic

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    graphic : str
        The name of the graphic to be displayed
    type : str
        Determines if the function returns on calls on. Either 'day', or 'now'
    """
    # graphic_str = correct_condition_terms(graphic)
    #print("GRAPHIC_STR: ", graphic_str)
    short_forecast_to_graphic_dict = {
        "Sunny": 'sunny', "Partly Sunny": 'partly_cloudy', "Mostly Sunny": 'sunny',
        "Cloudy": 'cloudy', "Partly Cloudy": 'partly_cloudy', "Mostly Cloudy": 'cloudy',
        "Patchy Fog": 'fog', "Scattered Showers": 'light_rain', "Showers": 'light_rain',
        "Isolated Showers": 'light_rain', "Showers and Thunderstorms": 'thunderstorm_rain',
        "Showers Thunderstorms": 'thunderstorm_rain', "Chance Showers": 'light_rain',
        "Clear": 'sunny', "Mostly Clear": 'sunny', "Smoke then Mostly Clear": 'haze', "Haze": 'haze',
        "Areas Of Smoke": 'haze', "Areas of Smoke": 'haze',
        "Haze then Mostly Clear": 'haze', "Areas of Fog": 'fog', "Areas Of Fog": 'fog',
        "Chance Showers And Thunderstorms": 'thunderstorm_rain',
        "Chance Rain Showers": 'heavy_rain', "Patchy Fog then Mostly Sunny": 'haze',
        "Mostly Sunny then Isolated Showers And Thunderstorms": 'partly_cloudy',
        "Slight Chance Showers And Thunderstorms": 'thunderstorm_rain',
        "Patchy Fog then Partly Sunny": 'fog', "Slight Chance Light Rain": 'light_rain',
        "Slight Chance Showers And Thunderstorms then Chance Showers And Thunderstorms": 'thunderstorm_rain',
        "Slight Chance Showers And Thunderstorms then Sunny": 'thunderstorm_rain',
        "Showers And Thunderstorms Likely": 'thunderstorm_rain',
        "Partly Sunny then Chance Showers And Thunderstorms": 'thunderstorm_rain',
        "Slight Chance Rain Showers then Chance Showers And Thunderstorms": 'thunderstorm_rain',

        "sunny_snow": "snow", "part_sunny_snow": "snow", "snow": "snow",
        "sunny_rain": "drizzle_rain", "part_sunny_rain": "light_rain", "rain": "heavy_rain",
        "sunny_snow_rain": "drizzle_rain", "part_sunny_snow_rain": "hail_rain", "snow_rain": "hail_rain",
        "sunny_thunderstorm": "light_rain", "part_sunny_thunderstorm": "thunderstorm_rain", "thunderstorms": "thunderstorm_rain",
        "sunny_hail": "hail_rain", "part_hail": "hail_rain", "hail": "hail_rain",
        "sunny_haze": "haze", "part_sunny_haze": "haze", "haze": "haze",
        "sunny_fog": "fog", "part_sunny_fog": "fog", "fog": "fog"
    }
    #url = f'https://openweathermap.org/img/wn/{graphic_id}@2x.png'
    #print("URL", day, url)
    #response = requests.get(url)
    #img = Image.open(BytesIO(response.content))

    print(graphic_str)
    if graphic_str in short_forecast_to_graphic_dict:
        graphic_name = short_forecast_to_graphic_dict[graphic_str]
    else:
        graphic_name = 'sunny'
    graphic_directory = './Images/' + graphic_name + '_graphic.svg'
    width, height = get_graphic_dimensions(graphic_name)
    offsetx, offsety = get_graphic_offset(graphic_name, 100, 80)
    #print(f"GRAPHIC | V1: {daily_widget_name} | V2: {graphic_directory} | V3 {width} | V4: {height} | V5: {offsetx} | V6: {offsety}")
    if type == 'day':
        daily_widget_name = 'condition_graphic_daily_' + str(day)
    elif type == 'now':
        daily_widget_name = 'condition_graphic_now'
    #else:
        #daily_widget_name = 'condition_graphic_now'
    #eel.updateDailyWeatherConditionGraphic(daily_widget_name, url, 80, 80, 15, 15)
    print("GRAPHIC DAILY UPDATE", daily_widget_name, graphic_directory)
    eel.updateDailyWeatherConditionGraphic(daily_widget_name, graphic_directory, width, height, offsetx, offsety)


def correct_condition_terms(graphic):
    """
    Currently deprecated. Working on generating forecast myself so I wont have to rely on shortForecast.
    """
    graphic_str = ""
    if type(graphic) != str:
        for _ in graphic:
            graphic_str += f"{str(_)} "
    graphic_str = graphic_str[:-1]
    return graphic_str


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
def update_alert(event="", headline="", description="", instruction="", source=""):
    """
    Updates Alert widget with new values

    Parameters:
    -----------
    event : str
        The header string text. ~20 characters. Defaults to 'Severe Weather Alert'
    headline : str
        The body string text. maybe 80 characters. Defaults to 'Severe Weather Alert'
    description : str
        The source of the alert. Defaults to 'National Weather Service'
    instruction : str
        The instructions given by the NWS alert.
    source : str
        The source of the alert - local weather agency

    """
    eel.updateAlertWidget(event, headline, description, instruction, source)


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
def update_now(temp=80, hi=90, lo=70, condition="Partly Cloudy", feels_like="80"):
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
    hilo = f"High: {hi} • Low: {lo}"
    new_feels_like = f"Feels like {feels_like}{chr(176)} • "
    eel.updateNowWidget(new_temp, hilo, condition, new_feels_like)



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


def start_program():
    global gui_message_controller
    gui_message_controller = GuiMessageController()

    # Starts the incoming message loop thread
    eel.spawn(gui_message_controller.main)

    inbound_message_manager = gui_message_controller.inbound_mm.InboundMessageManager(gui_message_controller)
    inbound_message_manager_thread = threading.Thread(target=inbound_message_manager.receive_message, daemon=True)
    inbound_message_manager_thread.start()

    run()


if __name__ == '__main__':
    start_program()
    #gui_message_controller = GuiMessageController()

    #inbound_message_manager = gui_message_controller.inbound_mm.InboundMessageManager(gui_message_controller)
    #inbound_message_manager_thread = threading.Thread(target=inbound_message_manager.receive_message, daemon=True)
    #inbound_message_manager_thread.start()
    #eel.spawn(receive_message)

    # Starts the incoming message loop thread
    #eel.spawn(gui_message_controller.main)

    #eel_thread = threading.Thread(target=run, daemon=True)
    #eel_thread.start()
    #run()
