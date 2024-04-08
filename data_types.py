import dataclasses


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


class PredictionResult:
    probability_list: list = []
    acquired_microsecond: int = 0
    # recv_microsecond: int = 0
    processed_microsecond: int = 0

    def __init__(self, probability_list: list, acquired_microsecond: int, processed_microsecond: int):
        self.probability_list = probability_list
        self.acquired_microsecond = acquired_microsecond
        self.processed_microsecond = processed_microsecond

