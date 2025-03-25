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

    def do_tts(self, in_srt_path, out_mp3_path, out_srt_path, rate, original_audio_path=None):
        texts_in = SrtTools.get_instance().read_srt(
            in_srt_path, unit="frame", rate=rate
        )
        texts_out = []
        if TTS_MODEL == "local":
            tts_local.load()
        pos = 0
        data = np.zeros(0)

        # If using original audio, load the original audio file
        original_audio_data = None
        original_sample_rate = None
        if TTS_MODEL == "original" and original_audio_path:
            original_audio_data, original_sample_rate = sf.read(original_audio_path)
            if original_sample_rate != rate:
                num_samples = int(len(original_audio_data) * rate / original_sample_rate)
                original_audio_data = resample(original_audio_data, num_samples)

        for idx, x in enumerate(texts_in):
            length = x["start"] - pos
            if length > 0:
                silence = np.zeros(int(length))
                if len(data.shape) > 1 and data.shape[1] > 1:
                    silence = np.zeros((int(length), data.shape[1]))
                data = np.concatenate([data, silence])
            plain_text = x["text"]
            plain_text = plain_text.replace("\\n", "")
            # print(f"{plain_text} {x['start']}, {x['end']}, {pos}")
            if plain_text != "< No Speech >":
                if TTS_MODEL == "original" and original_audio_data is not None:
                    # Extract corresponding audio segment from the original audio
                    start_sample = int(x["start"])
                    end_sample = int(x["end"])
                    if end_sample <= len(original_audio_data):
                        audio_data_1 = original_audio_data[start_sample:end_sample]
                    else:
                        logger.warning(f"Original audio too short for segment at {start_sample}:{end_sample}")
                        audio_data_1 = np.zeros(end_sample - start_sample)                
                if TTS_MODEL == "local":
                    ret, desc = tts_local.do_tts(
                        None, None, None, plain_text, language=LANGUAGE_CODE
                    )
                else:
                    ret, desc = tts_remote.do_tts(plain_text, TMP_MP3_PATH, language=LANGUAGE_CODE)
                if TTS_MODEL != "original":
                    if not ret:
                        logger.warning(f"failed to tts: {ret} {desc} {plain_text} {x['start']}, {x['end']}, {pos}")
                        continue
                    self.convert_sample_rate(TMP_MP3_PATH, TMP_WAV_PATH, rate, idx=idx)
                    audio_data_1, _ = sf.read(TMP_WAV_PATH)
            else:
                if len(data.shape) > 1 and data.shape[1] > 1:
                    audio_data_1 = np.zeros((int(x["end"] - x["start"]), data.shape[1]))
                else:
                    audio_data_1 = np.zeros(int(x["end"] - x["start"]))
            
            if len(data.shape) != len(audio_data_1.shape):
                # Convert from mono to multi-channel
                if len(data.shape) == 1 and len(audio_data_1.shape) > 1:
                    data = data.reshape(-1, 1)
                    if audio_data_1.shape[1] > 1:
                        data = np.tile(data, (1, audio_data_1.shape[1]))
                elif len(data.shape) > 1 and len(audio_data_1.shape) == 1:
                    audio_data_1 = audio_data_1.reshape(-1, 1)
                    if data.shape[1] > 1:
                        audio_data_1 = np.tile(audio_data_1, (1, data.shape[1]))
            
            pos_start = len(data)
            data = np.concatenate([data, audio_data_1])
            pos = len(data)
            x_new = {"start": pos_start, "end": pos, "text": x["text"]}
            texts_out.append(x_new)

        sf.write(out_mp3_path, data, rate, format="wav")
        SrtTools.get_instance().write_srt(
            texts_out, out_srt_path, rate=rate, no_speech="keep"
        )

    def convert_sample_rate(self, input_path, output_path, target_sample_rate=16000, idx=0):
        data, original_sample_rate = sf.read(input_path)
        num_samples = int(len(data) * target_sample_rate / original_sample_rate)
        resampled_data = resample(data, num_samples)
        sf.write(output_path, resampled_data, target_sample_rate)
        logger.debug(f"{idx} convert rate: {target_sample_rate}, and save to: {output_path}")
