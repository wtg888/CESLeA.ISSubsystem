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

RATE = 8000 #sampling rate
frame_duration_ms = 30 #30ms마다 분석
CHUNK = int(RATE * (frame_duration_ms / 1000.0))
FORMAT = pyaudio.paInt16 #16bit
CHANNELS = 1 #mono
p = pyaudio.PyAudio()
q = queue.Queue()
q2 = queue.Queue()
def asr(filename):
    """
    http://curl.haxx.se/libcurl/c/curl_easy_setopt.html
    http://code.activestate.com/recipes/576422-python-http-post-binary-file-upload-with-pycurl/
    http://pycurl.cvs.sourceforge.net/pycurl/pycurl/tests/test_post2.py?view=markup
    """
    url = 'http://127.0.0.1:7777/filemode/?productcode=DEMO&transactionid=0&language=kor'
    c = pycurl.Curl()
    #c.setopt(pycurl.VERBOSE, 1)
    c.setopt(pycurl.URL, url)
    fout = io.BytesIO()
    c.setopt(pycurl.WRITEFUNCTION, fout.write)

    c.setopt(c.HTTPPOST, [
                ("uploadfieldname",
                 (c.FORM_FILE, filename,
                  c.FORM_CONTENTTYPE, "audio/wav"))])
    c.perform()
    response_code = c.getinfo(pycurl.RESPONSE_CODE)
    if response_code == 200 :
        response_data = fout.getvalue().decode('UTF-8')
        res = json.loads(response_data, encoding='UTF-8')
        if res['rcode'] <= 0:
            out = 'fail'
        else:
            out = res['result']
    else:
        out = 'fail'
    c.close()
    return out


def runAsr():
    while True:
        try:
            g = q.get(timeout=30)
            now_s, file_name = g
            speech = asr(file_name)
            q2.put((now_s, file_name, speech))
        except queue.Empty:
            continue

def doSpeakerRecog(filename):
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
    while True:
        try:
            g = q2.get(timeout=30)
            now_s, file_name, speech = g
            speaker = -1
            if 2 < len(speech) < 7 and ( speech.endswith("리아") or speech.endswith("이야") or speech.endswith(" 야") or speech.endswith("리야")):
                speaker = doSpeakerRecog(file_name)
            fr.write((now_s + "\t"+ str(speaker) + '\t' + speech + "\r\n").encode())
            print(now_s + "\t"+ str(speaker) + '\t' + speech + "\r\n")
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
                #queue의 90%이상이 voice이면 트리거
                if num_voiced > 0.6 * ring_buffer.maxlen:
                    triggered = True
                    for f, s in ring_buffer:
                        voiced_frames.append(f)
                    ring_buffer.clear()
            else:
                #트리거 중이면 읽은 프레임 추가
                voiced_frames.append(frame)
                ring_buffer.append((frame, is_speech))
                #unvoice가 큐의 90% 이상이 되면 파일 저장
                num_unvoiced = len([f for f, speech in ring_buffer if not speech])
                if num_unvoiced > 0.6 * ring_buffer.maxlen:
                    triggered = False
                    print('save %d.wav'%num)
                    write_wave('speaker_recog\\wav\\%d.wav'%num, b''.join([f for f in voiced_frames]), RATE)
                    now = time.localtime()
                    now_s = "%04d_%02d_%02d_%02d_%02d_%02d" % (now.tm_year, now.tm_mon, now.tm_mday, now.tm_hour, now.tm_min, now.tm_sec)
                    q.put_nowait((now_s,'speaker_recog\\wav\\%d.wav'%num))
                    num = num + 1
                    ring_buffer.clear()
                    voiced_frames = []
    except:
        pass

stream = p.open(format=FORMAT,
                channels=CHANNELS,
                rate=RATE,
                input=True,
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