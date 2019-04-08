import threading
import contextlib
import keyboard
import pyaudio
import wave
from time import gmtime, strftime, sleep
import os
import sys
from data_split.vad_on_splited_data import preprocess
from tkinter import *

CHUNK = 2048
sample_rate = 16000


def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)
    print("save %s"%path)


class RecordingThread(threading.Thread):
    def __init__(self, filename):
        self.p = pyaudio.PyAudio()
        self.stream = self.p.open(format=self.p.get_format_from_width(2),
                                    channels=1,
                                    rate=sample_rate,
                                    input=True,
                                    frames_per_buffer=CHUNK
                                  )
        self.voiced_frames = []
        self.filename = filename

        self._stopevent = threading.Event()
        self._sleepperiod = 1.0
        threading.Thread.__init__(self, name='RecordingThread')

    def run(self):
        print('recording start')
        while not self._stopevent.isSet():
            frame = self.stream.read(CHUNK)
            self.voiced_frames.append(frame)

        self.stream.stop_stream()
        self.stream.close()
        self.p.terminate()
        print('recording end')
        try:
            write_wave(self.filename, b''.join(self.voiced_frames))
            preprocess(self.filename)
            self.isSuccess = True
        except:
            self.isSuccess = False
            print('fail')

    def join(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)


def get_yn(msg):
    inp = input(msg + '(y/n): ')
    if inp not in ['y', 'n', 'Y', 'N']:
        inp = input(msg + '(y/n): ')
    inp = inp.lower()
    return inp


def register(speaker_names, name):
    speaker_names.append(name)
    os.mkdir('../speaker_recog/train/%s' % name)
    os.mkdir('../speaker_recog/test/%s' % name)
    f = open('../speaker_recog/name.list', 'a')
    f.write(name + '\n')
    f.close()


def command(bt, lbl, thread):
    global i
    if thread:
        th = thread.pop()
        th.join()
        if th.isSuccess:
            # _, spk = predict_speaker(th.filename)
            lbl.config(text="")
        bt.set("start")
    else:
        rt = RecordingThread(filename='wavfile/%02d.wav' % i)
        rt.start()
        i = i + 1
        bt.set("stop")
        thread.append(rt)


if __name__ == '__main__':
    f = open('../speaker_recog/name.list', 'r')
    speaker_names = [x for x in f.read().split('\n') if x != '']
    f.close()

    root = Tk()
    root.geometry("200x200")
    root.title('Result')
    lbl = Label(root, text="이름")
    lbl.config()
    lbl.config(width=10)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    btn_text = StringVar()
    button = Button(root, overrelief="solid", width=10, repeatdelay=0, repeatinterval=100, textvar=btn_text)
    btn_text.set("start")
    thread = []
    button.place(relx=0.5, rely=1.0, anchor='s')
    button.config(command=lambda: command(btn_text, lbl, thread))

    try:
        root.mainloop()
    except:
        pass

    name = input("이니셜을 입력하세요: ")
    if name in speaker_names:
        inp = get_yn("이미 등록된 화자입니다. 추가로 데이터를 녹음하시겠습니까?")
        if inp == 'n':
            sys.exit(1)
    else:
        inp = get_yn("화자 리스트에 존재하지 않는 이름입니다. 등록하시겠습니까?")
        if inp == 'n':
            sys.exit(1)
        else:
            register(speaker_names, name)

    idx = 0
    t = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    while idx < 10:
        keyboard.wait('space')
        rt = RecordingThread(filename='../speaker_recog/train/%s/%s_%02d.wav' %(name, t, idx))
        rt.start()
        keyboard.wait('space')
        rt.join()
        idx = idx + 1

