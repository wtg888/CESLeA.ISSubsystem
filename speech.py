#-*- coding: utf-8 -*-
import os
import time
import queue
import wave
import threading
import io
import pycurl
import json
import collections
import contextlib
import sys
import wave
import webrtcvad
import pyaudio
import numpy as np
import scipy.signal
from googletest import google_stt, synthesize_text
import post
import shutil

initial2name = {"isy":"LimSoyoung", "jjr":"JoJoungrae", "kdh":"KimDongHyun", 
"kdy":"KwonDoyoung", "kjh":"KimJonghong", "kjs":"KangJunsu", 
"ksm":"KinSeungmin", "pjh":"ParkJonghoon", "rws":"RyuWoosup", 
"yhs":"YouHosang", "yig":"YoonIngyu", "aaa":"KinDohyeong",
"bra":"Braian", "ami":"Amin", "den":"Dennis",
"gwn":"Gwena", "lin":"lin", "who":"who",
"kkh":"KwonKihoon", "kst":"KangSeungtae", "kwh":"kwh",
"sji":"SeoJungin"}

RATE = 16000 #sampling rate
frame_duration_ms = 30 #30ms마다 분석
CHUNK = int(RATE * (frame_duration_ms / 1000.0))
FORMAT = pyaudio.paInt16 #16bit
CHANNELS = 1 #mono
l = ['몇시야', '몇시일 리아', '이제  시리아', '되질 이요', '세시에 내야', '슬슬 이여', '얘 시리아  나요', '제 시리아', '제트 리아', '네  시에는 이요', '몇시에 를요', '에스엘 이요', '제  비비안',
'없애실 이야', '주실 이야', '에스엘 리아', '저 실현 이야', '몇시일 로요', '스튜디오', '몇 cm 이요', '내실 래요', '대신리요', '아  세트 엔이요', '네  쓰여', '저  님이요', '근데 쓰여', '제가 시리아', '지에스 니요', '잭슨은 예', '센스 엔이요', '저  십일 이요', '예  일이야', '뒈질 리아', '지금  시리아', '유리야', '센스 이요', '넷째 일이요', '새 셀 리안', '에스 뭐야', '세실 리아  관계', '네 시리아', '열세 니요', '내 쯤이요', '세시로 예약', '응  지금  제일 이요', '접수를 이야', '씨름 이요', '그게  제일 이요', '내실 이요', '했으니 연', '저  시행을 이요', '세실 리아', '이에스엘 이요', '세트 이요', '저 심리학', '여실 이요', '제시를 약', '사실이야', '이제  씨엘 리아  모를까', '주스 리아', '제트 엔이요', '그랬더니 예', '세 수요일 이야', '넥센 이요', '세시에 를요', '세시에 되요', '매실 이야', '세시로요', '저 시리아', '네  일이요', '쓰리요', '쓸쓸히 약', '네  몇시야', '열심히 이요', '쇼핑몰이 약', '네  신용이요', '얘 시리아', '쓰리 약', '쓸수 엘이요', '이제 시리아', '세실 이야', '몇시에 로요', '저 시에 를요', '쓸수 있는게', '제트 이요', '느낌이 야']
p = pyaudio.PyAudio()
q = queue.Queue()
q2 = queue.Queue()


def makedixt():
    d = {"-1" : "N"}
    f = open("speaker_recog/ceslea_data/map.list", "r")
    l = [x.split(" ") for x in f.read().split('\n') if x]
    for a, b in l:
        d[a] = b
    print(d)
    return d


d = makedixt()

def asr(filename):
    # replace new ASR function
    return google_stt(filename, language_code="en-US")


def runAsr():
    while True:
        try:
            g = q.get()
            now_s, file_name = g
            speech = asr(file_name)
            print('speech : %s'%speech)
            if speech != "":
                q2.put((now_s, file_name, speech))
        except queue.Empty:
            continue

def doSpeakerRecog(filename):
    f = open("speaker_recog\\a.txt", "w")
    f.write("N1 .\\%s"%filename.split("\\")[-1])
    f.close()
    os.system("cd speaker_recog && hmml\\mfcc.exe -f ceslea_data\\mm.list a.txt wav16k && cd ..")
    spk_num = -1
    with open('speaker_recog\\spk_result.txt','r') as f:
        spk_num = int(f.readline())
    return spk_num


def text_ind_speaker_recognition(filename):
    shutil.copy(src=filename, dst='C:\\Users\\knu\\Desktop\\share\\test.wav')
    while not 'speaker_en.txt' in os.listdir('C:\\Users\\knu\\Desktop\\share'):
        time.sleep(0.1)
    time.sleep(0.05)
    with open('C:\\Users\\knu\\Desktop\\share\\speaker_en.txt','r') as f:
        spk = str(f.readline())
    os.remove('C:\\Users\\knu\\Desktop\\share\\speaker_en.txt')
    return spk.replace("\n","")


def runSpeakerRecog():
    global d
    fr = open("log.txt", "ab", 0)
    while True:
        try:
            g = q2.get()
            now, file_name, speech = g
            now_s = str(now)
            post.post(createdAt=now, speaker="User", speakerId="User", content=speech)
        except queue.Empty:
            continue


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

from flask import Flask
from flask import request
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'Hello World!'

@app.route('/tts', methods=['POST']) 
def login(): 
    global On
    if request.method == 'POST': 
        text = request.form['text'] 
        if len(text) == 0: 
            return '텍스트를 제대로 입력하지 않았습니다.' 
        On = False
        print(text)
        synthesize_text(text, 'en-US')
        time.sleep(0.1)
        On = True
        return 'OK' 
    else: 
        return '잘못된 접근입니다.'


if __name__ == '__main__':
    stream = p.open(format=FORMAT,
                    channels=CHANNELS,
                    rate=RATE,
                    input=True,
                    frames_per_buffer=CHUNK)
    vad = webrtcvad.Vad(2) # 0~3   3: the most aggressive
    t1 = threading.Thread(target=vad_, args=(RATE, frame_duration_ms, 700, vad, stream))
    t2 = threading.Thread(target=runAsr)
    t3 = threading.Thread(target=runSpeakerRecog)
    t1.daemon = True
    t2.daemon = True
    t3.daemon = True
    t1.start()
    t2.start()
    t3.start()
    app.run(host='0.0.0.0', port=5000)
    try:
        while True:
            time.sleep(24*60*60)
    except:
        print("interupt")
        stream.stop_stream()
        stream.close()
        p.terminate()