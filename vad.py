#-*- coding: utf-8 -*-
import os
import time
import queue
import threading
import collections
import contextlib
import wave
import webrtcvad
import pyaudio
import shutil

RATE = 16000 #sampling rate
frame_duration_ms = 30 #30ms마다 분석
CHUNK = int(RATE * (frame_duration_ms / 1000.0))
FORMAT = pyaudio.paInt16 #16bit
CHANNELS = 1 #mono
p = pyaudio.PyAudio()
q = queue.Queue()


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


On = True


def vad_(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, stream):
    global On
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    try:
        while True:
            # frame 읽어옴
            frame = stream.read(CHUNK)
            is_speech = vad.is_speech(frame, sample_rate)
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                # queue의 50%이상이 voice이면 트리거
                if On and len(ring_buffer) == ring_buffer.maxlen and num_voiced > 0.5 * ring_buffer.maxlen:
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
                # unvoice가 큐의 90% 이상이 되면 파일 저장
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if len(ring_buffer) == ring_buffer.maxlen and num_unvoiced > 0.9 * ring_buffer.maxlen:
                    triggered = False
                    print('save %d.wav'%num)
                    data = b''.join([f for f in voiced_frames])
                    write_wave('speaker_recog\\wav16k\\%d.wav'%num, data, sample_rate)
                    now = int(time.time())
                    q.put_nowait((now,'speaker_recog\\wav16k\\%d.wav'%num))
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass


if __name__ == '__main__':
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    vad = webrtcvad.Vad(2) # 0~3   3: the most aggressive
    t1 = threading.Thread(target=vad_, args=(RATE, frame_duration_ms, 700, vad, stream))
    t1.daemon = True
    t1.start()
    try:
        while True:
            time.sleep(24*60*60)
    except:
        print("interupt")
        stream.stop_stream()
        stream.close()
        p.terminate()