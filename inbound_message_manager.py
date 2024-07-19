import socket
import threading
import time
import json


class InboundMessageManager:
    """
    Manges inbound messages for services.
    """
    def __init__(self, service):
        self.service = service
        self.inbound_ip = service.ip
        self.inbound_port = service.port
        self.outbound_queue = service.outbound_queue
        self.inbound_queue = service.inbound_queue

    def run(self):
        """
        Establishes socket
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.bind((self.inbound_ip, self.inbound_port))
            server_socket.listen()
            print(f"[Socket Inbound] Listening on ({self.inbound_ip}, {self.inbound_port})")

            while True:
                client_socket, client_address = server_socket.accept()
                print("[Socket Inbound] Connection Accepted")
                client_thread = threading.Thread(target=self.receive_message, args=(client_socket, client_address), daemon=True)
                client_thread.start()

    def receive_message(self, client_socket, client_address):
        """
        Receives messages incoming over TCP connections from a given service.
        """
        print(f"[Inbound] Connection from {client_address}")
        with client_socket:
            while True:
                data = client_socket.recv(5120)
                if not data:
                    break

                inbound_data = json.loads(data.decode())
                self.inbound_queue.append(inbound_data)
                print(f"[Inbound] Received message: {inbound_data}")

