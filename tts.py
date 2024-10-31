import soundfile as sf
import numpy as np
from loguru import logger
from scipy.signal import resample
from utils import SrtTools
from vc_config import *

if TTS_MODEL == "local":
    import tts_local as tts_local
else:
    import tts_remote as tts_remote


class TtsTools:
    _instance = None

    @staticmethod
    def get_instance():
        if TtsTools._instance is None:
            TtsTools._instance = TtsTools()
        return TtsTools._instance

    def __init__(self):
        if TTS_MODEL == "local":
            tts_local.init()

    def do_tts(self, in_srt_path, out_mp3_path, out_srt_path, rate):
        texts_in = SrtTools.get_instance().read_srt(
            in_srt_path, unit="frame", rate=rate
        )
        texts_out = []
        if TTS_MODEL == "local":
            tts_local.load()
        pos = 0
        data = np.zeros(0)

        for x in texts_in:
            length = x["start"] - pos
            if length > 0:
                silence = np.zeros(int(length))
                data = np.concatenate([data, silence])
            plain_text = x["text"]
            plain_text = plain_text.replace("\\n", "")
            # print(f"{plain_text} {x['start']}, {x['end']}, {pos}")
            if plain_text != "< No Speech >":
                if TTS_MODEL == "local":
                    tts_local.do_tts(
                        None, None, None, plain_text, language=LANGUAGE_CODE
                    )
                else:
                    tts_remote.do_tts(plain_text, TMP_MP3_PATH, language=LANGUAGE_CODE)
                self.convert_sample_rate(TMP_MP3_PATH, TMP_WAV_PATH, rate)
                audio_data_1, _ = sf.read(TMP_WAV_PATH)
            else:
                audio_data_1 = np.zeros(int(x["end"] - x["start"]))
            pos_start = len(data)
            data = np.concatenate([data, audio_data_1])
            pos = len(data)
            x_new = {"start": pos_start, "end": pos, "text": x["text"]}
            texts_out.append(x_new)

        sf.write(out_mp3_path, data, rate, format="wav")
        SrtTools.get_instance().write_srt(
            texts_out, out_srt_path, rate=rate, no_speech="keep"
        )

    def convert_sample_rate(self, input_path, output_path, target_sample_rate=16000):
        data, original_sample_rate = sf.read(input_path)
        num_samples = int(len(data) * target_sample_rate / original_sample_rate)
        resampled_data = resample(data, num_samples)
        sf.write(output_path, resampled_data, target_sample_rate)
        logger.debug(f"convert rate: {target_sample_rate}, and dave to: {output_path}")
