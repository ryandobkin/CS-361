# Runs every microservice/program with one click

import gui_manager
import forecast_service
import api_interface_microservice_a
import converter_microservice_a
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

    # GUI Manager thread
    # gui_manager_thread = threading.Thread(target=gui_manager.start_program, daemon=True)
    # gui_manager_thread.start()

    gui_manager.start_program()
