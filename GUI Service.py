import eel
import threading

# Globals


class GUI:
    """
    GUI Object
    """
    def __init__(self):
        self.daily_rain_percent_0 = 0

    def run(self):
        eel.init('web')
        eel.start('index.html', size=(1280, 800), block=False)


# Exposed functions
@eel.expose
def receive_search(input):
    print(f"Search Input: " + input)
    return input


@eel.expose
def get_rain_percentage():
    return 15


if __name__ == '__main__':
    # Start GUI thread
    gui = GUI()
    gui.run()
    while True:
        try:
            eel.sleep(1)
        except KeyboardInterrupt:
            exit(0)


