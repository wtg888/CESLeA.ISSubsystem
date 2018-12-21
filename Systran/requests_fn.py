import io
import pycurl
import requests
import json


def asr(data):
    """
    Send audio file to ASR server
    """
    url = 'http://127.0.0.1:7777/filemode/?productcode=DEMO&transactionid=0&language=kor'
    files = {'file': ('wav.pcm', data, "audio/pcm")}
    r = requests.post(url, files=files)
    print(r.status_code)
    print(r.json())
    return r.json()


if __name__ == '__main__':
    pass