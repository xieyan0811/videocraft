import traceback
from vc_config import *
from openai import OpenAI


def transcribe_audio(file_path, language=LANGUAGE_CODE):
    client = OpenAI()
    with open(file_path, "rb") as audio_file:
        response = client.audio.transcriptions.create(
            model="whisper-1", file=audio_file, language=language
        )
    return response.text


def do_asr(files):
    arr = []
    for dic in files:
        try:
            dic["text"] = transcribe_audio(dic["path"])
        except:
            dic["text"] = ""
            print(traceback.format_exc())
        arr.append(dic)
    return arr
