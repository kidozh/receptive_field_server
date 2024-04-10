import asyncio
import json
import pickle
import threading
from abc import ABC
from asyncio import sleep
from typing import Optional, Awaitable, Union, Any
from datetime import datetime

import numpy as np
import tornado
import tornado.websocket
from tornado.ioloop import IOLoop
import tornado.process

from data_types import SignalRequest, PredictionResult
from tornado import gen, queues, httputil

from models import build_no_bn_shortcut_relu_model

DEFAULT_COOKIE_KEY = 'code'
DEFAULT_COOKIE_VALUE = 'default'

EXPIRE_SECONDS = 5

CONCURRENCY = 1

total_depth = 25

model = build_no_bn_shortcut_relu_model(total_depth, primary_filter=32, input_size=(64, 2))
model.load_weights("RESNET_NO_BN_LAYER_d_25_f_1000_s_0.064_d0.50_PS_100/ep351-loss0.025-val_acc0.991.h5")


class BatchPredictionWebSocketHandler(tornado.websocket.WebSocketHandler, ABC):
    observer_client_list = []
    publisher_client_list = []
    concurrency = 1
    max_prediction_per_fetch = 100

    client_dict: dict[str, set] = dict()

    q = queues.PriorityQueue()

    def initialize(self, concurrency, max_prediction_per_fetch=128) -> None:
        self.concurrency = concurrency
        self.max_prediction_per_fetch = max_prediction_per_fetch

        print("Prepare the cache pool")

        # IOLoop.current().spawn_callback(self.run_worker_forever)
        # threading.Thread(
        #     target=self.run_worker_forever
        # ).start()
        print("Cache pool done")

    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        self._workers = gen.multi([self.run_worker_forever() for _ in range(self.concurrency)])

        print("Add callback for the method")
        IOLoop.current().add_callback(self.run_worker_forever)
        print("Add consumer by thread")

        tornado.process.Subprocess(

        )

        threading.Thread(
            target=self.run_worker_forever
        ).start()

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
            self.close(1004, 'The message is not a valid SignalRequest object.')
            return

        # Check with expiration
        now = datetime.now()

        if (now.timestamp() - signal_request.acquired_microsecond) / 1000 < EXPIRE_SECONDS:
            print("PUT it in queue", signal_request.acquired_microsecond, self.q.qsize())
            self.q.put((signal_request.acquired_microsecond, signal_request))

    @tornado.gen.coroutine
    async def run_worker_forever(self):
        print("Start consumer object")
        while True:
            await self.predict_job_worker()

    @tornado.gen.coroutine
    async def predict_job_worker(self):
        # check with the expiration
        iteration_times = min(self.q.qsize(), self.max_prediction_per_fetch)
        now = datetime.now()
        index_list: list[SignalRequest] = []
        data_list = []
        print("[WORKER]", self.q.qsize(), "->", iteration_times)
        if iteration_times == 0:
            await asyncio.sleep(0.1)
            self.q.task_done()
        for i in range(iteration_times):
            signal_request = await self.q.get()
            if (now.timestamp() - signal_request.acquired_microsecond) / 1000 < EXPIRE_SECONDS:
                # should append it to the prediction jobs
                data_list.append(signal_request.signal_arr)
                index_list.append(signal_request)

        # predict by deep learning
        predict_signal_arr = np.concatenate(data_list, axis=0)
        result_arr = model.predict(predict_signal_arr)
        # traverse it one by one
        for i in range(result_arr.shape[0]):
            result = result_arr[i, ...]
            signal_request = index_list[i]
            now = datetime.now()
            prediction_result = PredictionResult(result.tolist(), signal_request.acquired_microsecond,
                                                 int(now.timestamp()))
            json_prediction_result = json.dumps(prediction_result.__dict__)
            # look at the table now
            for client in self.client_dict[signal_request.code]:
                client.write_message(json_prediction_result)
