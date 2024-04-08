import json
import time

import websocket
import threading
from datetime import datetime

from data_types import SignalData, SignalRequest

URL = ""


class ExponentialBackoffClient:
    """
    Sending the request following exponential backoff
    """
    # the basic relay is 1.414 (sqrt 2)
    # relay_delay_base = 1.41421356
    relay_delay_base = 2
    initial_delay_division = 2
    delay = 0
    recv_last_prediction = False

    def __init__(self, url: str, sampling_rate: int, sampling_duration: float):
        self.websocketApp = websocket.WebSocketApp(url, on_message=self.on_recv_message)
        self.last_submission_time: datetime = datetime.now()
        self.sampling_rate = sampling_rate
        self.sampling_duration = sampling_duration
        self.initial_delay = sampling_duration / self.initial_delay_division
        threading.Thread(
            target=self.websocketApp.run_forever
        ).start()
        print("Please wait 1s for establishment")
        time.sleep(1)
        # self.websocketApp.run_forever()

    def on_recv_message(self, websocketApp, message):
        # adjust the speed accordingly
        # check with the delay
        now: datetime = datetime.now()
        second_since_last_submission = (now.timestamp() - self.last_submission_time.timestamp())
        self.recv_last_prediction = True

        if second_since_last_submission < self.delay / self.relay_delay_base:
            self.delay = self.delay / self.relay_delay_base
        elif second_since_last_submission > self.delay / self.relay_delay_base:
            self.delay = self.delay * self.relay_delay_base

        if self.delay <= self.initial_delay:
            self.delay = self.initial_delay

        print("Actual time: %.3f s, delay %.3f, refresh rate: %.0f Hz" % (
        second_since_last_submission, self.delay, 1 / self.delay))

    def send_json_data_if_delay_permitted(self, signalData: SignalData):
        now: datetime = datetime.now()
        second_since_last_submission = (now.timestamp() - self.last_submission_time.timestamp())
        # print(second_since_last_submission, self.delay)
        if second_since_last_submission >= self.delay:
            if self.delay == 0:
                # intialize the delay
                self.delay = self.initial_delay
            json_string: str = json.dumps(signalData.__dict__)
            self.last_submission_time: datetime = datetime.now()
            self.websocketApp.send(json_string)
            return True
        else:
            # should not send it due to the cooldown period
            return False
            pass


class ExponentialBackoffStatefulClient(ExponentialBackoffClient):
    code: str

    def __init__(self, code: str, url: str, sampling_rate: int, sampling_duration: float, *args, **kwargs):
        super().__init__(url, sampling_rate, sampling_duration)
        self.code = code

    def send_signal_request_json_if_delay_permitted(self, signalRequest: SignalRequest):
        now: datetime = datetime.now()
        second_since_last_submission = (now.timestamp() - self.last_submission_time.timestamp())
        if second_since_last_submission >= self.delay:
            if self.delay == 0:
                # intialize the delay
                self.delay = self.initial_delay
            json_string: str = json.dumps(signalRequest.__dict__)
            self.last_submission_time: datetime = datetime.now()
            if not self.recv_last_prediction:
                self.delay = self.delay * self.relay_delay_base
            self.websocketApp.send(json_string)
            return True
        else:
            # should not send it due to the cooldown period
            return False
            pass
