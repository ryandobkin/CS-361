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
        #print(f"[Outbound] Connected to ({socket})")
        socket.send(json.dumps(message).encode())
        #print(f"[Outbound] Sent message: {message}")
        message = socket.recv()
        #print(f"[Outbound] Received reply: {message}")
        context.destroy()
        print("outbound req/res complete")
        return json.loads(message.decode())
    except ConnectionRefusedError:
        print("[Outbound] ConnectionRefusedError")
    except AttributeError:
        print("[Outbound] AttributeError")

