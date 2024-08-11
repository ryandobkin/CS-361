import json
import zmq
import outbound_message_manager


def main():
    outbound_message_manager.send_message(json.load(open('gui_forecast_example.json')), '5558')


if __name__ == '__main__':
    main()
