# -*- coding: utf-8 -*-
import os
os.chdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_')
import queue
import threading
import collections
import contextlib
import wave
import webrtcvad
import pyaudio
import time
import struct
import numpy as np
import librosa
from tkinter import *
from googletest import google_stt
from llsollu.requests_fn import asr
from post import post_age_recog

triggered = False
stream1 = queue.Queue()
speechQ1 = queue.Queue()

count = 0
voiced_frames = []


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def receive_thread(chunk):
    b1 = b''
    b2 = b''
    bO = b''
    try:
        while True:
            L, C, R, oL, oC, oR = map(int, input().split('\t'))
            b1 += struct.pack('h', L)
            b2 += struct.pack('h', R)
            bO += struct.pack('h', int((oL+ oR + oC)/3))
            if len(b1) == 2 * chunk:
                if triggered:
                    voiced_frames.append((b1, b2, bO))
                b1 = b''
                b2 = b''
                bO = b''
    except:
        os._exit(1)


def asr_thread(outLabel):
    i = 0
    while True:
        try:
            i += 1
            b1, b2, bO = speechQ1.get()
            fn1, fn2, fnO = 'wavfile1\\%d.wav'%i, 'wavfile2\\%d.wav'%i, 'ori_wavfile\\%d.wav'%i
            write_wave(fn1, b1, 16000)
            write_wave(fn2, b2, 16000)
            write_wave(fnO, bO, 16000)

            google_ans = google_stt(fnO)

            spk1 = post_age_recog(fn1)
            D = np.frombuffer(b1, dtype=np.int16)
            data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            llsollu_ans1 = asr(data)

            spk2 = post_age_recog(fn1)
            D = np.frombuffer(b2, dtype=np.int16)
            data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            llsollu_ans2 = asr(data)

            outLabel.config(text="Speaker1 : " + spk1 + '\r\n'
                                 + "엘솔루 : " + llsollu_ans1 + '\r\n'
                                 + "Speaker2 : " + spk2 + '\r\n'
                                 + "엘솔루 : " + llsollu_ans2 + '\r\n'
                                 + "Google : " + google_ans)

        except queue.Empty:
            continue


def s_event(event):
    global triggered
    if not triggered:
        print('on')
        triggered = True


def e_event(event):
    global triggered
    global voiced_frames
    if triggered:
        print('off')
        triggered = False
        speechQ1.put_nowait((b''.join([f[0] for f in voiced_frames]),
                            b''.join([f[1] for f in voiced_frames]),
                            b''.join([f[2] for f in voiced_frames])))
        voiced_frames = []


def main():
    RATE = 16000
    frame_duration_ms = 30
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))

    if not os.path.isdir('wavfile1'):
        os.mkdir('wavfile1')

    if not os.path.isdir('ori_wavfile'):
        os.mkdir('ori_wavfile')

    if not os.path.isdir('wavfile2'):
        os.mkdir('wavfile2')

    root = Tk()
    root.geometry("1500x1000")
    root.title('Result')

    lbl = Label(root, text="")
    lbl.config()
    lbl.config(width=50)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    root.bind('s', s_event)
    root.bind('e', e_event)

    ths = list()
    ths.append(threading.Thread(target=receive_thread, args=(CHUNK, )))
    ths.append(threading.Thread(target=asr_thread, args=(lbl,)))
    for th in ths:
        th.daemon = True
        th.start()

    root.mainloop()


if __name__ == '__main__':
    main()
