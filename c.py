import contextlib
import wave
import numpy as np


sample_rate = 8000


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


def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


if __name__ == '__main__':
    o, c = np.frombuffer(read_wave('ELDn_.wav')[0], dtype=np.int16), np.frombuffer(read_wave('CHDn.wav')[0], dtype=np.int16)[:2339786]
    print(o.shape, c.shape)
    a = np.stack([o, c], axis=-1)
    print(a.shape)
    ba = a.tobytes()
    assert ba[:2] == read_wave('ELDn_.wav')[0][:2]
    assert ba[2:4] == read_wave('CHDn.wav')[0][:2]
    write_wave('addn.wav', ba)
