import contextlib
import wave
import os
import random


sample_rate = 16000


def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def read_wave(path):
    """Reads a .wav file.
    Takes the path, and returns (PCM audio data, sample rate).
    """
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        assert num_channels == 1
        sample_width = wf.getsampwidth()
        assert sample_width == 2
        sample_rate = wf.getframerate()
        assert sample_rate in (sample_rate, )
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


if __name__ == '__main__':
    path = 'temp'
    l = os.listdir(path)
    audio = b''
    for f in l:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('test_spk.wav', audio)
