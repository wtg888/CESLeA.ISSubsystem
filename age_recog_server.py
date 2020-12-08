from flask import Flask, request, jsonify
import os
import datetime
import shutil
import contextlib
import wave

app = Flask(__name__)
speaker_dict = {}
reverse_speaker_dict = {}

ROOT_DIR = os.getcwd()
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'AgeRecog', 'online')
DATA_DIR = os.path.join(ROOT_DIR, 'data2')


def write_wav(path, audio):
    audio.save(path)


def train_model():
    os.chdir(SCRIPTS_DIR)
    os.system('time ./run_train.sh')
    os.chdir(ROOT_DIR)


def test_speaker_recog():
    # try:
        os.chdir(SCRIPTS_DIR)
        os.system('time ./run_test.sh')
        os.chdir(ROOT_DIR)
        with open(os.path.join(SCRIPTS_DIR, 'result.txt'), 'r') as f:
            l = f.readline()
        os.system('rm -rf %s' % os.path.join(SCRIPTS_DIR, 'result.txt'))
        return reverse_speaker_dict[l.split()[0]]


def get_time():
    time_format = '%Y_%m_%d_%H_%M_%S'
    now = datetime.datetime.now()
    return now.strftime(time_format)


def update_speaker_list():
    with open('age_list.txt', 'w', encoding='utf-8') as f:
        for s, i in speaker_dict.items():
            f.write(s + '\t' + i + '\n')


def load_speaker_list():
    global speaker_dict
    global reverse_speaker_dict
    try:
        with open('age_list.txt', 'r', encoding='utf-8') as f:
            speaker_dict = {x.split('\t')[0]: x.split('\t')[1] for x in f.read().split('\n') if x}
        reverse_speaker_dict = {v:k for k, v in speaker_dict.items()}
    except:
        f = open('age_list.txt', 'w', encoding='utf-8')
        f.close()
        speaker_dict = {}
        reverse_speaker_dict = {}


@app.route("/age_recog", methods=['POST'])
def speaker_recognition():
    audio_file = request.files['audio_file']
    path = os.path.join(DATA_DIR, 'test', 'test.wav')
    os.system('rm -rf %s' % path)
    write_wav(path, audio_file)
    res = test_speaker_recog()
    os.system('rm -rf %s' % path)
    return res


@app.route("/age_list", methods=['GET'])
def speaker_list():
    data = {'speakers': list(speaker_dict.keys())}
    return jsonify(data)


if __name__ == "__main__":
    load_speaker_list()
    app.run(host='0.0.0.0', port='8090', debug=True)
