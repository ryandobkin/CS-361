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
        self.outbound_ip = service.outbound_ip
        self.outbound_port = service.outbound_port
        self.outbound_queue = service.outbound_queue
        self.inbound_queue = service.inbound_queue

    def run(self) -> None:
        """
        Starts the client loop, which runs indefinitely.
        It continuously dequeues messages from the outbound message queue and sends them to the recipient nodes.
        """
        while True:
            if len(self.outbound_queue) > 0:
                message = self.outbound_queue[0]
                self.outbound_queue.pop(0)
                if message:
                    self.send_message(message)
            eel.sleep(5)

    def send_message(self, message):
        """
        Sends message to designated socket
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            try:
                client_socket.connect((self.outbound_ip, self.outbound_port))
                print(f"[Outbound] Connected to ({self.outbound_ip}, {self.outbound_port})")
                client_socket.sendall(message.encode())
                print(f"[Outbound] Sent message: {message}")
                data = client_socket.recv(1024)
                print(f"[Outbound] Received response: {data.decode()}")
                if data.decode() != 'Acknowledgement':
                    self.inbound_queue.append(data.decode())
            except ConnectionRefusedError:
                print("[Outbound] ConnectionRefusedError")
            except AttributeError:
                print("[Outbound] AttributeError")

