import io
import os
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "D:\git\CESLeA\My First Project-689bf9126b2f.json"

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types

def google_stt(file_name, language_code):
    # Instantiates a client
    client = speech.SpeechClient()

    # Loads the audio into memory
    with io.open(file_name, 'rb') as audio_file:
        content = audio_file.read()
        audio = types.RecognitionAudio(content=content)

    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code=language_code)#영어 : 'en-US' 한국어 : 'ko-KR'

    try:
        # Detects speech in the audio file
        response = client.recognize(config, audio)
        res = ""
        print(response.results)
        for result in response.results:
            res = res + str(result.alternatives[0].transcript)
        return res
    except:
        return "fail"

if __name__ == "__main__":
    # The name of the audio file to transcribe
    file_name = os.path.join(
        os.path.dirname(__file__),
        #'resources',
        'test2.wav')
    google_stt(file_name)