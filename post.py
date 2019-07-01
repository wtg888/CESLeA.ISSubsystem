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
    # post test
    try:
        URL = 'http://x.x.x.x:5000/tts'
        data=[('text',text)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")
        pass


if __name__ == '__main__':
    post_me("TEST")