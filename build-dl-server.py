import asyncio
import json
import os
import traceback
from typing import Optional, Awaitable, Union

import numpy as np
import tornado
import tornado.websocket
from datetime import datetime
from models import build_no_bn_shortcut_relu_model
from data_types import SignalData

total_depth = 25


model = build_no_bn_shortcut_relu_model(total_depth, primary_filter=32, input_size=(64, 2))
model.load_weights("RESNET_NO_BN_LAYER_d_25_f_1000_s_0.064_d0.50_PS_100/ep351-loss0.025-val_acc0.991.h5")
# to warm up the model
model.predict(np.random.random((1,64,2)))

DRILL_STAGE_NAME = ["Engagement", "CFRP", "Material transition", "Al", "Disengagement"]

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
        # self.write(template_loader.load("index.html").generate())

class IdentificationProcessingHandler(tornado.web.RequestHandler):
    def get(self):
        code = self.get_argument('code', '')
        # set cookie
        self.set_cookie('code', code, expires_days=10)
        self.render("monitor.html", code=code)
        # self.write(template_loader.load('monitor.html').generate(code=code))


class ProcessingWebSocket(tornado.websocket.WebSocketHandler):
    status = "await"

    # to host client information
    observer_client_list = []
    publisher_client_list = []

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        # check the code
        code = self.get_cookie('code', '')
        if code != '':
            # it is a observer client
            self.observer_client_list.append(self)
        else:
            self.publisher_client_list.append(self)
        print("recv code token:", code)

        return super().open(*args, **kwargs)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        # check the type
        if self in self.publisher_client_list:
            # parse the message that recieved
            request_timestamp = datetime.now().timestamp()
            try:
                json_data: json = json.loads(message)
                # need to convert the array
                predict_result = "void"
                if json_data["status"] != "end":
                    signal_array = np.array(json_data["signal_list"])
                    signal_array_transpose = np.transpose(signal_array, (1, 0))
                    print(signal_array.shape)
                    signal_data: SignalData = SignalData(json_data["record_end_timestamp"],
                                                         json_data["sample_frequency"],
                                                         json_data["sample_duration"], signal_array_transpose.tolist(),
                                                         json_data["status"])
                    # we shall predict it here
                    pred_signal = np.expand_dims(signal_array, axis=0)
                    SKIP_NUMBER = int(signal_data.sample_frequency // 1000)
                    SKIP_NUMBER = 1
                    signal_data.signal_list = signal_array_transpose[:,::SKIP_NUMBER].tolist()
                    print(pred_signal.shape)
                    res = model.predict(pred_signal[:, ::SKIP_NUMBER, :])
                    first_pred_result = res[0]
                    pred_index = np.argmax(first_pred_result, axis=0)
                    predict_result = DRILL_STAGE_NAME[pred_index]
                    print("Pred res", res, pred_index, pred_index)
                    # if pred_index % 2 == 0:
                    #     # trigger arduino
                    #     ser.write("o".encode())
                    # else:
                    #     ser.write("c".encode())
                    process_timestamp = datetime.now().timestamp()
                    record_timestamp = json_data["record_end_timestamp"]
                    print("Transmission delay %d ms, Processing delay %d ms"%(request_timestamp - record_timestamp, process_timestamp -record_timestamp))


                else:
                    signal_data: SignalData = SignalData(json_data["record_end_timestamp"],
                                                         json_data["sample_frequency"],
                                                         json_data["sample_duration"], [],
                                                         json_data["status"])

                # then sent it to json

                # the client which sends signal to websocket server
                ## processing the json data
                sent_data = signal_data.__dict__
                sent_data["predict_result"] = predict_result
                sent_message: str = json.dumps(sent_data)

                for client in self.observer_client_list:
                    client.write_message(sent_message)
                for client in self.publisher_client_list:
                    client.write_message(sent_message)
            except Exception as e:
                print("NOT A VALID POST")
                traceback.print_exc()
        elif self in self.observer_client_list:
            # the observer part
            pass
        # return super().on_message(message)

    def on_close(self) -> None:
        if self in self.observer_client_list:
            self.observer_client_list.remove(self)
        if self in self.publisher_client_list:
            self.publisher_client_list.remove(self)
        return super().on_close()

class BinaryDataInferenceWebSocket(tornado.websocket.WebSocketHandler):
    status = "await"

    # to host client information
    observer_client_list = []
    publisher_client_list = []

    def open(self, *args: str, **kwargs: str) -> Optional[Awaitable[None]]:
        # check the code
        code = self.get_cookie('code', '')
        if code != '':
            # it is a observer client
            self.observer_client_list.append(self)
        else:
            self.publisher_client_list.append(self)
        print("recv code token:", code)

        return super().open(*args, **kwargs)

    def on_message(self, message: Union[str, bytes]) -> Optional[Awaitable[None]]:
        # check the type
        if self in self.publisher_client_list:
            # parse the message that recieved
            try:
                json_data: json = json.loads(message)
                # need to convert the array
                predict_result = "void"
                if json_data["status"] != "end":
                    signal_array = np.array(json_data["signal_list"])
                    signal_array_transpose = np.transpose(signal_array, (1, 0))
                    print(signal_array.shape)
                    signal_data: SignalData = SignalData(json_data["record_end_timestamp"],
                                                         json_data["sample_frequency"],
                                                         json_data["sample_duration"], signal_array_transpose.tolist(),
                                                         json_data["status"])
                    # we shall predict it here
                    pred_signal = np.expand_dims(signal_array, axis=0)
                    SKIP_NUMBER = int(signal_data.sample_frequency // 1000)
                    SKIP_NUMBER = 1
                    signal_data.signal_list = signal_array_transpose[:,::SKIP_NUMBER].tolist()
                    # print(pred_signal.shape)
                    res = model.predict(pred_signal[:, ::SKIP_NUMBER, :])
                    first_pred_result = res[0]
                    pred_index = np.argmax(first_pred_result, axis=0)
                    predict_result = DRILL_STAGE_NAME[pred_index]
                    print("Pred res", res, pred_index, pred_index)
                    # if pred_index % 2 == 0:
                    #     # trigger arduino
                    #     ser.write("o".encode())
                    # else:
                    #     ser.write("c".encode())


                else:
                    signal_data: SignalData = SignalData(json_data["record_end_timestamp"],
                                                         json_data["sample_frequency"],
                                                         json_data["sample_duration"], [],
                                                         json_data["status"])

                # then sent it to json

                # the client which sends signal to websocket server
                ## processing the json data
                sent_data = signal_data.__dict__
                sent_data["predict_result"] = predict_result
                sent_message: str = json.dumps(sent_data)

                for client in self.observer_client_list:
                    client.write_message(sent_message)
                for client in self.publisher_client_list:
                    client.write_message(sent_message)

            except Exception as e:
                print("NOT A VALID POST")
                traceback.print_exc()
        elif self in self.observer_client_list:
            # the observer part
            pass
        # return super().on_message(message)

    def on_close(self) -> None:
        if self in self.observer_client_list:
            self.observer_client_list.remove(self)
        if self in self.publisher_client_list:
            self.publisher_client_list.remove(self)
        return super().on_close()


class TornadoApp(tornado.web.Application):

    def __init__(self) -> None:
        handlers = [
            (r"/", MainHandler),
            (r"/monitor", IdentificationProcessingHandler),
            (r"/live", ProcessingWebSocket),
            (r"/static/(.*)", tornado.web.StaticFileHandler, {"path": "/static"}),
        ]

        settings = {
            'template_path': "template",
            "static_path": os.path.join(os.path.dirname(__file__), "static"),
            'debug': True,
            'autoreload': True
        }
        super().__init__(handlers, **settings)


async def main():
    app = TornadoApp()
    app.listen(8888)
    tornado.autoreload.start()
    for dir, _, files in os.walk('template'):
        [tornado.autoreload.watch(dir + '/' + f) for f in files if not f.startswith('.')]
    print("The server is now running.")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())