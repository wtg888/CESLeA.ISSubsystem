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

On = True
speechQ = queue.Queue()
count = 0


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def vad_thread(sample_rate, frame_duration_ms, padding_duration_ms, vad, stream):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    chunk = int(sample_rate * (frame_duration_ms / 1000.0))
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    while True:
        frame = stream.read(chunk)
        is_speech = vad.is_speech(frame, sample_rate)
        if not triggered:
            ring_buffer.append((frame, is_speech))
            num_voiced = len([f for f, speech in ring_buffer if speech])
            if len(ring_buffer) == ring_buffer.maxlen and num_voiced > 0.9 * ring_buffer.maxlen:
                print('on')
                triggered = True
                for f, s in ring_buffer:
                    voiced_frames.append(f)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append((frame, is_speech))
            num_unvoiced = len([f for f, speech in ring_buffer if not speech])
            if len(ring_buffer) == ring_buffer.maxlen and num_unvoiced > 0.9 * ring_buffer.maxlen:
                print('off')
                data = b''.join([f for f in voiced_frames])
                fn = 'wavfile\\%d.wav'%num
                write_wave(fn, data, sample_rate)
                print('save %d.wav' % num)
                now = int(time.time())
                speechQ.put_nowait((now, fn, data))
                num = num + 1
                triggered = False
                ring_buffer.clear()
                voiced_frames = []


def asr_thread(outLabel):
    while True:
        try:
            g = speechQ.get()
            now, file_name, data = g
            now_s = str(now)

            google_ans = google_stt(file_name)
            # D = np.frombuffer(data, dtype=np.int16)
            # data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            # systran_ans = asr(data)
            # if google_ans or systran_ans:
            if google_ans:
                # outLabel.config(text="Google : " + google_ans + '\r\n' + "엘솔루 : " + systran_ans)
                outLabel.config(text="Google : " + google_ans)
            else:
                print("empty")
            # On = True
            #     on -= 1
                # outLabel.config(text=speaker + ': ' + out)
                # print(speaker, out)
        except queue.Empty:
            continue


def main():
    RATE = 16000
    frame_duration_ms = 30
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    if not os.path.isdir('wavfile'):
        os.mkdir('wavfile')

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    input_device_index=1,
                    frames_per_buffer=CHUNK)

    vad = webrtcvad.Vad(3)  # 0~3   3: the most aggressive

    root = Tk()
    root.geometry("1500x500")
    root.title('Result')

    lbl = Label(root, text="")
    lbl.config()
    lbl.config(width=50)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    ths = list()
    ths.append(threading.Thread(target=vad_thread, args=(RATE, frame_duration_ms, 300, vad, stream)))
    ths.append(threading.Thread(target=asr_thread, args=(lbl,)))
    for th in ths:
        th.daemon = True
        th.start()

    root.mainloop()


if __name__ == '__main__':
    main()
