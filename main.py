from GUI_Service import GUI
import eel
import threading

condition_list = ["sunny", "partly_cloudy", "cloudy", "haze", "fog", "windy", "thunderstorm_rain"]


def startup():
    gui_service = GUI()
    gui_service.run()
    for _ in range(7):
        print(_)
        eel.sleep(3)
        gui_service.update_location(f"Day-{_}")
        gui_service.update_daily_rain_percent()
        gui_service.update_daily_wind()
        gui_service.update_daily_hilo()
        gui_service.update_daily_weather_condition_text()
        gui_service.update_daily_weather_condition_graphic()


if __name__ == '__main__':
    startup()
