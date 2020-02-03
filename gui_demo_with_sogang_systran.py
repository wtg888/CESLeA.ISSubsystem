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
import numpy as np
import time
import librosa
import struct

from speaker_recog.predict_speaker_recog import predict_speaker
from llsollu.requests_fn import asr

On = True
q = queue.Queue()
q2 = queue.Queue()
target_speakers = ['kst', 'lsw', 'lms', 'kms']
stream = queue.Queue()
count = 0
f = open('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\speaker_recog/name.list', 'r')
speaker_names = [x for x in f.read().split('\n') if x != '']
f.close()
speaker = ''
spk = {"kms":"김민수", "kst":"강승태", "ojh":"오혜준", "kjh":"김종홍", "kdh":"김동현", "lsw":"이상원"}

target_speakers = speaker_names


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def receive_thread(chunk):
    bL = b''
    # bR = b''
    try:
        while True:
            L, R = map(int, input().split('\t'))
            bL += struct.pack('h', L)
            # bR += struct.pack('h', R)
            if len(bL) == 2 * chunk:
                stream.put(bL)
                bL = b''
                # bR = b''
    except:
        pass


def vad_thread2(sample_rate, frame_duration_ms, padding_duration_ms, vad):
    global On
    global count
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
                    print('on s')
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
                    print('off s')
                    if count > 0:
                        # count -= 1
                        print('save %d.wav'%num)
                        data = b''.join([f for f in voiced_frames])
                        fn = 'C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile2\\%d.wav'%num
                        write_wave(fn, data, sample_rate)
                        now = int(time.time())
                        q2.put_nowait((now, data))
                        num = num + 1
                    triggered = False
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass


def asr_thread(outLabel):
    global speaker
    global count
    while True:
        g = q2.get()
        if count:
            now, data = g
            now_s = str(now)
            if len(data) < 0.5 * 16000 * 2:
                continue
            D = np.frombuffer(data, dtype=np.int16)
            data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            print('run asr')
            out = asr(data)
            if out:
                count = count - 1
                print(out)
                outLabel.config(text=spk[speaker] + ': ' + out)
            else:
                print('out is empty')


def vad_thread(sample_rate, frame_duration_ms, padding_duration_ms, vad, stream):
    global On
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    chunk = int(sample_rate * (frame_duration_ms / 1000.0))
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    try:
        while True:
            frame = stream.read(chunk)
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
                    if count == 0:
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
    global count
    global speaker
    while True:
        try:
            g = q.get()
            now, file_name = g
            now_s = str(now)
            if not count:
                _, speaker = predict_speaker(file_name)
                outLabel.config(text=spk[speaker])
                print(now_s, speaker)
                if speaker in target_speakers:
                    time.sleep(0.4)
                    count = 1
            else:
                pass
        except queue.Empty:
            continue


def main():
    RATE = 16000
    frame_duration_ms = 30
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    if not os.path.isdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile'):
        os.mkdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile')

    if not os.path.isdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile2'):
        os.mkdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile2')

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    vad = webrtcvad.Vad(3)
    vad1 = webrtcvad.Vad(2)

    root = Tk()
    root.geometry("800x800")
    root.title('Result')
    lbl = Label(root, text="이름")
    lbl.config()
    lbl.config(width=30)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    ths = list()
    ths.append(threading.Thread(target=receive_thread, args=(CHUNK, )))
    ths.append(threading.Thread(target=vad_thread, args=(RATE, frame_duration_ms, 300, vad, stream)))
    ths.append(threading.Thread(target=speaker_recog_thread, args=(lbl,)))
    ths.append(threading.Thread(target=vad_thread2, args=(RATE, frame_duration_ms, 500, vad1)))
    ths.append(threading.Thread(target=asr_thread, args=(lbl,)))
    for th in ths:
        th.daemon = True
        th.start()

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