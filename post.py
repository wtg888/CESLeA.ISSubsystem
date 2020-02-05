import time
import requests
import json


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
        URL = 'http://x.x.x.x:8080/add_speaker'
        data=[('speaker', speaker)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")


def post_add_data(speaker, audio_file):
    try:
        URL = 'http://127.0.0.1:8080/add_data'
        speaker = io.StringIO(speaker)
        files = {
            'audio_file': ('data.mp3', open(audio_file, 'rb')),
            'speaker': ('name.txt', speaker)
        }
        res = requests.post(url=URL, files=files)
        print(res.content)
    except:
        print("error")


def post_delete_speaker(speaker):
    try:
        URL = 'http://127.0.0.1:8080/delete_speaker'
        data=[('speaker', speaker)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")


def post_delete_data(speaker):
    try:
        URL = 'http://127.0.0.1:8080/delete_data'
        data=[('speaker', speaker)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")


if __name__ == '__main__':
    pass
