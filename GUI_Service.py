import eel
import time

# Globals
graphic_dimensions_list = {"sunny": (55, 55), "partly_cloudy": (71, 60), "haze": (74, 55),
 "fog": (71, 61), "windy": (63, 40), "cloudy": (71, 44), "thunderstorm_rain": (71, 65), "light_rain": (71, 65),
 "heavy_rain": (71, 65), "drizzle_rain": (71, 58), "hail_rain": (71, 66), "snow": (61, 66)}
query_queue = [0]


def run():
    """
    Starts the web page and eel loop.
    """
    eel.init('web')
    eel.start('index.html', size=(1614, 937), block=True)


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


# SEARCH WIDGET VV
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
    query_queue.append(query)


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
    new_wind_value = f"{direction} {speed} mph"
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
def update_daily_weather_condition_graphic(day=0, graphic='haze'):
    """
    Updates the daily forecast weather condition graphic

    Parameters:
    -----------
    day : int
        The given day (module) that should be edited. Values should be 0-6.
    graphic : str
        The name of the graphic to be displayed
    """
    daily_widget_name = 'condition_graphic_daily_' + str(day)
    graphic_directory = './Images/' + graphic + '_graphic.png'
    width, height = get_graphic_dimensions(graphic)
    offsetx, offsety = get_graphic_offset(graphic, 100, 80)
    #print(f"GRAPHIC | V1: {daily_widget_name} | V2: {graphic_directory} | V3 {width} | V4: {height} | V5: {offsetx} | V6: {offsety}")
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


def await_request():
    """
    Eel thread that maintains the controller loop.
    """
    # Check for query
    if len(query_queue) != 1:
        # send to queue
        # return queue update
        update_location("New Location")


if __name__ == '__main__':
    # Start GUI thread
    #eel.spawn(test)
    # eel.spawn(await_request)
    run()

