import os
import torch
from loguru import logger
import soundfile as sf
from vc_config import *
import config as global_config
from command.inference import get_tts_wav, g_infer  

local_config = None
local_dic_args = None


def init():
    # Initialize your model here
    global local_config
    global local_dic_args
    local_config = global_config.Config()
    os.chdir("/opt/xieyan/git/GPT-SoVITS_cmd")
    local_dic_args = {
        "model_name": "zhaoyy",
        "sovits_path": local_config.sovits_path,
        "gpt_path": local_config.gpt_path,
        "default_refer_path": "",
        "default_refer_text": "",
        "default_refer_language": "",
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "bind_addr": "0.0.0.0",
        "port": 9880,
        "full_precision": False,
        "half_precision": False,
        "hubert_path": local_config.cnhubert_path,
        "bert_path": local_config.bert_path,
    }
    load()


def load():
    global local_config
    global local_dic_args
    g_infer.load(local_config, local_dic_args)
    # g_infer.hps.data.sampling_rate = rate # not effective


def do_tts(refer_wav_path, prompt_text, prompt_language, text, text_language):
    global local_config
    global local_dic_args
    if (
        refer_wav_path == ""
        or refer_wav_path is None
        or prompt_text == ""
        or prompt_text is None
        or prompt_language == ""
        or prompt_language is None
    ):
        refer_wav_path, prompt_text, prompt_language = (
            g_infer.model_info.path,
            g_infer.model_info.text,
            g_infer.model_info.language,
        )
        if not g_infer.model_info.is_ready():
            return None

    text = text.replace("\\n", "")
    with torch.no_grad():
        gen = get_tts_wav(
            refer_wav_path, prompt_text, prompt_language, text, text_language
        )
        sampling_rate, audio_data = next(gen)

    sf.write(TMP_WAV_PATH, audio_data, sampling_rate, format="wav")
    torch.cuda.empty_cache()
    if local_dic_args["device"] == "mps":
        logger.debug("executed torch.mps.empty_cache()")
        torch.mps.empty_cache()
