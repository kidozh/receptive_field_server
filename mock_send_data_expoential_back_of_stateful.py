import json
from datetime import datetime
import time

import numpy as np
from websocket import create_connection

from data_types import SignalData, SignalRequest
from data import Data
from client import ExponentialBackoffClient, ExponentialBackoffStatefulClient

RAW_SAMPLE_RATE = 100000

URL = "ws://localhost:8888/"

# send

TOOL_INDEX = 3
HOLE_INDEX = 15
SAMPLE_DURATION = 0.064
SAMPLE_FREQ = 1000

CODE = "MCR"

assert RAW_SAMPLE_RATE % SAMPLE_FREQ == 0

dataset = Data()
dataframe = dataset.get_segment_data(TOOL_INDEX, HOLE_INDEX)
multi_channel_signal = dataframe.to_numpy()[:, 1:6]

subsampled_signal = multi_channel_signal[::RAW_SAMPLE_RATE // SAMPLE_FREQ, :2]
print(multi_channel_signal.shape)

INCREMENT_LENGTH = int(SAMPLE_FREQ * SAMPLE_DURATION)
SAMPLE_END_TIME = INCREMENT_LENGTH

expoentialBackoffClient = ExponentialBackoffStatefulClient(CODE, URL, SAMPLE_FREQ, SAMPLE_DURATION)

print("Ready to send request")

while True:
    SAMPLE_END_TIME = INCREMENT_LENGTH
    while SAMPLE_END_TIME < subsampled_signal.shape[0]:
        # time.sleep(0.01)
        sample = subsampled_signal[SAMPLE_END_TIME - INCREMENT_LENGTH:SAMPLE_END_TIME]
        sample = np.asarray(sample, dtype=np.float16)
        # print(sample.shape, sample)
        # send it to signal
        timestamp = int(datetime.now().timestamp())
        signal_request = SignalRequest(CODE, timestamp, SAMPLE_FREQ, SAMPLE_DURATION, sample.tolist(),
                                       False)
        isSent = expoentialBackoffClient.send_signal_request_json_if_delay_permitted(signal_request)
        if isSent:
            print("SEND", timestamp)

        SAMPLE_END_TIME += INCREMENT_LENGTH

signal_data = SignalData(int(time.time() * 1000), SAMPLE_FREQ, SAMPLE_DURATION, [], 'end')
json_string: str = json.dumps(signal_data.__dict__)
print(ws.send(json_string))

ws.close()
