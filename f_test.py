from flask import Flask
from flask import request
app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/api/v1/speech', methods=['POST'])
def tts():
    global On
    if request.method == 'POST':
        print(request.form['createdAt'], request.form['speaker'], request.form['speakerId'], request.form['content'])
        return 'OK'
    else:
        return '잘못된 접근입니다.'



def main():
    app.run(host='0.0.0.0', port=3001)

if __name__ == '__main__':
    main()