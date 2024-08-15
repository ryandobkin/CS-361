# Microservice C
import zmq
import json
from datetime import datetime, timedelta

SOCKET_PORT = '5560'
socket_port_gui_manager = '5558'
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{SOCKET_PORT}")


def main():
    try:
        while True:
            message = json.loads(socket.recv().decode())
            out_dict = update_hourly_widget(message)
            socket.send(json.dumps(out_dict).encode())
    except Exception as e:
        print("[HOURLY FORECAST MICROSERVICE] Error:", e)
        exit(1)


def update_hourly_widget(msg):
    hud = {}
    cto = datetime.fromisoformat(msg["currentTime"])
    for _ in range(7):
        sub_dict = {}
        hrk = msg[(cto + timedelta(hours=_)).isoformat()]
        this_time = int(cto.hour) + _
        goesin = this_time / 12
        print(this_time, goesin)
        if goesin > 2:
            hr_widget_time = f"{this_time - 24} AM"
        elif goesin > 1:
            hr_widget_time = f"{this_time - 12} PM"
        else:
            hr_widget_time = f"{this_time} AM"
        sub_dict.update({"temp": hrk["temperature"]})
        sub_dict.update({"time": hr_widget_time})
        sub_dict.update({"graphic": hrk["genForecast"]["forecast_graphic"]})
        hud.update({str(_): sub_dict})
    print(hud)
    return hud


def start_program():
    main()


if __name__ == '__main__':
    pass
