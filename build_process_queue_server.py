#  Copyright (c) 2024.
import time

import tornado.queues
import tornado.ioloop
import tornado.gen
import tornado.web

import asyncio
import json
import pickle
import threading
from abc import ABC
from asyncio import sleep
from multiprocessing import Process

from typing import Optional, Awaitable, Union, Any
from datetime import datetime

import numpy as np
import tornado
import tornado.websocket
from tornado.ioloop import IOLoop
import tornado.process

from data_types import SignalRequest, PredictionResult, SignalRequestInPriorityQueue, \
    SignalRequestTornadoRequestInPriorityQueue
from tornado import gen, queues, httputil

from models import build_no_bn_shortcut_relu_model

DEFAULT_COOKIE_KEY = 'code'
DEFAULT_COOKIE_VALUE = 'default'

EXPIRE_SECONDS = 5

CONCURRENCY = 1

total_depth = 25

model = build_no_bn_shortcut_relu_model(total_depth, primary_filter=32, input_size=(64, 2))
model.load_weights("RESNET_NO_BN_LAYER_d_25_f_1000_s_0.064_d0.50_PS_100/ep351-loss0.025-val_acc0.991.h5")

q = tornado.queues.PriorityQueue()


class Consumer():

    def __init__(self):
        # self.queued_items = tornado.queues.Queue()
        pass

    @tornado.gen.coroutine
    def watch_queue(self):
        while True:
            print("Watch queue")
            items = yield q.get()
            # go_do_something_with_items(items)
            print(items)


class BatchPredictionWebSocketHandler(tornado.websocket.WebSocketHandler, ABC):
    observer_client_list = []
    publisher_client_list = []
    concurrency = 1
    max_prediction_per_fetch = 100

    client_dict: dict[str, set] = dict()

    def initialize(self) -> None:

        print("Prepare the cache pool")

        # IOLoop.current().spawn_callback(self.run_worker_forever)
        # threading.Thread(
        #     target=self.run_worker_forever
        # ).start()
        print("Cache pool done")

    def __init__(self, application: tornado.web.Application, request: httputil.HTTPServerRequest, **kwargs: Any):
        super().__init__(application, request, **kwargs)
        # self._workers = gen.multi([self.run_worker_forever() for _ in range(self.concurrency)])
        #
        # print("Add callback for the method")
        # IOLoop.current().add_callback(self.run_worker_forever)
        # print("Add consumer by thread")

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

    async def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
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
            signal_request_in_priority_queue = SignalRequestTornadoRequestInPriorityQueue(self, signal_request)
            print("PUT it in queue", signal_request.acquired_microsecond, q.qsize())
            q.put_nowait((signal_request.acquired_microsecond, signal_request_in_priority_queue))

    @tornado.gen.coroutine
    async def run_worker_forever(self):
        print("Start consumer object")
        while True:
            await self.predict_job_worker()

    async def predict_job_worker(self):
        # check with the expiration
        iteration_times = min(q.qsize(), self.max_prediction_per_fetch)
        now = datetime.now()
        index_list: list[SignalRequest] = []
        data_list = []
        print("[WORKER]", q.qsize(), "->", iteration_times)
        if iteration_times == 0:
            await asyncio.sleep(0.1)
            q.task_done()
        for i in range(iteration_times):
            priority, signal_request = await q.get()
            if (now.timestamp() - signal_request.acquired_microsecond) / 1000 < EXPIRE_SECONDS:
                # should append it to the prediction jobs
                data_list.append([signal_request.signal_arr])
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
            await self.write_message(json_prediction_result)


async def predict_job_worker():
    if True:
        # check with the expiration
        iteration_times = min(q.qsize(), 128)
        now = datetime.now()
        index_list: list[SignalRequestTornadoRequestInPriorityQueue] = []
        data_list = []
        print("[WORKER]", q.qsize(), "->", iteration_times)
        if iteration_times == 0:
            return
        for i in range(iteration_times):
            priority, signal_request_in_priority_queue = await q.get()
            signal_request = signal_request_in_priority_queue.signal_request
            if (now.timestamp() - signal_request.acquired_microsecond) / 1000 < EXPIRE_SECONDS:
                # should append it to the prediction jobs
                data_list.append([signal_request.signal_arr])
                index_list.append(signal_request_in_priority_queue)

        # predict by deep learning
        predict_signal_arr = np.concatenate(data_list, axis=0)
        result_arr = model.predict(predict_signal_arr)
        # traverse it one by one
        for i in range(result_arr.shape[0]):
            result = result_arr[i, ...]
            signal_request_in_priority_queue = index_list[i]
            now = datetime.now()
            prediction_result = PredictionResult(result.tolist(),
                                                 signal_request_in_priority_queue.signal_request.acquired_microsecond,
                                                 int(now.timestamp()))
            json_prediction_result = json.dumps(prediction_result.__dict__)
            print(i, result)
            await signal_request_in_priority_queue.websocket_protocol.write_message(json_prediction_result)

            # await self.write_message(json_prediction_result)


async def run_job_consumer():
    BLOCK_SECOND = 0.1
    now  = datetime.now()
    while True:

        await sleep(0.1)
        await predict_job_worker()


if __name__ == "__main__":
    # client = Consumer()
    #
    # # Watch the queue for when new items show up
    # tornado.ioloop.IOLoop.current().add_callback(client.watch_queue)

    # Create the web server
    application = tornado.web.Application([
        (r'/live_ws', BatchPredictionWebSocketHandler),
    ], debug=True)

    tornado.ioloop.IOLoop.current().add_callback(lambda: run_job_consumer())

    # period_callback = tornado.ioloop.PeriodicCallback(lambda: predict_job_worker(), 100)
    # period_callback.start()

    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()