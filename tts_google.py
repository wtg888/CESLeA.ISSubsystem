import playsound
from gtts import gTTS

i = 0

def synthesize_text(text, language_code='ko'):
    global i
    """Synthesizes speech from the input string of text."""
    tts = gTTS(text, language_code)
    with open('output%d.mp3'%i, 'wb') as out:
        tts.write_to_fp(out)

    playsound.playsound('output%d.mp3'%i, True)
    i = i + 1


if __name__ == "__main__":
    synthesize_text("안녕하세요", 'ko')