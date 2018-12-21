import sys
import os
import struct
import wave
import contextlib


def write_wave(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


if __name__ == '__main__':
    sr = 16000
    bL = b''
    bR = b''
    try:
        while True:
            L, R = map(int, input().split('\t'))
            bL += struct.pack('h', L)
            bR += struct.pack('h', R)
    except:
        pass
    print('finish')
    write_wave('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\L.wav', bL, sr)
    write_wave('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_\\R.wav', bR, sr)

