import eel
import threading
import GUI_Service

condition_list = ["sunny", "partly_cloudy", "cloudy", "haze", "fog", "windy", "thunderstorm_rain"]

class GUI_Manager:
    """

    """

def startup():
    for _ in range(7):
        try:
            print(_)
            eel.sleep(2)
            GUI_Service.update_location(f"Day {_}")
            GUI_Service.update_daily_rain_percent(_, _)
            GUI_Service.update_daily_wind(_, "NW", _)
            GUI_Service.update_daily_hilo(_, _, _)
            GUI_Service.update_daily_weather_condition_text(_, "Meh")
            GUI_Service.update_daily_weather_condition_graphic(_, 'heavy_rain')
        except KeyboardInterrupt:
            exit(1)


if __name__ == '__main__':
    try:
        eel.spawn(startup)
        GUI_Service.run()
    except KeyboardInterrupt:
        exit(1)
