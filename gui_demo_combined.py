# -*- coding: utf-8 -*-
import time
import os
import queue
import threading
import collections
import contextlib
import wave
import webrtcvad
import struct
from tkinter import *

from speaker_recog.predict_speaker_recog import predict_speaker

On = True
q = queue.Queue()
stream = queue.Queue()


def receive_thread(chunk):
    bL = b''
    bR = b''
    try:
        while True:
            L, R = map(int, input().split('\t'))
            bL += struct.pack('h', L)
            bR += struct.pack('h', R)
            if len(bL) == 2 * chunk:
                stream.put(bL)
                bL = b''
                bR = b''
    except:
        pass
    pass


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def vad_thread(sample_rate, frame_duration_ms, padding_duration_ms, vad):
    global On
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    try:
        while True:
            frame = stream.get()
            is_speech = vad.is_speech(frame, sample_rate)
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                if On and len(ring_buffer) == ring_buffer.maxlen and num_voiced > 0.5 * ring_buffer.maxlen:
                    print('on')
                    triggered = True
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                if not On:
                    triggered = False
                    ring_buffer.clear()
                    voiced_frames = []
                    continue
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if len(ring_buffer) == ring_buffer.maxlen and num_unvoiced > 0.5 * ring_buffer.maxlen:
                    print('off')
                    triggered = False
                    print('save %d.wav'%num)
                    data = b''.join([f for f in voiced_frames])
                    fn = 'C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile\\%d.wav'%num
                    write_wave(fn, data, sample_rate)
                    now = int(time.time())
                    q.put_nowait((now, fn))
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass


def speaker_recog_thread(outLabel):
    global d
    while True:
        try:
            g = q.get()
            now, file_name = g
            now_s = str(now)
            _, speaker = predict_speaker(file_name)
            outLabel.config(text=speaker)
            print(now_s, speaker)
        except queue.Empty:
            continue


def main():
    RATE = 16000
    frame_duration_ms = 30
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))
    CHANNELS = 1

    if not os.path.isdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile'):
        os.mkdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile')

    vad = webrtcvad.Vad(3)  # 0~3   3: the most aggressive

    root = Tk()
    root.geometry("200x200")
    root.title('Result')
    lbl = Label(root, text="이름")
    lbl.config()
    lbl.config(width=10)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    t0 = threading.Thread(target=receive_thread, args=(CHUNK, ))
    t1 = threading.Thread(target=vad_thread, args=(RATE, frame_duration_ms, 300, vad))
    t2 = threading.Thread(target=speaker_recog_thread, args=(lbl,))
    t0.daemon = True
    t1.daemon = True
    t2.daemon = True
    t0.start()
    t1.start()
    t2.start()

    try:
        root.mainloop()
    except:
        print("interupt")
    finally:
        pass


if __name__ == '__main__':
    main()
