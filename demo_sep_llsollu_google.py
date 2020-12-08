import os
os.chdir('C:\\Users\\MI\\Documents\\GitHub\\CESLeA_')
import struct
import wave
import contextlib
import numpy as np
import librosa
from llsollu.requests_fn import asr
from googletest import google_stt


def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
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
        assert sample_rate in (16000, )
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate


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
            b1 += struct.pack('h', i1)
            b2 += struct.pack('h', i2)
            b3 += struct.pack('h', i3)
            bo1 += struct.pack('h', io1)
            bo2 += struct.pack('h', io2)
            bo3 += struct.pack('h', io3)
    except:
        pass

    write_wave('test1.wav', b1)
    write_wave('test2.wav', b2)
    write_wave('test3.wav', b3)

    write_wave('testo1.wav', bo1)
    write_wave('testo2.wav', bo2)
    write_wave('testo3.wav', bo3)
    
    print('녹음 완료')
    
    b1 = read_wave('test1.wav')[0]
    b2 = read_wave('test3.wav')[0]

    D = np.frombuffer(b1, dtype=np.int16)
    data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
    llsollu_ans1 = asr(data)

    D = np.frombuffer(b2, dtype=np.int16)
    data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
    llsollu_ans2 = asr(data)

    b1 = read_wave('testo1.wav')[0]
    b2 = read_wave('testo2.wav')[0]
    b3 = read_wave('testo3.wav')[0]

    D1 = np.frombuffer(b1, dtype=np.int16)
    D2 = np.frombuffer(b2, dtype=np.int16)
    D3 = np.frombuffer(b3, dtype=np.int16)

    # D = np.frombuffer(b1, dtype=np.int16)
    # data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
    # llsollu_ans1 = asr(data)

    D = (1.0 * D1 + 1.0 * D2 + 1.0 * D3) # / 3.0
    bo = D.astype(np.int16).tobytes()
    write_wave('testo.wav', bo)

    # D = np.frombuffer(b1, dtype=np.int16)
    # data = librosa.core.resample(1.0 * D, orig_sr=16000, target_sr=8000).astype(dtype=np.int16).tobytes()
    # llsollu_ans1 = asr(data)

    # ans1 = google_stt('testo1.wav')
    # ans2 = google_stt('testo3.wav')
    ans = google_stt('testo.wav')
    print('음원 분리 + 엘솔루 노인 :', llsollu_ans1 if llsollu_ans1 else '인식 불가')
    print('음원 분리 + 엘솔루 아이 :', llsollu_ans2 if llsollu_ans2 else '인식 불가')
    # print('       구글 mic 1       :', ans1 if ans1 else '인식 불가')
    # print('       구글 아이         :', ans2 if ans2 else '인식 불가')
    print('             구글      :', ans if ans else '인식 불가')
