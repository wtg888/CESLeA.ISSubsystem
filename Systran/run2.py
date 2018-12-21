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
from requests_fn import asr


On = True
q = queue.Queue()


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
                if On and len(ring_buffer) == ring_buffer.maxlen and num_voiced > 0.8 * ring_buffer.maxlen:
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
                    now = int(time.time())
                    data = b''.join([f for f in voiced_frames])
                    q.put_nowait((now, data))
                    print('save %d.wav' % num)
                    fn = 'wavfile/%d.wav'%num
                    write_wave(fn, data, sample_rate)
                    now = int(time.time())
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass


def speaker_recog_thread():
    global d
    while True:
        try:
            g = q.get()
            now, data = g
            now_s = str(now)
            out = asr(data)
            # print(out)
        except queue.Empty:
            continue


def main():
    RATE = 8000
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
                    frames_per_buffer=CHUNK)

    vad = webrtcvad.Vad(2)  # 0~3   3: the most aggressive

    t1 = threading.Thread(target=vad_thread, args=(RATE, frame_duration_ms, 300, vad, stream))
    t2 = threading.Thread(target=speaker_recog_thread)
    t1.daemon = True
    t2.daemon = True
    t1.start()
    t2.start()

    try:
        while True:
            time.sleep(24 * 60 * 60)
    except:
        print("interupt")
    finally:
        stream.stop_stream()
        stream.close()
        p.terminate()


if __name__ == '__main__':
    main()