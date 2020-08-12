import os
import sys
import io
import json
import base64
import numpy as np
import base64
import zipfile


class Handler:
    def __init__(self):
        pass

    def __call__(self, req):
        inp = json.loads(req.input.decode(), strict=False)
        print('cwd', os.getcwd())
        print('listdir', os.listdir('.'))
        audio_data = inp['audio_data']
        audio_data = base64.b64decode(audio_data)
        with open('temp.zip', 'wb') as f:
            f.write(audio_data)
        print('listdir', os.listdir('.'))
        
        with open('b', 'r') as f:
            print(f.read())
        
        with open('b', 'a') as f:
            f.write('\naa\naa')
            
            
        with open('b', 'r') as f:
            print(f.read())
        result = json.dumps(req.input.decode())
        
        return result