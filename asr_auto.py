import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import pyaudio


recoord = False

RATE = 8000
CHUNK = 4096
FORMAT = pyaudio.paInt16
CHANNELS = 1
p = pyaudio.PyAudio()
stream = None

asrRequestOption = json.dumps({
    'productcode': "DIGITALW",
    'domain': 'default',
    'cmd': "START",
    'transactionid': "0",
    'language': "kor",
    'epd': True,
    'frmt': "0",
    'slu': False,
    'partial': True,
    'cfl': False
})
print('asrRequestOption', asrRequestOption)


def on_message(ws, message):
    print("event.data:", message)


def on_error(ws, error):
    print(error)


def on_close(ws):
    print("onclose")


def on_open(ws):
    global recoord
    recoord = True
    ws.send(asrRequestOption)
    def run(*args):
        while recoord:
            for i in range(3):
                time.sleep(1)
                ws.send("Hello %d" % i)
            time.sleep(1)
    thread.start_new_thread(run, ())


if __name__ == "__main__":
    pass
    # websocket.enableTrace(True)
    # ws = websocket.WebSocketApp("ws://echo.websocket.org/",
    #                           on_message = on_message,
    #                           on_error = on_error,
    #                           on_close = on_close)
    # ws.on_open = on_open
    # ws.run_forever()
