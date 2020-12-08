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
    b1 = b''
    b2 = b''
    b3 = b''
    bo1 = b''
    bo2 = b''
    bo3 = b''
    try:
        while True:
            i1, i2, i3 = map(int, input().split('\t'))
            b1 += struct.pack('h', i1)
            b2 += struct.pack('h', i2)
            b3 += struct.pack('h', i3)
    except:
        pass
    print(len(b1))
    print(len(b2))
    print(len(b3))

    write_wave('test1_2.wav', b1)
    write_wave('test2_2.wav', b2)
    write_wave('test3_2.wav', b3)
