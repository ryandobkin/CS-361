# Written by github.com/Aaronmx1
# Microservice Repo - https://github.com/Aaronmx1/SoftwareEngineeringProject/tree/microserviceA_v2

# Microservice which converts characters or integers.
# This microservice will convert characters to hexadecimal for authentication key generation,
#   and convert Fahrenheit to Celsius
import time
import zmq  # For ZeroMQ
import json

# @Context(): setup the environment to begin socket creation
context = zmq.Context()

# @socket(socket_type): This is the type of socket
#   we will be working with.  REP is a reply socket
socket = context.socket(zmq.REP)

# @bind(addr): This is the address string where the socket
#   will listen on the network port. Port number = 5555
socket.bind("tcp://*:5555")


def main():
    # Create infinite loop that will wait for a message from the client.
    while True:
        # Message from the client
        # @recv(flags=0, copy: bool=True, track: bool=False): will receive a message from the client.
        # This will be blank since we wait for message to arrive
        print("[Converter] Awaiting connection...")
        message = socket.recv()
        print("[Converter] Received connection...")

        # Ryan Networking microservice piece
        try:
            tempC = json.loads(message)
            print(f"RAW: {tempC}")

            if len(tempC) != 1:
                for key, value in tempC.items():
                    value = int(round((float(value) * 9) / 5 + 32,0))
                    tempC[key] = value
                socket.send(json.dumps(tempC).encode())
                print(f"CONVERTED: {tempC}\n")
                continue
        except:
            print("message: ", message)
            # contain hex value
            hexConversion = ''
            # convertor logic
            if len(message) != 1:
                for ch in message:
                    hexConversion += hex(ch)
                socket.send_string(hexConversion)
                continue

        # We will decode the message so that we don't get a 'b' in front of text.
        # ZeroMQ defaults to UTF-8 encoding when nothing is specified
        print(f"Received request from the client: {message.decode()}")

    # Make a clean exit
    context.destroy()


def start_program():
    main()
