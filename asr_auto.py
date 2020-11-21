import websocket
try:
    import thread
except ImportError:
    import _thread as thread
import time
import json
import pyaudio
import struct


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
    stream.stop_stream()
    stream.close()


def on_close(ws):
    print("onclose")
    stream.stop_stream()
    stream.close()


def on_open(ws):
    global recoord
    global stream
    recoord = True
    ws.send(asrRequestOption)
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    def run(*args):
        while recoord:
            for i in range(3):
                frame = stream.read(CHUNK)
                ws.send(struct.pack('b', 0) + frame)

    thread.start_new_thread(run, ())


if __name__ == "__main__":
    # websocket.enableTrace(True)
    ws = websocket.WebSocketApp("wss://asrdemo.llsollu.com/asr/recognition/websocket/",
                              on_message = on_message,
                              on_error = on_error,
                              on_close = on_close)
    ws.on_open = on_open
    ws.run_forever()
