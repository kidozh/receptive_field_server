import json
import pickle
from abc import ABC
from typing import Optional, Awaitable, Union
from datetime import datetime
import tornado
import tornado.websocket

from data_types import SignalRequest
from tornado import gen, queues

DEFAULT_COOKIE_KEY = 'code'
DEFAULT_COOKIE_VALUE = 'default'

EXPIRE_SECONDS = 5

CONCURRENCY = 1


class ProcessingWebSocket(tornado.websocket.WebSocketHandler, ABC):
    observer_client_list = []
    publisher_client_list = []
    workers = 1
    max_prediction_per_fetch = 100

    client_dict: dict[str, set] = dict()

    q = queues.PriorityQueue()

    def __int__(self, workers=1, max_prediction_per_fetch=100):
        self.workers = workers
        self.max_prediction_per_fetch = max_prediction_per_fetch
        # start a worker that run forever

        pass

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        # check the code
        code = self.get_cookie(DEFAULT_COOKIE_KEY, DEFAULT_COOKIE_VALUE)

        if code not in self.client_dict.keys():
            self.client_dict[code] = set()

        #  add it to client list
        self.client_dict[code].add(self)

        return super().open(*args, **kwargs)

    def on_close(self) -> None:
        for code, client_set in self.client_dict.items():
            if self in client_set:
                client_set.remove(self)
                break

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        signal_request = None
        code = self.get_cookie(DEFAULT_COOKIE_KEY, DEFAULT_COOKIE_VALUE)

        if isinstance(message, str):
            # is a json format?
            json_data: json = json.loads(message)
            signal_request = SignalRequest(**json_data)
        elif isinstance(message, bytes):
            obj = pickle.dumps(message)
            if isinstance(obj, SignalRequest):
                signal_request = obj

        if signal_request is None:
            return

        # Check with expiration
        now = datetime.now()
        if now.timestamp() - signal_request.acquired_microsecond / 1000 < EXPIRE_SECONDS:
            self.q.put((signal_request.acquired_microsecond, signal_request))

    async def predict_job_worker(self) :
        # check with the expiration
        iteration_times = min(self.q.qsize(), self.max_prediction_per_fetch)
        now = datetime.now()

        for i in range(iteration_times):
            priority, signal_request = await self.q.get()
            if now.timestamp() - signal_request.acquired_microsecond / 1000 < EXPIRE_SECONDS:
                # should append it to the prediction jobs

                pass
