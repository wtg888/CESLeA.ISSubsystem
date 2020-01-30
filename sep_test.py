import os
os.chdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_')
import struct
import wave
import contextlib


def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio)


if __name__ == '__main__':
    bL = b''
    bR = b''
    try:
        while True:
            L, R = map(int, input().split('\t'))
            # print(L, R)
            bL += struct.pack('h', L)
            bR += struct.pack('h', R)
    except:
        pass
    # print(len(bL))
    # print(len(bR))
    write_wave('testL.wav', bL)
    write_wave('testR.wav', bR)

