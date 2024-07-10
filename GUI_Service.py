import eel
import time

# Globals


class GUI:
    """
    GUI Object
    """
    def __init__(self, manager=None):
        self.manager = manager
        eel.init('web')
        self.graphic_dimensions_list = {"sunny": (55, 55), "partly_cloudy": (71, 60), "haze": (74, 55),
         "fog": (71, 61), "windy": (63, 40), "cloudy": (71, 44), "thunderstorm_rain": (71, 65), "light_rain": (71, 65),
         "heavy_rain": (71, 65), "drizzle_rain": (71, 58), "hail_rain": (71, 66), "snow": (61, 66)}

    def run(self):
        eel.start('index.html', size=(1614, 937), block=False)

    @eel.expose
    def update_location(self, new_location=None):
        """
        Updates location display banner.

        Parameters:
        -----------
        new_location : str
            The new location to display in the location banner.
        """
        eel.updateLocationDisplay(new_location)

    @eel.expose
    def update_daily_rain_percent(self, day=0, new_percent=0):
        """
        Updates daily forecast rain value

        Parameters:
        -----------
        day : int
            The given day (module) that should be edited. Values should be 0-6.
        new_percent : int
            The precipitation % forecasted for a given day.
        """
        daily_widget = 'daily_rain_0' + str(day)
        value = str(new_percent) + '%'
        eel.updateDailyRainPercent(daily_widget, value)

    @eel.expose
    def update_daily_wind(self, day=0, direction='N', speed=0):
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
        daily_widget_name = 'daily_wind_' + str(day)
        new_wind_value = f"{direction} {speed} mph"
        print(f"1: {daily_widget_name} || 2: {new_wind_value}")
        eel.updateDailyWind(daily_widget_name, new_wind_value)

    @eel.expose
    def update_daily_hilo(self, day=0, hi=0, lo=0):
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
        daily_widget_name = 'weather_hi_lo_daily_' + str(day)
        eel.updateDailyHiLo(daily_widget_name, hilo)

    @eel.expose
    def update_daily_weather_condition_text(self, day=0, weather_condition='Default'):
        """
        Updates daily forecast weather condition text

        Parameters:
        -----------
        day : int
            The given day (module) that should be edited. Values should be 0-6.
        weather_condition : str
            The new weather condition.
        """
        daily_widget_name = 'weather_condition_text_daily_' + str(day)
        eel.updateDailyWeatherConditionText(daily_widget_name, weather_condition)

    @eel.expose
    def update_daily_weather_condition_graphic(self, day=0, graphic='haze'):
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
        width, height = self.get_graphic_dimensions(graphic)
        offsetx, offsety = self.get_graphic_offset(graphic)
        eel.updateDailyWeatherConditionGraphic(daily_widget_name, graphic_directory, width, height, offsetx, offsety)

    # ^^ ---------  Public / Exposed Functions   --------- ^^ #
    # VV --------- Local / Private / Not Exposed --------- VV #

    def get_graphic_dimensions(self, graphic_name="sunny"):
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
        graphic_dim = self.graphic_dimensions_list[graphic_name]
        return graphic_dim[0], graphic_dim[1]

    def get_graphic_offset(self, graphic_name="sunny"):
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
        """
        innerx, innery = self.graphic_dimensions_list[graphic_name]
        offsetx = (100 - innerx) / 2
        offsety = (80 - innery) / 2
        pxoffsetx = str(offsetx) + 'px'
        pxoffsety = str(offsety) + 'px'
        return pxoffsetx, pxoffsety


# Exposed functions
@eel.expose
def print_in_python(input):
    print(f"Successfully received: {input}")


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
    # can be sent out to API


if __name__ == '__main__':
    # Start GUI thread
    gui = GUI()
    gui.run()
    eel.sleep(1)
    while True:
        try:
            eel.sleep(5)
        except KeyboardInterrupt:
            exit(0)


