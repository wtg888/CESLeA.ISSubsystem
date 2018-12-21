import os
import struct

if __name__ == '__main__':
    bL = b''
    bR = b''
    try:
        while True:
            L, R = map(int, input().split('\t'))
            print(L, R)
            bL += struct.pack('h', L)
            bR += struct.pack('h', R)
            print(bL, bR)
    except:
        pass
    finally:
        pass
