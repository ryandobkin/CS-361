import zmq
import eel
import json
import threading


def send_message(message, socket_port):
    """
    Sends message to designated socket
    """
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect(f"tcp://localhost:{socket_port}")
    try:
        socket.send(json.dumps(message).encode())
        print(f"[OBMM {socket_port}] SEND {message}")
        message = socket.recv()
        print(f"[OBMM {socket_port}] RECV")
        context.destroy()
        return json.loads(message.decode())
    except ConnectionRefusedError:
        print(f"[OBMM {socket_port}] ConnectionRefusedError")
    except AttributeError:
        print(f"[OBMM {socket_port}] AttributeError")

