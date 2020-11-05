import threading
import contextlib
import keyboard
import pyaudio
import wave
from time import gmtime, strftime, sleep
import os
import sys
import datetime
from tkinter import *

os.chdir('..')

from data_split.vad_on_splited_data import preprocess
import speaker_recog_v2


CHUNK = 2048
sample_rate = 16000
i = 0

def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


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


def command(id, root, bt, lbl, button, thread):
    global i
    if thread:
        th = thread.pop()
        th.join()
        bt.set("start")
        if i == 10:
            button.config(state='disable')
            speaker_recog_v2.train_model()
            root.quit()
            root.destroy()
    else:
        rt = RecordingThread(filename=os.path.join(speaker_recog_v2.DATA_DIR, id, get_time() + '_%d.wav' % i))
        rt.start()
        i = i + 1
        lbl.config(text="%2d/%2d" % (i,10))
        bt.set("stop")
        thread.append(rt)


def get_yn(msg):
    inp = input(msg + '(y/n): ')
    if inp not in ['y', 'n', 'Y', 'N']:
        inp = input(msg + '(y/n): ')
    inp = inp.lower()
    return inp


def get_time():
    time_format = '%Y_%m_%d_%H_%M_%S'
    now = datetime.datetime.now()
    return now.strftime(time_format)


if __name__ == '__main__':
    speaker_recog_v2.load_speaker_list()
    name = input("이니셜을 입력하세요: ")
    if name in speaker_recog_v2.speaker_dict.keys():
        inp = get_yn("이미 등록된 화자입니다. 추가로 데이터를 녹음하시겠습니까?")
        if inp == 'n':
            sys.exit(1)
    else:
        inp = get_yn("화자 리스트에 존재하지 않는 이름입니다. 등록하시겠습니까?")
        if inp == 'n':
            sys.exit(1)
        else:
            speaker_recog_v2.add_speaker(name)
    root = Tk()
    root.geometry("200x200")
    root.title('Result')
    lbl = Label(root, text="%2d/%2d" % (0,10))
    lbl.config()
    lbl.config(width=10)
    lbl.config(font=("Courier", 44))
    lbl.place(relx=0.5, rely=0.5, anchor=CENTER)

    btn_text = StringVar()
    button = Button(root, overrelief="solid", width=10, repeatdelay=0, repeatinterval=100, textvar=btn_text)
    btn_text.set("start")
    thread = []
    button.place(relx=0.5, rely=1.0, anchor='s')
    button.config(command=lambda: command(speaker_recog_v2.speaker_dict[name], root, btn_text, lbl, button, thread))

    try:
        root.mainloop()
    except:
        speaker_recog_v2.train_model()
