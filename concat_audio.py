import contextlib
import wave
import os
import random


sample_rate = 8000


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
    f = open('C:\\Users\\MI\\Dropbox\\엘솔루 dataset\\transcription.txt', 'r', encoding='utf8')
    l = f.readlines()
    f.close()

    path = 'C:\\Users\\MI\\Dropbox\\엘솔루 dataset\\300wav'
    trans = [x.split()[0].split('-')[-1] + '.wav' for x in l if x.startswith('ELD')]
    random.shuffle(trans)

    audio = b''
    for f in trans:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('ELD.wav', audio)

    trans = [x.split()[0].split('-')[-1] + '.wav' for x in l if x.startswith('CHD')]
    random.shuffle(trans)

    audio = b''
    for f in trans:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('CHD.wav', audio)

    trans = [x.split()[0].split('-')[-1] + '.wav' for x in l if x.startswith('M') or x.startswith('F')]
    random.shuffle(trans)

    audio = b''
    for f in trans:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('normal.wav', audio)

    path = 'C:\\Users\\MI\\Dropbox\\엘솔루 dataset\\300wav_noise'
    trans = [x.split()[0].split('-')[-1] + '.wav' for x in l if x.startswith('ELD')]
    random.shuffle(trans)

    audio = b''
    for f in trans:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('ELD_noise.wav', audio)

    trans = [x.split()[0].split('-')[-1] + '.wav' for x in l if x.startswith('CHD')]
    random.shuffle(trans)

    audio = b''
    for f in trans:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('CHD_noise.wav', audio)

    trans = [x.split()[0].split('-')[-1] + '.wav' for x in l if x.startswith('M') or x.startswith('F')]
    random.shuffle(trans)

    audio = b''
    for f in trans:
        audio += read_wave(os.path.join(path, f))[0]
    write_wave('normal_noise.wav', audio)







