import io
import pycurl
import requests
import json


def asr(data):
    """
    Send audio file to ASR server
    """
    f = open('url.txt', 'r')
    url = f.read()
    f.close()
    files = {'file': ('wav.pcm', data, "audio/pcm")}
    r = requests.post(url, files=files)
    res = r.json()
    out = 'fail'
    if r.status_code == 200 and res['rcode'] == 1:
        out = res['result']
    return out


if __name__ == '__main__':
    pass