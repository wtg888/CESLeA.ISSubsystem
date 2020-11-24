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

ON = True
q = queue.Queue()

# URL = 'http://192.168.1.100:8080/spk'
URL = 'http://192.168.1.115:8080/spk'

pre_spk = None

spk_history = collections.deque(maxlen=3)
from collections import Counter


def modefinder(numbers):
    c = Counter(numbers)
    mode = c.most_common(1)
    return mode[0][0]


def post_res(spk):
    try:
        res = requests.post(URL, data={'text': spk})
    except:
        pass


def write_wave(path, audio, sample_rate=16000):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def record_thread(sample_rate, frame_duration_ms, length_ms, inference_ms, stream):
    global ON
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
                    if ON:
                        data = b''.join([f for f in ring_buffer])
                        q.put_nowait(data)
    except:
        pass


def speaker_recog_thread(outLabel, outLabelp):
    global pre_spk
    while True:
        try:
            data = q.get()
            outLabel.config(text='...')
            post_res('%s\n%s'%('...', pre_spk))
            write_wave(os.path.join(age_recog_v2.DATA_DIR, 'test', 'test.wav'), data)
            speaker = age_recog_v2.test_speaker_recog()
            outLabel.config(text=speaker)
            if speaker != '...':
                spk_history.append(speaker)
                spk = modefinder(spk_history)
                post_res('%s\n%s'%(spk, pre_spk))
                print(spk)
                if pre_spk != speaker:
                    pre_spk = speaker
                    outLabelp.config(text=speaker)
        except queue.Empty:
            continue


def command(bt, lbl):
    global ON
    global q
    if ON:
        ON = False
        with q.mutex:
            q.queue.clear()
        with spk_history.mutex:
            spk_history.queue.clear()
        bt.set("start")
    else:
        ON = True
        lbl.config(text='...')
        post_res('%s\n%s' % ('...', pre_spk))
        bt.set("stop")


def main():
    global ON
    age_recog_v2.load_speaker_list()
    RATE = 16000
    frame_duration_ms = 100
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
    root.geometry("400x400")
    root.title('Result')
    lbl = Label(root, text="이름")
    lbl.config()
    lbl.config(width=10)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.33, anchor=CENTER)

    lbl_p = Label(root, text="이름")
    lbl_p.config()
    lbl_p.config(width=10)
    lbl_p.config(font=("Courier", 44))
    lbl_p.place(relx=0.5, rely=0.66, anchor=CENTER)

    btn_text = StringVar()
    button = Button(root, overrelief="solid", width=10, repeatdelay=0, repeatinterval=100, textvar=btn_text)
    btn_text.set("start")
    ON = False
    button.place(relx=0.5, rely=1.0, anchor='s')
    button.config(command=lambda: command(btn_text, lbl))

    t1 = threading.Thread(target=record_thread, args=(RATE, frame_duration_ms, 2000, 1500, stream))
    t2 = threading.Thread(target=speaker_recog_thread, args=(lbl, lbl_p))
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
