from flask import Flask, request, jsonify
import os
from message import create_msg

app = Flask(__name__)
speaker_dict = {}
reverse_speaker_dict = {}


@app.route("/iss", methods=['POST'])
def stt():
    text = request.form['text']
    spk = request.form['speaker']
    print(spk, text)
    return "200 OK"


def run_app():
    app.run(host='0.0.0.0', port='8080', debug=True)


if __name__ == "__main__":
    run_app()
