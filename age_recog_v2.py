import os
import wave
import contextlib
import time


ROOT_DIR = os.getcwd()
SCRIPTS_DIR = os.path.join(ROOT_DIR, 'AgeRecog', 'online')
DATA_DIR = os.path.join(ROOT_DIR, '300wav_upsample')

speaker_dict = dict()
reverse_speaker_dict = dict()


def write_wave(path, audio):
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(audio)


def load_speaker_list():
    global speaker_dict
    global reverse_speaker_dict
    try:
        with open('age_list.txt', 'r', encoding='utf-8') as f:
            speaker_dict = {x.split('\t')[0]: x.split('\t')[1] for x in f.read().split('\n') if x}
        with open('age_list.txt', 'r', encoding='utf-8') as f:
            reverse_speaker_dict = {x.split('\t')[1]: x.split('\t')[0] for x in f.read().split('\n') if x}
    except:
        f = open('age_list.txt', 'w', encoding='utf-8')
        f.close()
        speaker_dict = {}
        reverse_speaker_dict = {}


def update_speaker_list():
    with open('age_list.txt', 'w', encoding='utf-8') as f:
        for s, i in speaker_dict.items():
            f.write(s + '\t' + i + '\n')


def test_speaker_recog(audio=None):
    try:
        if audio:
            write_wave(os.path.join(DATA_DIR, 'test', 'test.wav'), audio)
        os.chdir(SCRIPTS_DIR)
        os.system('rm -rf %s' % os.path.join(SCRIPTS_DIR, 'result.txt'))
        os.system('time ./run_test.sh')
        os.chdir(ROOT_DIR)
        with open(os.path.join(SCRIPTS_DIR, 'result.txt'), 'r') as f:
            l = f.read().split()[0]
        if l.startswith('m'):
            return 'adult_m'
        elif l.startswith('f'):
            return 'adult_f'
        else:
            return 'kid'

    except Exception as e:
        print('Error', e)
        return '...'


def add_speaker(name):
    if len(speaker_dict.keys()):
        speaker_dict[name] = '%04d' % (max(map(int, speaker_dict.values())) + 1)
    else:
        speaker_dict[name] = '0000'

    reverse_speaker_dict[speaker_dict[name]] = name

    update_speaker_list()
    os.mkdir(os.path.join(DATA_DIR, speaker_dict[name]))


def train_model():
    os.chdir(SCRIPTS_DIR)
    os.system('time ./run_train.sh')
    os.chdir(ROOT_DIR)
