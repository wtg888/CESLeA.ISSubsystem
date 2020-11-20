# -*- coding: utf-8 -*-
import time
import os
import queue
import threading
import collections
import contextlib
import wave
import webrtcvad
import pyaudio
from tkinter import *
import shutil

import age_recog_v2 as age_recog_v2
import requests

On = True
q = queue.Queue()

# URL = 'http://192.168.1.100:8080/spk'
URL = 'http://127.0.0.1:8080/spk'


def post_res(spk):
    res = requests.post(URL, data={'text': spk})


def write_wave(path, audio, sample_rate=16000):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def record_thread(sample_rate, frame_duration_ms, length_ms, inference_ms, stream):
    global On
    chunk = int(sample_rate * (frame_duration_ms / 1000.0))
    ring_buffer = collections.deque(maxlen=length_ms // frame_duration_ms)

    num = 0
    try:
        while True:
            frame = stream.read(chunk)
            ring_buffer.append(frame)

            if len(ring_buffer) == ring_buffer.maxlen:
                num += 1
                if num == inference_ms // frame_duration_ms:
                    num = 0
                    data = b''.join([f for f in ring_buffer])
                    q.put_nowait(data)

    except:
        pass


def speaker_recog_thread(outLabel):
    global d
    while True:
        try:
            data = q.get()

            write_wave(os.path.join(age_recog_v2.DATA_DIR, 'test', 'test.wav'), data)
            speaker = age_recog_v2.test_speaker_recog()
            outLabel.config(text=speaker)
            post_res(speaker)
            print(speaker)
        except queue.Empty:
            continue


def main():
    age_recog_v2.load_speaker_list()
    RATE = 16000
    frame_duration_ms = 1000
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1


    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    root = Tk()
    root.geometry("200x200")
    root.title('Result')
    lbl = Label(root, text="이름")
    lbl.config()
    lbl.config(width=10)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    t1 = threading.Thread(target=record_thread, args=(RATE, frame_duration_ms, 5000, 4000, stream))
    t2 = threading.Thread(target=speaker_recog_thread, args=(lbl,))
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    try:
        root.mainloop()
    except:
        print("interupt")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    main()
