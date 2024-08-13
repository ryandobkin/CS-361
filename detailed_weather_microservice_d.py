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
            message = json.loads(socket.recv().decode())
            text_dict = text_updater(message)
            #graphic_updater(message)
            socket.send(json.dumps(text_dict).encode())
    except:
        print("Program Interrupted")
        exit(1)


def text_updater(message):
    """
    Returns the appropriately parsed dict containing the update values for the current conditions widget.

    sun = (sunrise, sunset, dawn, dusk : int)

    uv = (uv_value : int)

    humidity = (humidity, dew : int)

    wind = (speed : int, direction : str)

    pressure = (pressure : int)
    """
    text_response_dict = {}
    sun_data = message["sunrise_sunset"]
    text_response_dict.update({"sunrise": sun_data["sunrise"], "sunset": sun_data["sunset"],
                              "dawn": sun_data["dawn"], "dusk": sun_data["dusk"]})
    text_response_dict.update({"uv_index": message["uv_index"]["uvi"]})
    text_response_dict.update({"windSpeed": message["wind"]["windSpeed"],
                               "windDirectionDeg": message["wind"]["windDirection"]})
    wd_deg = text_response_dict["windDirectionDeg"]
    if 337.5 < wd_deg <= 22.5:
        wd_str = 'N'
    elif 22.5 < wd_deg <= 67.5:
        wd_str = 'NE'
    elif 67.5 < wd_deg <= 112.5:
        wd_str = 'E'
    elif 112.5 < wd_deg <= 157.5:
        wd_str = 'SE'
    elif 157.5 < wd_deg <= 202.5:
        wd_str = 'S'
    elif 202.5 < wd_deg <= 247.5:
        wd_str = 'SW'
    elif 247.5 < wd_deg <= 292.5:
        wd_str = 'W'
    elif 292.5 < wd_deg <= 337.5:
        wd_str = 'NW'
    else:
        wd_str = 'D'
    text_response_dict.update({"windDirectionStr": wd_str})
    text_response_dict.update({"relativeHumidity": message["humidity"]["relativeHumidity"],
                               "dewpoint": message["humidity"]["dewpoint"]})
    text_response_dict.update({"pressure": message["pressure"]["pressure"]})
    return text_response_dict


def graphic_updater(message):
    pass







def start_program():
    main()


if __name__ == '__main__':
    pass
