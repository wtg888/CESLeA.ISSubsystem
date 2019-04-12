import threading
import contextlib
import keyboard
import pyaudio
import wave
from time import gmtime, strftime, sleep
import os
import sys
from data_split.vad_on_splited_data import preprocess


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
        write_wave(self.filename, b''.join(self.voiced_frames))
        preprocess(self.filename)


    def join(self, timeout=None):
        self._stopevent.set()
        threading.Thread.join(self, timeout)


def get_yn(msg):
    inp = input(msg + '(y/n): ')
    if inp not in ['y', 'n', 'Y', 'N']:
        inp = input(msg + '(y/n): ')
    inp = inp.lower()
    return inp


def register(name):
    if not os.path.isdir('../speaker_recog/textind/train/%s' % name):
        os.mkdir('../speaker_recog/textind/train/%s' % name)
    if not os.path.isdir('../speaker_recog/textind/test/%s' % name):
        os.mkdir('../speaker_recog/textind/test/%s' % name)


if __name__ == '__main__':
    name = input("이니셜을 입력하세요: ")
    register(name)

    idx = 0
    t = strftime("%Y_%m_%d_%H_%M_%S", gmtime())
    while idx < 20:
        keyboard.wait('space')
        rt = RecordingThread(filename='../speaker_recog/train/%s/%s_%02d.wav' %(name, t, idx))
        rt.start()
        keyboard.wait('space')
        rt.join()
        idx = idx + 1

