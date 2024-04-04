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
    acquired_microsecond: int = 0
    sample_frequency: int = 0
    sample_duration: float = 0
    signal_arr: list = []
    should_terminate: bool = False


class PredictionResult:
    probability_list: list = []
    acquired_microsecond: int = 0
    recv_microsecond: int = 0
    processed_microsecond: int = 0
