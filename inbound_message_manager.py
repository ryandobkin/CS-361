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

    def receive_message(self):
        """
        Receives messages incoming over TCP connections from a given service.
        """
        context = zmq.Context()
        socket = context.socket(zmq.REP)
        socket.bind(f"tcp://*:{self.socket_port}")
        while True:
            message = socket.recv()
            print("[IBMM] RECV")
            inbound_data = json.loads(message.decode())
            self.inbound_queue.append(inbound_data)
            print(f"[IBMM] Received message: {inbound_data}")
            socket.send(json.dumps("Ack").encode())
            print("[IBMM] SEND")

