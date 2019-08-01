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
import librosa

from googletest import google_stt

from speaker_recog.predict_speaker_recog import predict_speaker
from Systran.requests_fn import asr

On = True
q = queue.Queue()

target_speakers = ['SEUNGTAE', 'GILJIN', 'kst', 'ohj']


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


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
                    print('save %d.wav'%num)
                    data = b''.join([f for f in voiced_frames])
                    fn = 'C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile\\%d.wav'%num
                    write_wave(fn, data, sample_rate)
                    now = int(time.time())
                    q.put_nowait((now, fn, data))
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
                    # On = False
    except:
        pass


def speaker_recog_thread(outLabel):
    global d
    global On
    while True:
        try:
            g = q.get()
            now, file_name, data = g
            now_s = str(now)
            # if not on:
            #     _, speaker = predict_speaker(file_name)
            #     outLabel.config(text=speaker)
            #     print(now_s, speaker)
            #     if speaker in target_speakers:
            #         on = 1
            # else:

            google_ans = google_stt(file_name)

            D = np.frombuffer(data, dtype=np.int16)
            data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
            systran_ans = asr(data)
            if google_ans or systran_ans:
                outLabel.config(text="Google : " + google_ans + '\r\n' + "엘솔루 : " + systran_ans)
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

    if not os.path.isdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile'):
        os.mkdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\wavfile')

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    vad = webrtcvad.Vad(2)  # 0~3   3: the most aggressive

    root = Tk()
    root.geometry("1500x500")
    root.title('Result')
    lbl = Label(root, text="")
    lbl.config()
    lbl.config(width=50)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    t1 = threading.Thread(target=vad_thread, args=(RATE, frame_duration_ms, 600, vad, stream))
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
