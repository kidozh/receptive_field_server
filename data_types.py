import dataclasses
import sys
from datetime import datetime
from typing import Callable, Awaitable, Any

import numpy as np
import tornado.websocket
from websockets.legacy.server import WebSocketServerProtocol


class SignalData:
    # timestamp is the milliseconds
    record_end_timestamp: int = 0
    sample_frequency: int = 0
    sample_duration: float = 0
    # multichannel signal in list
    signal_list: list = []
    status: str = ""

    def __init__(self, record_end_timestamp: int, sample_frequency: int, sample_duration: float, signal_list: list,
                 status: str) -> None:
        self.record_end_timestamp = record_end_timestamp
        self.sample_frequency = sample_frequency
        self.sample_duration = sample_duration
        self.signal_list = signal_list
        self.status = status


class SignalRequest:
    code: str = ""
    acquired_microsecond: int = 0
    sample_frequency: int = 0
    sample_duration: float = 0
    signal_arr: list = []
    should_terminate: bool = False

    def __init__(self, code: str, acquired_microsecond: int, sample_frequency: int, sample_duration: float,
                 signal_arr: list, should_terminate: bool):
        self.code = code
        self.acquired_microsecond = acquired_microsecond
        self.sample_frequency = sample_frequency
        self.sample_duration = sample_duration
        self.signal_arr = signal_arr
        self.should_terminate = should_terminate

    def __lt__(self, other):
        return self.acquired_microsecond < other.acquired_microsecond


class SignalRequestInPriorityQueue:

    websocket_protocol: Callable[[WebSocketServerProtocol], Awaitable[Any]]
    signal_request: SignalRequest

    def __init__(self, websocket_protocol: Callable[[WebSocketServerProtocol], Awaitable[Any]],
                 signal_request: SignalRequest):
        self.websocket_protocol = websocket_protocol
        self.signal_request = signal_request


    def __lt__(self, other):
        return self.signal_request < other.signal_request


class SignalRequestTornadoRequestInPriorityQueue:
    websocket_protocol: tornado.websocket.WebSocketHandler
    signal_request: SignalRequest
    queue_microsecond: int = 0

    def __init__(self, websocket_protocol: tornado.websocket.WebSocketHandler,
                 signal_request: SignalRequest, queue_microsecond: int):
        self.websocket_protocol = websocket_protocol
        self.signal_request = signal_request
        self.queue_microsecond = queue_microsecond

    def __lt__(self, other):
        return self.signal_request < other.signal_request


class PredictionResult:
    probability_list: list = []
    acquired_microsecond: int = 0
    queue_microsecond: int = 0
    calculation_microsecond: int = 0
    processed_microsecond: int = 0

    def __init__(self, probability_list: list, acquired_microsecond: int, queue_microsecond:int, calculation_microsecond: int, processed_microsecond: int):
        self.probability_list = probability_list
        self.acquired_microsecond = acquired_microsecond
        self.queue_microsecond = queue_microsecond
        self.calculation_microsecond = calculation_microsecond
        self.processed_microsecond = processed_microsecond


if __name__ == "__main__":
    microsecond = datetime.now().microsecond

    status_bool = True

    bit_size = [64, 32, 16]

    for product_size in [64, 128, 256, 512, 1024]:
        for np_type in [np.float64, np.float32, np.float16]:
            signal_arr = np.random.random((product_size, 1)).astype(np_type)
            print(np_type, product_size, sys.getsizeof(signal_arr))


    # for sample_duration in [0.064, 0.128, 0.192, 0.256, 0.384, 0.448, 0.512, 0.576, 0.064]:
    #     for sample_freq in range(100, 1100, 100):
    #         signal_arr = np.random.random((int(sample_freq * sample_duration), 1)).astype(np.float64)
    #         print(sample_duration, sample_freq, sys.getsizeof(signal_arr))


    # sample_freq = 1000
    # sample_duration = 0.064
    # signal_arr = np.random.random((int(sample_freq * sample_duration), 1)).astype(np.float64)
    # signal_list = signal_arr.tolist()
    # signal_request = SignalRequest(
    #     "CNT",
    #     microsecond,
    #     sample_freq,
    #     sample_duration,
    #     signal_list,
    #     status_bool
    # )
    # print(sys.getsizeof(signal_request), sys.getsizeof(signal_arr))