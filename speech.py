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
from googletest import google_stt
import post

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

def asr(filename):
    return google_stt(filename)


def runAsr():
    while True:
        try:
            g = q.get(timeout=30)
            now_s, file_name = g
            speech = asr(file_name)
            if speech:
                q2.put((now_s, file_name, speech))
        except queue.Empty:
            continue

def doSpeakerRecog(filename):
    os.system('sox-14.4.2-win32\\sox-14.4.2\\sox.exe %s -r 8000 %s'%(filename, filename.replace('wav16k','wav')))
    filename = filename.replace('wav16k','wav')
    f = open("speaker_recog\\a.txt", "w")
    f.write("N1 .\\%s"%filename.split("\\")[-1])
    f.close()
    os.system("cd speaker_recog && hmml\\mfcc.exe -f ceslea_data\\mm.list a.txt wav && cd ..")
    spk_num = -1
    with open('speaker_recog\\spk_result.txt','r') as f:
        spk_num = int(f.readline())
    return spk_num

def runSpeakerRecog():
    fr = open("log.txt", "ab", 0)
    d = {"-1":"N", "0":"ami", "1":"den", "2":"jan", "3":"jun", "4":"lee", "5":"lim", "6":"moh","7":"nas","8":"pro","9":"son","10":"woo","11":"you"}
    while True:
        try:
            g = q2.get(timeout=30)
            now, file_name, speech = g
            now_s = str(now)
            speaker = -1
            if (speech in l) or (2 < len(speech) < 7 and ( speech.endswith("리아") or speech.endswith("이야") or speech.endswith(" 야") or speech.endswith("리야"))):
                speaker = doSpeakerRecog(file_name)
                speech = '세실리아'
            fr.write((now_s + "\t"+ str(speaker) + '\t' + speech + "\r\n").encode())
            print(now_s + "\t"+ str(speaker) + '\t' + speech + "\r\n")
            post.post(createdAt=now, speaker=d[str(speaker)], speakerId=str(speaker), content=speech)
        except queue.Empty:
            continue
    fr.close()


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def vad_(sample_rate, frame_duration_ms,
                  padding_duration_ms, vad, stream):
    num_padding_frames = int(padding_duration_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    num = 0
    voiced_frames = []
    try:
        while True:
            #frame 읽어옴
            frame = stream.read(CHUNK)
            is_speech = vad.is_speech(frame, sample_rate)
            #sys.stdout.write('1' if is_speech else '0')
            if not triggered:
                ring_buffer.append((frame, is_speech))
                num_voiced = len([f for f, speech in ring_buffer if speech])
                #queue의 80%이상이 voice이면 트리거
                if num_voiced > 0.8 * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                #트리거 중이면 읽은 프레임 추가
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                #unvoice가 큐의 60% 이하가 되면 파일 저장
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.6 * ring_buffer.maxlen:
                    triggered = False
                    print('save %d.wav'%num)
                    data = b''.join([f for f in voiced_frames])
                    write_wave('speaker_recog\\wav16k\\%d.wav'%num, data, sample_rate)
                    #downsample('speaker_recog\\wav16k\\%d.wav'%num, 'speaker_recog\\wav\\%d.wav'%num)
                    now = int(time.time())
                    q.put_nowait((now,'speaker_recog\\wav16k\\%d.wav'%num))
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass

def postres():
    
    pass

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
                input_device_index=3,
                frames_per_buffer=CHUNK)
vad = webrtcvad.Vad(3) # 0~3   3: the most aggressive
t1 = threading.Thread(target=vad_, args=(RATE, frame_duration_ms, 450, vad, stream))
t2 = threading.Thread(target=runAsr)
t3 = threading.Thread(target=runSpeakerRecog)
t1.daemon = True
t2.daemon = True
t3.daemon = True
t1.start()
t2.start()
t3.start()
try:
    while True:
        time.sleep(24*60*60)
except:
    print("interupt")
    stream.stop_stream()
    stream.close()
    p.terminate()