import os
from loguru import logger
from vc_config import *
from utils import is_chinese_language
import edge_tts
from openai import OpenAI


def do_tts(text, out_path, language, debug=False):
    try:
        if os.path.exists(out_path):
            os.remove(out_path)
        if TTS_MODEL == "edge":
            do_tts_edge(text, out_path, language, debug)
        else:
            do_tts_openai(text, out_path)
    except Exception as e:
        logger.warning(f"failed {e}")
        return False, e


def do_tts_edge(text, out_path, language, debug=False):
    speed_delta = "+0%"
    if debug:
        logger.debug(
            f"text {len(text)}, {text[:20]}, language {language}, speed {speed_delta}"
        )
    if is_chinese_language(language):
        VOICE = "zh-CN-YunxiNeural"
    else:
        VOICE = "en-GB-SoniaNeural"
    communicate = edge_tts.Communicate(
        text, VOICE, rate=speed_delta, proxy=os.environ.get("HTTP_PROXY", None)
    )
    communicate.save_sync(out_path)


def do_tts_openai(text, out_path):
    model = "tts-1"
    voice = "onyx"
    client = OpenAI()
    response = client.audio.speech.create(
        model=model, voice=voice, speed=1.0, input=text
    )
    with open(out_path, "wb") as file:
        file.write(response.content)
