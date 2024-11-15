import traceback
import os
from openai import OpenAI
from loguru import logger
from vc_config import *
import httpx


def transcribe_audio(file_path, language=LANGUAGE_CODE):
    # 从环境变量获取代理设置
    http_proxy = os.getenv('HTTP_PROXY')
    https_proxy = os.getenv('HTTPS_PROXY')
    
    client = OpenAI(
        http_client=httpx.Client(
            proxies={
                "http://": http_proxy,
                "https://": https_proxy
            } if http_proxy and https_proxy else None
        )
    )
    
    try:
        with open(file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1", file=audio_file, language=language
            )
        return response.text
    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise


def do_asr(files):
    arr = []
    for dic in files:
        logger.debug(f"ASR: {dic['path']}")
        try:
            dic["text"] = transcribe_audio(dic["path"])
        except:
            dic["text"] = ""
            print(traceback.format_exc())
        arr.append(dic)
    return arr
