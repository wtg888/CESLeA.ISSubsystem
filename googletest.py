import io
import os

# path of your google cloud json file
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = ""

# Imports the Google Cloud client library
from google.cloud import speech
from google.cloud.speech import enums
from google.cloud.speech import types
from google.cloud import texttospeech
import playsound
i = 0


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
        language_code=language_code) # English : 'en-US', Korean : 'ko-KR'

    try:
        # Detects speech in the audio file
        response = client.recognize(config, audio)
        res = ""
        print(response.results)
        for result in response.results:
            res = res + str(result.alternatives[0].transcript)
        return res
    except:
        print("error")
        return ""


def synthesize_text(text, language_code):
    global i
    """Synthesizes speech from the input string of text."""
    client = texttospeech.TextToSpeechClient()

    input_text = texttospeech.types.SynthesisInput(text=text)

    # Note: the voice can also be specified by name.
    # Names of voices can be retrieved with client.list_voices().
    voice = texttospeech.types.VoiceSelectionParams(
        language_code=language_code,
        ssml_gender=texttospeech.enums.SsmlVoiceGender.FEMALE)

    audio_config = texttospeech.types.AudioConfig(
        audio_encoding=texttospeech.enums.AudioEncoding.MP3)

    response = client.synthesize_speech(input_text, voice, audio_config)

    # The response's audio_content is binary.
    with open('output%d.mp3'%i, 'wb') as out:
        out.write(response.audio_content)
    playsound.playsound('output%d.mp3'%i, True)
    i = i + 1


if __name__ == "__main__":
    synthesize_text("Hello World!!", 'en-US')