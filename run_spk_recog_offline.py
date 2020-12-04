# -*- coding: utf-8 -*-
import time
import os
import collections
import contextlib
import wave
import numpy as np
import speaker_recog_final


def write_wave(path, audio, sample_rate=16000):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def read_wave(path):
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (16000, )
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


def speaker_recog(path):
    pcm = read_wave(path)[0]
    write_wave(os.path.join(speaker_recog_final.DATA_DIR, 'test', 'test.wav'), pcm)
    speaker = speaker_recog_final.test_speaker_recog()
    return speaker


def main():
    results = []
    data = os.path.join(speaker_recog_final.DATA_DIR, 'test_offline')
    for d in os.listdir(data):
        for f in os.listdir(os.path.join(data, d)):
            res = speaker_recog(os.path.join(data, d, f))
            results.append(d == res)
    print('offline accuracy', np.mean(results)*100, '%%')


if __name__ == '__main__':
    main()
