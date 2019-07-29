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
import numpy as np
import shutil

from Systran.requests_fn import asr
from googletest import synthesize_text, google_stt
import post

On = True
q = queue.Queue()
q2 = queue.Queue()

f = open("CESLeA.txt", 'r', encoding='UTF8')
CESLeA = f.readlines()
f.close()
CESLeA = [x.replace('\r', "").replace('\n', '') for x in CESLeA]


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def vad_thread(sample_rate, frame_duration_ms, padding_duration_ms, vad, stream):
    global On
    print(On, "ON")
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
                    # print('save %d.wav'%num)
                    data = b''.join([f for f in voiced_frames])

                    fn = 'C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\CESLeA-ISS\\wavfile\\%d.wav'%num
                    write_wave(fn, data, sample_rate)

                    now = int(time.time())
                    q.put_nowait((now, fn, data))
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass


def predict_speaker(file_name):
    shutil.copy(src=file_name, dst='C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\공유폴더\\test.wav')
    while not 'speaker_kr.txt' in os.listdir('C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\공유폴더'):
        time.sleep(0.1)
    time.sleep(0.05)
    with open('C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\공유폴더\\speaker_kr.txt','r') as f:
        spk = str(f.readline())
    os.remove('C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\공유폴더\\speaker_kr.txt')
    spk = spk.replace("\n", "")
    return spk, spk


def asr_thread():
    global d
    while True:
        try:
            g = q2.get()
            now, file_name, data, speaker = g

            speech = google_stt(file_name)
            if speech:
                if speech in CESLeA:
                    speech = "CESLeA"
                print(speaker, speech)
                post.post(createdAt=now, speaker=speaker, speakerId=speaker, content=speech)
            else:
                print("empty")
        except queue.Empty:
            continue


def speaker_recog_thread():
    global d
    on = 0
    while True:
        try:
            g = q.get()
            now, file_name, data = g
            now_s = str(now)
            _, speaker = predict_speaker(file_name)
            print(now_s, speaker)
            q2.put_nowait((now, file_name, data, speaker))
        except queue.Empty:
            continue


from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/tts', methods=['POST'])
def tts():
    global On
    if request.method == 'POST':
        text = request.form['text']
        if len(text) == 0:
            return '텍스트를 제대로 입력하지 않았습니다.'
        On = False
        print(text)
        synthesize_text(text, 'ko-KR') # 'en-US'
        time.sleep(0.1)
        On = True
        return 'OK'
    else:
        return '잘못된 접근입니다.'



def main():
    RATE = 16000
    frame_duration_ms = 30
    CHUNK = int(RATE * (frame_duration_ms / 1000.0))
    FORMAT = pyaudio.paInt16
    CHANNELS = 1

    if not os.path.isdir('C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\CESLeA-ISS\\wavfile'):
        os.mkdir('C:\\Users\\kon72\\OneDrive\\바탕 화면\\VM\\CESLeA-ISS\\wavfile')

    p = pyaudio.PyAudio()

    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)

    vad = webrtcvad.Vad(3)  # 0~3   3: the most aggressive


    ths = []
    ths.append(threading.Thread(target=vad_thread, args=(RATE, frame_duration_ms, 300, vad, stream)))
    ths.append(threading.Thread(target=speaker_recog_thread))
    for i in range(4):
        ths.append(threading.Thread(target=asr_thread))

    for th in ths:
        th.daemon = True
    for th in ths:
        th.start()

    app.run(host='0.0.0.0', port=5000)

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
