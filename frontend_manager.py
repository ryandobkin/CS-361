import socket
import time
import json
import threading
from inbound_message_manager import InboundMessageManager
from outbound_message_manager import OutboundMessageManager


class FrontendManager:
    """
    The main controlling object for the Weather application.
    Keeps values and calls and receives functions.

    In the future, will write to files or use websockets to receive/send data between
    services. For now, will probably write to files.
    """
    def __init__(self):
        self.ip = '127.0.0.1'
        self.port = 23456
        self.service_sockets = {"api_manager": ['127.0.0.2', 23457], "gui_manager": ['127.0.0.3', 23458]}
        self.service_list = {"t": ""}
        self.outbound_queue = []
        self.inbound_queue = []
        self.location_widget = "Los Angeles, CA"
        self.search_query = None
        self.hourly_widget = {0: {'temp': 75, 'time': 'Now', 'graphic': 'haze'}}
        self.now_widget = {"temp": 0, "hi": 0, "lo": 0, "condition": 'Cloudy', "graphic": 'haze', "feels_like": 75}
        self.sunrise_widget = {"sunrise": 6, "sunset": 12, "dawn": 10, "dusk": 20}
        self.uv_widget = {"uv_value": 0}
        self.wind_widget = {"speed": 0, "direction": 'N'}
        self.humidity_widget = {"humidity": 0, "dew": 50}
        self.pressure_widget = {"pressure": 30}
        self.alert_widget = {"active_alert": True, "header": "Severe Weather Alert", "body": "High Wind",
            "source": "National Weather Service"}
        self.daily_widget = {0: {"date": "Today", "graphic": 'haze', "condition": 'cloudy', "hi": 80, "lo": 60,
            "rain": 30, "wind_speed": 0, "wind_direction": 'N'}}

    def manager(self):
        while True:
            self.inbound_queue_processor()
            time.sleep(1)

    def inbound_queue_processor(self):
        """
        Processes and sends queue data to the correct socket/services.
        """
        if len(self.inbound_queue) > 0:
            try:
                message = self.inbound_queue[0]
                self.inbound_queue.pop(0)
                if message["service"] == "forecast":
                    if message["type"] == "response":
                        socket_data = self.service_sockets['gui_manager']
                        message.update({"socket": [socket_data[0], socket_data[1]]})
                        print(f"Sending ({message})\nto: ({socket_data[0]}, {socket_data[1]}")
                        self.outbound_queue.append(message)
                    elif message["type"] == "request":
                        socket_data = self.service_sockets['api_manager']
                        message.update({"socket": [socket_data[0], socket_data[1]]})
                        print(f"Sending ({message}) to = ({socket_data[0]}, {socket_data[1]}")
                        self.outbound_queue.append(message)
            except AttributeError:
                print("Attribute Error: Not a valid dict")




if __name__ == '__main__':
    frontend_manager = FrontendManager()

    # Starts the incoming message loop thread
    inbound_message_manager = InboundMessageManager(frontend_manager)
    incoming_message_manager_thread = threading.Thread(target=inbound_message_manager.run, daemon=True)
    incoming_message_manager_thread.start()

    # Starts the outgoing message loop thread
    outbound_message_manager = OutboundMessageManager(frontend_manager)
    outgoing_message_manager_thread = threading.Thread(target=outbound_message_manager.run, daemon=True)
    outgoing_message_manager_thread.start()

    frontend_manager.manager()

