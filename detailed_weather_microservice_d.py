# Microservice-A
import zmq
import json
from datetime import datetime
import pytz

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
            socket.send(json.dumps(text_dict).encode())
    except Exception as e:
        print("Error:", e)
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
    trd = {}
    # Assigns data to dict
    sun_data = message["sunrise_sunset"]
    sun_list = [sun_data["sunrise"], sun_data["sunset"], sun_data["dawn"], sun_data["dusk"]]
    curr = 0
    for _ in sun_list:
        # Remove the seconds from date
        spl_m = _.split(' ')[1]
        spl_time = _.split(':')
        spl_new = f"{spl_time[0]}:{spl_time[1]} {spl_m}"
        # Convert to datetime object so that we can convert time zone from UTC

        combined_str = f'2024-08-14 {spl_new}'
        date_format = '%Y-%m-%d %I:%M %p'
        dt_spl = datetime.strptime(combined_str, date_format)
        utc = pytz.timezone('UTC')
        localized = utc.localize(dt_spl)
        new_tz = pytz.timezone(sun_data["time_zone"])
        convert_dt = localized.astimezone(new_tz)
        hour = convert_dt.strftime('%I').lstrip('0')
        local_spl = convert_dt.strftime('%M %p')
        final_spl = f'{hour}:{local_spl}'
        sun_list[curr] = final_spl
        curr += 1

    trd.update({"sunrise": sun_list[0], "sunset": sun_list[1],
                "dawn": sun_list[2], "dusk": sun_list[3]})
    trd.update({"uv_index": message["uv_index"]["uvi"]})
    trd.update({"relativeHumidity": message["humidity"]["relativeHumidity"],
                "dewpoint": message["humidity"]["dewpoint"]})
    trd.update({"pressure": '%.2f' % message["pressure"]["pressure"]})
    trd.update({"windSpeed": '%.1f' % message["wind"]["windSpeed"],
                "windDirectionDeg": message["wind"]["windDirection"]})

    # Updates wind direction str value
    wd_deg = trd["windDirectionDeg"]
    if 337.5 < wd_deg <= 22.5:
        wd_str = 'From North'
    elif 22.5 < wd_deg <= 67.5:
        wd_str = 'From Northeast'
    elif 67.5 < wd_deg <= 112.5:
        wd_str = 'From East'
    elif 112.5 < wd_deg <= 157.5:
        wd_str = 'From Southeast'
    elif 157.5 < wd_deg <= 202.5:
        wd_str = 'From South'
    elif 202.5 < wd_deg <= 247.5:
        wd_str = 'From Southwest'
    elif 247.5 < wd_deg <= 292.5:
        wd_str = 'From West'
    elif 292.5 < wd_deg <= 337.5:
        wd_str = 'From Northwest'
    else:
        wd_str = 'From Undefined'

    # Updates wind status str value
    wd_sp = int(message["wind"]["windSpeed"])
    if wd_sp <= 1:
        wd_st = 'Calm'
    elif 1 < wd_sp <= 3.5:
        wd_st = 'Light Air'
    elif 3.5 < wd_sp <= 7.5:
        wd_st = 'Light Breeze'
    elif 7.5 < wd_sp <= 12.5:
        wd_st = 'Gentle Breeze'
    elif 12.5 < wd_sp <= 18.5:
        wd_st = 'Moderate Breeze'
    elif 18.5 < wd_sp <= 24.5:
        wd_st = 'Fresh Breeze'
    elif 24.5 < wd_sp <= 31.5:
        wd_st = 'Strong Breeze'
    elif 31.5 < wd_sp <= 38.5:
        wd_st = 'Near Gale'
    elif 38.5 < wd_sp <= 46.5:
        wd_st = 'Gale'
    elif 46.5 < wd_sp <= 54.5:
        wd_st = 'Strong Gale'
    elif 54.5 < wd_sp <= 63.5:
        wd_st = 'Whole Gale'
    elif 63.5 < wd_sp <= 75:
        wd_st = 'Storm Force'
    elif 75 < wd_sp:
        wd_st = 'Hurricane Force'
    else:
        wd_st = 'Good Luck'

    full_wd_str = f"{wd_st} • {wd_str}"
    trd.update({"windDirectionStr": full_wd_str})
    print("[DETAILED WEATHER] Current Conditions Popup Widget Update Dict Returned")
    return trd


def graphic_updater(message):
    pass







def start_program():
    main()


if __name__ == '__main__':
    pass
