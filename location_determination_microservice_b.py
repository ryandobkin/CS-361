# Microservice C

# test request
# http://freegeoip.net/json/

import ipinfo
import requests
import threading
import json
import outbound_message_manager
import inbound_message_manager
import time


class LocateMe:
    def __init__(self):
        self.socket_port_in = '5563'
        self.socket_port_gui_manager = '5558'
        self.inbound_queue = []

    def main(self):
        while True:
            time.sleep(.5)
            try:
                if len(self.inbound_queue) > 0:
                    request = self.inbound_queue.pop()
                    token = '01a0b7df895938'
                    ip = requests.get('https://api.ipify.org').content.decode('utf-8')
                    handler = ipinfo.getHandler(token)
                    details = handler.getDetails(ip)
                    det = details.all
                    loc_det = det['loc']
                    loc_det = loc_det.split(',')
                    response_message = {"service": "locate_me", "type": "coords", "request": request,
                                        "response": loc_det}
                    outbound_message_manager.send_message(response_message, self.socket_port_gui_manager)
            except:
                print("error")


def start_program():
    locate_me = LocateMe()
    InboundMessageManager = inbound_message_manager.InboundMessageManager(locate_me)
    inbound_message_manager_thread = threading.Thread(target=InboundMessageManager.receive_message, daemon=True)
    inbound_message_manager_thread.start()

    locate_me.main()


if __name__ == '__main__':
    start_program()

