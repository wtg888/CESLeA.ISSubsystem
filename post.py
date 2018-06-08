import time
import requests
import json

def post(createdAt, speaker, speakerId, content):
    try:
        URL = 'http://155.230.104.191:3001/api/v1/speech'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data=[('createdAt',createdAt), ('speaker',speaker), ('speakerId',speakerId), ('content',content)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        pass

def post_me(text):
    try:
        URL = 'http://127.0.0.1:5000/tts'
        headers = {'Content-Type': 'application/json; charset=utf-8'}
        data=[('text',text)]
        res = requests.post(url=URL, data=data)
        print(res.content)
    except:
        print("error")
        pass

if __name__ == '__main__':
    post_me("TEST")