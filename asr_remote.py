import os
import traceback
import os
from openai import OpenAI
from loguru import logger
from vc_config import *

MAX_RETRIES = 10


def transcribe_audio(file_path, language=LANGUAGE_CODE):
    api_key = os.getenv("OPENAI_API_KEY")
    url = os.getenv("OPENAI_BASE_URL")

    try:
        client = OpenAI(api_key=api_key, base_url=url)
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language=language
            )
        return True, response.text
    except Exception as e:
        logger.error(f"转录错误: {str(e)}")
        traceback.print_exc()
        return False, None


def do_asr(files):
    arr = []
    error_count = 0

    for idx, dic in enumerate(files):
        logger.debug(f"ASR: {idx} {dic['path']}")
        ret, dic["text"] = transcribe_audio(dic["path"])
        if not ret:
            error_count += 1
            dic["text"] = ""
            print(traceback.format_exc())
            logger.error(f"ASR failed, error count: {error_count}")

            if error_count >= MAX_RETRIES:
                logger.error("Too many errors, aborting ASR process")
                return arr
        if ret:
            arr.append(dic)
    return arr
