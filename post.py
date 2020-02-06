import time
import requests
import json
import io

with open('spk_url.txt', 'r') as f:
    spk_url = f.read()


def post(createdAt, speaker, speakerId, content):
    try:
        URL = 'x.x.x.x:x/api/v1/speech/browser' # server url will be changed
        data=[('createdAt', createdAt), ('speaker', speaker), ('speakerId', speakerId), ('content', content)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        pass


def post_me(text):
    try:
        URL = 'http://x.x.x.x:5000/tts'
        data=[('text',text)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")
        # pass


def post_add_speaker(speaker):
    try:
        URL = '%s:8080/add_speaker' % spk_url
        data=[('speaker', speaker)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")


def post_add_data(speaker, audio_file):
    try:
        URL = '%s:8080/add_data' % spk_url
        speaker = io.StringIO(speaker)
        files = {
            'audio_file': ('data.wav', open(audio_file, 'rb')),
            'speaker': ('name.txt', speaker)
        }
        res = requests.post(url=URL, files=files)
        print(res.content)
    except:
        print("error")


def post_delete_speaker(speaker):
    try:
        URL = '%s:8080/delete_speaker' % spk_url
        data=[('speaker', speaker)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")


def post_delete_data(speaker):
    try:
        URL = '%s:8080/delete_data' % spk_url
        data=[('speaker', speaker)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")


def post_speaker_recog(audio_file):
    try:
        URL = '%s:8080/speaker_recog' % spk_url
        files = {
            'audio_file': ('data.wav', open(audio_file, 'rb')),
        }
        res = requests.post(url=URL, files=files)
        print(res.content)
        return res.content.decode('utf8')
    except:
        print("error")


def post_age_recog(audio_file):
    try:
        URL = '%s:8090/age_recog' % spk_url
        files = {
            'audio_file': ('data.wav', open(audio_file, 'rb')),
        }
        res = requests.post(url=URL, files=files)
        print(res.content)
        return res.content.decode('utf8')
    except:
        print("error")


if __name__ == '__main__':
    pass
