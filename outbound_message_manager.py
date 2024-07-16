import socket
import eel
import json
import threading


class OutboundMessageManager:
    """
    Manges outbound messages for services.
    """
    def __init__(self, service):
        self.service = service
        self.outbound_queue = service.outbound_queue
        self.inbound_queue = service.inbound_queue

    def run(self) -> None:
        """
        Starts the client loop, which runs indefinitely.
        It continuously dequeues messages from the outbound message queue and sends them to the recipient nodes.
        """
        while True:
            if len(self.outbound_queue) > 0:
                message = self.outbound_queue.pop(0)
                if message:
                    self.send_message(message)
            eel.sleep(.1)

    def send_message(self, message):
        """
        Sends message to designated socket
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                print(message["socket"])
                ip, port = message["socket"]
                client_socket.connect((ip, port))
                print(f"[Outbound] Connected to ({ip}, {port})")
                print(f"[Outbound] Message: {message}")
                client_socket.sendall(json.dumps(message).encode())
                print(f"[Outbound] Sent message: {message}")
            except ConnectionRefusedError:
                print("[Outbound] ConnectionRefusedError")
            except AttributeError:
                print("[Outbound] AttributeError")

