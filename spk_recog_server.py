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
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'SpeakerRecogv2', 'online')
DATA_DIR = os.path.join(ROOT_DIR, 'data')


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
    with open('speaker_list.txt', 'w', encoding='utf-8') as f:
        for s, i in speaker_dict.items():
            f.write(s + '\t' + i + '\n')


def load_speaker_list():
    global speaker_dict
    global reverse_speaker_dict
    try:
        with open('speaker_list.txt', 'r', encoding='utf-8') as f:
            speaker_dict = {x.split('\t')[0]: x.split('\t')[1] for x in f.read().split('\n') if x}
        reverse_speaker_dict = {v:k for k, v in speaker_dict.items()}
    except:
        f = open('speaker_list.txt', 'w', encoding='utf-8')
        f.close()
        speaker_dict = {}
        reverse_speaker_dict = {}


@app.route("/add_speaker", methods=['POST'])
def add_speaker():
    username = request.files['username']
    username = username.getvalue().decode('utf-8')
    audio_files = [request.files['audio_file%d' % i] for i in range(1, 11)]
    name = username
    if name in speaker_dict.keys():
        return '중복된 이름입니다.'
    if len(speaker_dict.keys()):
        speaker_dict[name] = '%04d' % (max(map(int, speaker_dict.values())) + 1)
    else:
        speaker_dict[name] = '0000'
    reverse_speaker_dict[speaker_dict[name]] = name
    update_speaker_list()
    os.mkdir(os.path.join(DATA_DIR, speaker_dict[name]))
    for i, audio in enumerate(audio_files):
        path = os.path.join(DATA_DIR, speaker_dict[name], get_time() + '_' + str(i) + '.wav')
        write_wav(path, audio)
    train_model()
    return "Add user %s" % name


@app.route("/add_data", methods=['POST'])
def add_data():
    username = request.files['username']
    username = username.getvalue().decode('utf-8')
    name = username
    if name not in speaker_dict.keys():
        return '등록되지 않은 화자입니다.'
    audio_file = request.files['audio_file']
    path = os.path.join(DATA_DIR, speaker_dict[name], get_time() + '.wav')
    write_wav(path, audio_file)
    train_model()
    return "Add %s's data" % name


@app.route("/delete_speaker", methods=['POST'])
def delete_speaker():
    username = request.form['username']
    name = username
    if name not in speaker_dict.keys():
        return '등록되지 않은 화자입니다.'
    shutil.rmtree(os.path.join(DATA_DIR, speaker_dict[name]))
    del reverse_speaker_dict[speaker_dict[name]]
    del speaker_dict[name]
    train_model()
    update_speaker_list()
    return "Delete speaker %s" % name


@app.route("/delete_data", methods=['POST'])
def delete_data():
    username = request.form['username']
    name = username
    if name not in speaker_dict.keys():
        return '등록되지 않은 화자입니다.'
    for x in os.listdir(os.path.join('data', speaker_dict[name])):
        os.remove(os.path.join(DATA_DIR, speaker_dict[name], x))
    return "Delete %s's data" % name


@app.route("/speaker_recog", methods=['POST'])
def speaker_recognition():
    audio_file = request.files['audio_file']
    path = os.path.join(DATA_DIR, 'test', 'test.wav')
    os.system('rm -rf %s' % path)
    write_wav(path, audio_file)
    res = test_speaker_recog()
    os.system('rm -rf %s' % path)
    return res


@app.route("/speaker_list", methods=['GET'])
def speaker_list():
    data = {'speakers': list(speaker_dict.keys())}
    return jsonify(data)


if __name__ == "__main__":
    load_speaker_list()
    app.run(host='0.0.0.0', port='8080', debug=True)
