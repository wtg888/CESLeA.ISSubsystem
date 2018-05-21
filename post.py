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
        
if __name__ == '__main__':
    post(int(time.time()), "TEST", '1', "test")