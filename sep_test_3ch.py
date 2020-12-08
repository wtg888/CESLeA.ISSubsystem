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
            i1, i2, i3, io1, io2, io3 = map(int, input().split('\t'))
            # print(L, R)
            b1 += struct.pack('h', i1)
            b2 += struct.pack('h', i2)
            b3 += struct.pack('h', i3)
            bo1 += struct.pack('h', io1)
            bo2 += struct.pack('h', io2)
            bo3 += struct.pack('h', io3)
    except:
        pass
    print(len(b1))
    print(len(b2))
    print(len(b3))
    print(len(bo1))
    print(len(bo2))
    print(len(bo3))

    write_wave('test1.wav', b1)
    write_wave('test2.wav', b2)
    write_wave('test3.wav', b3)

    write_wave('testo1.wav', bo1)
    write_wave('testo2.wav', bo2)
    write_wave('testo3.wav', bo3)
