from flask import Flask, request, jsonify

app = Flask(__name__)
speaker_dict = {}
reverse_speaker_dict = {}


@app.route("/stt", methods=['POST'])
def stt():
    text = request.form['text']
    print(text)
    return "OK"


@app.route("/spk", methods=['POST'])
def spk():
    text = request.form['text']
    print(text)
    return "OK"


@app.route("/env", methods=['POST'])
def env():
    text = request.form['text']
    print(text)
    return "OK"


def run_app():
    app.run(host='0.0.0.0', port='8080', debug=True)


if __name__ == "__main__":
    run_app()
