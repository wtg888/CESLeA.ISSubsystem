from flask import Flask, request, jsonify
import os
import datetime
import shutil
import contextlib
import wave
import numpy as np
import librosa

app = Flask(__name__)
speaker_dict = {}
reverse_speaker_dict = {}

os.chdir('/')

ROOT_DIR = os.getcwd()
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'SpeakerDiarization', 'diarization_online')
DATA_DIR = os.path.join(ROOT_DIR, 'testdata')


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


def write_wave_(path, audio, sample_rate):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)


def write_wav(path, audio):
    audio.save(path.replace('.wav', '_.wav'))
    pcm, sr = read_wave(path.replace('.wav', '_.wav'))

    D = np.frombuffer(pcm, dtype=np.int16)
    data = librosa.core.resample(1.0 * D, orig_sr=sr, target_sr=16000).astype(dtype=np.int16).tobytes()
    write_wave_(path, data, 16000)
    os.system('rm -rf %s' % path.replace('.wav', '_.wav'))


def train_model():
    os.chdir(SCRIPTS_DIR)
    os.system('./run_train.sh')
    os.chdir(ROOT_DIR)


def test_speaker_recog():
    # try:
        os.chdir(SCRIPTS_DIR)
        os.system('./run_test.sh')
        os.chdir(ROOT_DIR)
        l = []
        with open(os.path.join(SCRIPTS_DIR, 'result.txt'), 'r') as f:
            l = f.readlines()
        l = [x.replace('\n', '') for x in l if x]
        for i in range(1, len(l), 2):
            if l[i] == 'unknown':
                continue
            l[i] = reverse_speaker_dict[l[i]]
        os.system('rm -rf %s' % os.path.join(SCRIPTS_DIR, 'result.txt'))
        return l


def get_time():
    time_format = '%Y_%m_%d_%H_%M_%S'
    now = datetime.datetime.now()
    return now.strftime(time_format)


def update_speaker_list():
    with open('data/speaker_list.txt', 'w', encoding='utf-8') as f:
        for s, i in speaker_dict.items():
            f.write(s + '\t' + i + '\n')


def load_speaker_list():
    global speaker_dict
    global reverse_speaker_dict
    try:
        with open('data/speaker_list.txt', 'r') as f:
            speaker_dict = {x.split('\t')[0]: x.split('\t')[1] for x in f.read().split('\n') if x}
        reverse_speaker_dict = {v:k for k, v in speaker_dict.items()}
    except:
        f = open('data/speaker_list.txt', 'w')
        f.close()
        speaker_dict = {}
        reverse_speaker_dict = {}


@app.route("/speaker_recog", methods=['POST'])
def speaker_recognition():
    audio_file = request.files['audio_file']
    path = os.path.join(DATA_DIR, 'test.wav')
    os.system('rm -rf %s' % path)
    write_wav(path, audio_file)
    res = test_speaker_recog()
    os.system('rm -rf %s' % path)
    return '\t'.join(res)


@app.route("/speaker_list", methods=['GET'])
def speaker_list():
    data = {'speakers': list(speaker_dict.keys())}
    return jsonify(data)


if __name__ == "__main__":
    load_speaker_list()
    train_model()
    app.run(host='0.0.0.0', port='8080', debug=True)
