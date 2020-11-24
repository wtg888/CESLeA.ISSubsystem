import contextlib
import wave
import os
import random
import struct
import numpy as np

sample_rate = 16000


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


def get_energy(path):
    pcm, _ = read_wave(path)
    arr = 1.0 * np.frombuffer(pcm, dtype=np.int16) / (32767. / 2)
    print(arr)
    energy = np.mean(arr ** 2)
    print(energy)


if __name__ == '__main__':
    get_energy('/home/mi/PycharmProjects/CESLeA/300wav_upsample/test_offline/adult_m/MOGS01166.wav')
