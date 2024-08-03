import socket
import threading
import time
import json
import zmq


class InboundMessageManager:
    """
    Manges inbound messages for services.
    """
    def __init__(self, service):
        self.inbound_queue = service.inbound_queue
        self.socket_port = service.socket_port_in

#     def run(self):
#         """
#         Establishes socket
#         """
#         with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
#             server_socket.bind((self.inbound_ip, self.inbound_port))
#             server_socket.listen()
#             print(f"[Socket Inbound] Listening on ({self.inbound_ip}, {self.inbound_port})")
#
#             while True:
#                 client_socket, client_address = server_socket.accept()
#                 print("[Socket Inbound] Connection Accepted")
#                 client_thread = threading.Thread(target=self.receive_message, args=(client_socket, client_address), daemon=True)
#                 client_thread.start()

    def receive_message(self):
        """
        Receives messages incoming over TCP connections from a given service.
        """
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{self.socket_port}")
        while True:
            message = socket.recv()
            inbound_data = json.loads(message.decode())
            self.inbound_queue.append(inbound_data)
            print(f"[Inbound] Received message: {inbound_data}")
            socket.send(json.dumps("Ack").encode())

