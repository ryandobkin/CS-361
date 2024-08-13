# Runs every microservice/program with one click

import gui_manager
import forecast_service
import api_interface_microservice_a
import converter_microservice_a
import location_determination_microservice_b
import detailed_weather_microservice_d
import threading


if __name__ == '__main__':
    # Forecast Service thread
    forecast_service_thread = threading.Thread(target=forecast_service.start_program, daemon=True)
    forecast_service_thread.start()

    # API Interface Thread
    api_interface_thread = threading.Thread(target=api_interface_microservice_a.start_program, daemon=True)
    api_interface_thread.start()

    # Converter Thread
    converter_microservice_thread = threading.Thread(target=converter_microservice_a.start_program, daemon=True)
    converter_microservice_thread.start()

    # Microservice B Thread
    location_determination_microservice_thread = \
        threading.Thread(target=location_determination_microservice_b.start_program, daemon=True)
    location_determination_microservice_thread.start()

    # Microservice D Thread
    detailed_weather_microservice_thread = \
        threading.Thread(target=detailed_weather_microservice_d.main, daemon=True)
    detailed_weather_microservice_thread.start()

    # GUI Manager thread
    # gui_manager_thread = threading.Thread(target=gui_manager.start_program, daemon=True)
    # gui_manager_thread.start()

    gui_manager.start_program()
