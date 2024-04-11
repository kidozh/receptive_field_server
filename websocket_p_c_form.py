import time
import asyncio
import websockets
import functools
import json
from multiprocessing import Process, Pipe, Queue


async def consumer_handler(websocket, parent_conn):
    while True:
        try:
            message = await websocket.recv()
            print('Consumer',message)
            parent_conn.put(message)
            print("I sent this to the queue: {}".format(message))
        except Exception as e1:
            print("consumer exception was: {}".format(e1))
            break


async def producer_handler(websocket, child_conn2):
    while True:
        message = child_conn2.recv()
        message = json.dumps(message)
        print("Recv message", message)
        try:
            await websocket.send(message)
        except Exception as e1:
            print("producer exception was: {}".format(e1))
            break


async def handler(websocket, path, parent_conn, child_conn2):
    consumer_task = asyncio.ensure_future(consumer_handler(websocket, parent_conn))
    producer_task = asyncio.ensure_future(producer_handler(websocket, child_conn2))
    done, pending = await asyncio.wait(
        [consumer_task, producer_task],
        return_when=asyncio.FIRST_COMPLETED,
    )

    for task in pending:
        task.cancel()


def f(parent_conn):
    print("child_conn f started.")  # Is this thing even on?
    while True:
        stuff = parent_conn.get()
        print("Stuff in fconn is: {}".format(stuff))


def f2(parent_conn, parent_conn2):
    county = 0
    while True:
        time.sleep(2)
        currenttime = round(time.time())
        parent_conn2.send(currenttime)
        if county > 5:  # send something to the consumer once in awhile so we know it's alive
            parent_conn.put(currenttime)
            county = 0
        county += 1


if __name__ == '__main__':
    parent_conn = Queue()
    parent_conn2, child_conn2 = Pipe()
    p = Process(target=f, args=(parent_conn,))
    p.start()
    p2 = Process(target=f2, args=(parent_conn, parent_conn2,))
    p2.start()
    start_server = websockets.serve(
        functools.partial(handler, parent_conn=parent_conn,
                          child_conn2=child_conn2),
        'localhost', 8888)
    asyncio.get_event_loop().run_until_complete(start_server)
    asyncio.get_event_loop().run_forever()

    p.join()
    p2.join()