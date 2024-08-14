# Microservice C
import zmq
import json
import datetime

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
    except:
        print("Program Interrupted")
        exit(1)


def update_hourly_widget(msg):
    hud = {}
    for _ in range(7):
        sub_dict = {}
        hrk = msg[f"hr_{_}"]
        sub_dict.update({"temp": hrk["temperature"]})
        time_hr = hrk["startTime"].timetuple()
        print(time_hr, time_hr[3])
        #sub_dict.update({"time": time_hr})
        hud.update({_: sub_dict})
    print(hud)
    return hud


def start_program():
    main()


if __name__ == '__main__':
    pass
