# Microservice-A
import zmq
import json

SOCKET_PORT = '5562'
socket_port_gui_manager = '5558'
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind(f"tcp://*:{SOCKET_PORT}")


def main():
    try:
        while True:
            message = socket.recv()
            text_updater(message)
            graphic_updater(message)
            socket.send(json.dumps("Ack").encode())
    except:
        print("Program Interrupted")
        exit(1)


def text_updater(message):
    """
    Updates the text fields of the GUI current conditions widgets
    """
    sun_data = message["sunrise_sunset"]
    sun_update_list = [sun_data["sunrise"], sun_data["sunset"], sun_data["dawn"], sun_data["dusk"]]

    uv_update_val = message["uv_index"]["uv"]


def graphic_updater():
    pass







def start_program():
    main()


if __name__ == '__main__':
    pass
