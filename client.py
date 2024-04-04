import websocket
from datetime import datetime

HOST = "localhost"
PORT = "8888"


class ExponentialBackoffClient:
    """
    Sending the request following exponential backoff
    """
    # the basic relay is 1.414
    relay_delay_base = 1.41421356
    delay = 0

    def __init__(self, sampling_rate: int, sampling_duration: float):
        self.websocketApp = websocket.WebSocketApp("ws://%s:%s" % (HOST, PORT), on_message=self.on_recv_message)
        self.last_submission_time = datetime.now()
        self.sampling_rate = sampling_rate
        self.sampling_duration = sampling_duration
        self.websocketApp.run_forever()

    def on_recv_message(self, websocketApp, message):
        print(message)

    def send_data_if_delay_permitted(self):
        self.websocketApp.send(

        )
