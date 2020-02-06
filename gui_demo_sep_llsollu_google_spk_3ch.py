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
from post import post_speaker_recog

On = True
stream1 = queue.Queue()
speechQ1 = queue.Queue()

stream2 = queue.Queue()
speechQ2 = queue.Queue()

count = 0


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
            # print(L)
            b1 += struct.pack('h', L)
            b2 += struct.pack('h', C)
            bO += struct.pack('h', int((oL+ oR + oC)/3))
            if len(b1) == 2 * chunk:
                stream1.put((b1, bO))
                stream2.put((b2, bO))
                b1 = b''
                b2 = b''
                bO = b''
    except:
        os._exit(1)


def vad_thread1(sample_rate, frame_duration_ms, padding_duration_ms, vad):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    while True:
        frame = stream1.get()
        is_speech = vad.is_speech(frame[0], sample_rate)
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
                sep_data = b''.join([f[0] for f in voiced_frames])
                o_data = b''.join([f[1] for f in voiced_frames])
                fn = 'wavfile1\\%d.wav'%num
                write_wave(fn, sep_data, sample_rate)
                write_wave(fn.replace('wavfile', 'ori_wavfile'), o_data, sample_rate)
                print('save %d.wav' % num)
                now = int(time.time())
                speechQ1.put_nowait((now, fn, sep_data))
                num = num + 1
                triggered = False
                ring_buffer.clear()
                voiced_frames = []


def asr_thread1(outLabel):
    while True:
        try:
            g = speechQ1.get()
            now, file_name, data = g
            now_s = str(now)

            spk = post_speaker_recog(file_name.replace('wavfile', 'ori_wavfile'))

            google_ans = google_stt(file_name)
            D = np.frombuffer(data, dtype=np.int16)
            data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            llsollu_ans = asr(data)
            # if google_ans or systran_ans:
            if llsollu_ans or google_ans:
                outLabel.config(text="Speaker : " + spk + '\r\n' + "Google : " + google_ans + '\r\n' + "엘솔루 : " + llsollu_ans)
            else:
                print("empty")
        except queue.Empty:
            continue


def vad_thread2(sample_rate, frame_duration_ms, padding_duration_ms, vad):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    while True:
        frame = stream2.get()
        is_speech = vad.is_speech(frame[0], sample_rate)
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
                sep_data = b''.join([f[0] for f in voiced_frames])
                o_data = b''.join([f[1] for f in voiced_frames])
                fn = 'wavfile2\\%d.wav'%num
                write_wave(fn, sep_data, sample_rate)
                write_wave(fn.replace('wavfile', 'ori_wavfile'), o_data, sample_rate)
                print('save %d.wav' % num)
                now = int(time.time())
                speechQ2.put_nowait((now, fn, sep_data))
                num = num + 1
                triggered = False
                ring_buffer.clear()
                voiced_frames = []


def asr_thread2(outLabel):
    while True:
        try:
            g = speechQ2.get()
            now, file_name, data = g
            now_s = str(now)

            spk = post_speaker_recog(file_name.replace('wavfile', 'ori_wavfile'))

            google_ans = google_stt(file_name)
            D = np.frombuffer(data, dtype=np.int16)
            data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            llsollu_ans = asr(data)
            # if google_ans or systran_ans:
            if llsollu_ans or google_ans:
                outLabel.config(text="Speaker : " + spk + '\r\n' + "Google : " + google_ans + '\r\n' + "엘솔루 : " + llsollu_ans)
            else:
                print("empty")
        except queue.Empty:
            continue


def main():
    RATE = 16000
    frame_duration_ms = 30
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    if not os.path.isdir('wavfile1'):
        os.mkdir('wavfile1')

    if not os.path.isdir('ori_wavfile1'):
        os.mkdir('ori_wavfile1')

    vad = webrtcvad.Vad(3)  # 0~3   3: the most aggressive

    root = Tk()
    root.geometry("1500x1000")
    root.title('Result')

    lbl1 = Label(root, text="")
    lbl1.config()
    lbl1.config(width=50)
    lbl1.config(font=("Courier", 44))
    lbl1.place(relx=0.5, rely=0.25, anchor=CENTER)

    lbl2 = Label(root, text="")
    lbl2.config()
    lbl2.config(width=50)
    lbl2.config(font=("Courier", 44))
    lbl2.place(relx=0.5, rely=0.75, anchor=CENTER)

    ths = list()
    ths.append(threading.Thread(target=receive_thread, args=(CHUNK, )))
    ths.append(threading.Thread(target=vad_thread1, args=(RATE, frame_duration_ms, 300, vad)))
    ths.append(threading.Thread(target=asr_thread1, args=(lbl1,)))
    ths.append(threading.Thread(target=vad_thread2, args=(RATE, frame_duration_ms, 300, vad)))
    ths.append(threading.Thread(target=asr_thread2, args=(lbl2,)))
    for th in ths:
        th.daemon = True
        th.start()

    root.mainloop()


if __name__ == '__main__':
    main()
