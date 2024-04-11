#!/usr/bin/env python

import asyncio
import json
import pickle
import queue
from multiprocessing.queues import Queue, SimpleQueue
import threading
from datetime import datetime
from multiprocessing import Process, freeze_support
from typing import Callable, Awaitable, Any

import numpy as np
import tornado.ioloop
from websockets.legacy.server import WebSocketServerProtocol
from websockets.server import serve

from data_types import SignalRequest, SignalRequestInPriorityQueue, PredictionResult
from models import build_no_bn_shortcut_relu_model

EXPIRE_SECONDS = 5

CONCURRENCY = 1

total_depth = 25

max_prediction_per_fetch = 128

model = build_no_bn_shortcut_relu_model(total_depth, primary_filter=32, input_size=(64, 2))
model.load_weights("RESNET_NO_BN_LAYER_d_25_f_1000_s_0.064_d0.50_PS_100/ep351-loss0.025-val_acc0.991.h5")
model.predict(np.zeros(shape=(64,64,2)))

predict_queue = queue.Queue()

async def echo(websocket):
    async for message in websocket:
        print(message)
        await websocket.send(message)

async def predict_handler(websocket):
    """
    It is the consumer
    """
    await asyncio.sleep(0.5)
    async for message in websocket:
        signal_request = None
        if isinstance(message, str):
            # is a json format?
            json_data: json = json.loads(message)
            signal_request = SignalRequest(**json_data)
        elif isinstance(message, bytes):
            obj = pickle.dumps(message)
            if isinstance(obj, SignalRequest):
                signal_request = obj

        if signal_request is None:
            websocket.close(1004, 'The message is not a valid SignalRequest object.')
            return

        # Check with expiration
        now = datetime.now()

        if (now.timestamp() - signal_request.acquired_microsecond) / 1000 < EXPIRE_SECONDS:
            print("PUT it in queue", signal_request.acquired_microsecond, predict_queue.qsize())
            signal_request_in_priority_queue = SignalRequestInPriorityQueue(websocket, signal_request)
            predict_queue.put_nowait(signal_request_in_priority_queue)
            # await predict_job_worker()


async def predict_job_worker():
    # check with the expiration
    iteration_times = min(predict_queue.qsize(), max_prediction_per_fetch)
    now = datetime.now()
    index_list: list[Callable[[WebSocketServerProtocol], Awaitable[Any]]] = []
    data_list = []
    print('Predict iteration ', iteration_times)
    if iteration_times == 0:
        return
    for i in range(iteration_times):
        signal_request_in_priority_queue: SignalRequestInPriorityQueue = predict_queue.get()
        signal_request = signal_request_in_priority_queue.signal_request
        websocket_protocol = signal_request_in_priority_queue.websocket_protocol
        if (now.timestamp() - signal_request.acquired_microsecond) / 1000 < EXPIRE_SECONDS:
            # should append it to the prediction jobs
            data_list.append([signal_request.signal_arr])
            index_list.append(websocket_protocol)

    # if len(data_list) == 1:
    #     # if only one element
    #     data_list.append(np.zeros(shape=(64,2)))

    # predict by deep learning
    predict_signal_arr = np.concatenate(data_list, axis=0)
    print("PREDICT SHAPE",predict_signal_arr.shape)
    result_arr = model.predict(predict_signal_arr)
    # traverse it one by one
    for i in range(len(index_list)):
        result = result_arr[i, ...]
        websocket_protocol = index_list[i]
        now = datetime.now()
        prediction_result = PredictionResult(result.tolist(), signal_request.acquired_microsecond,
                                             int(now.timestamp()))
        json_prediction_result = json.dumps(prediction_result.__dict__)
        # look at the table now
        websocket_protocol.send(json_prediction_result)
        # for client in self.client_dict[signal_request.code]:
        #     client.write_message(json_prediction_result)

async def run_consumer_forever():
    print("RUN consumer thread")
    while True:
        await asyncio.sleep(0.5)
        await predict_job_worker()

async def main():
    async with serve(predict_handler, "localhost", 8888):
        # await run_consumer_forever()
        print("Successfully run it")
        await asyncio.Future()  # run forever


if __name__ == "__main__":
    freeze_support()

    asyncio.run(main())

