import json
from datetime import datetime
import time
from multiprocessing import Process

import numpy as np

from data_types import SignalData, SignalRequest
from client import ExponentialBackoffClient, ExponentialBackoffStatefulClient

RAW_SAMPLE_RATE = 100000

URL = "ws://localhost:8888/live_ws"

# send

TOOL_INDEX = 3
HOLE_INDEX = 15
SAMPLE_DURATION = 0.064
SAMPLE_FREQ = 1000

CODE = "MCR"

def send_random_data_to_server():
    expoentialBackoffClient = ExponentialBackoffStatefulClient(CODE, URL, SAMPLE_FREQ, SAMPLE_DURATION)
    while True:
        sample = (np.random.rand(64,2) -0.5)* 1000
        timestamp = int(datetime.now().timestamp())
        signal_request = SignalRequest(CODE, timestamp, SAMPLE_FREQ, SAMPLE_DURATION, sample.tolist(),
                                       False)
        isSent = expoentialBackoffClient.send_signal_request_json_if_delay_permitted(signal_request)
        # if isSent:
        #     print("SEND", timestamp, sample.shape)

if __name__ == "__main__":
    thread_number = 1
    process_list = []
    for _ in range(thread_number):
        p = Process(target=send_random_data_to_server)
        p.start()
        process_list.append(p)

    for p in process_list:
        p.join()