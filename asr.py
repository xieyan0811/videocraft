import os
import ffmpeg
import numpy as np
from loguru import logger
from slicer import Slicer
from scipy.io import wavfile
from utils import SrtTools, get_media_info, is_chinese_language
from vc_config import *

if ASR_MODEL == "local":
    import asr_local as asr_local
else:
    import asr_remote as asr_remote


class VideoSrt:
    """
    Video subtitle generation
    """

    _instance = None

    @staticmethod
    def get_instance():
        if VideoSrt._instance is None:
            VideoSrt._instance = VideoSrt()
        return VideoSrt._instance

    def load_audio(self, file: str, sr: int) -> np.ndarray:
        """
        Load mp4 file's audio into numpy array.
        """
        try:
            out, _ = (
                ffmpeg.input(file, threads=0)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
                .run(
                    cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True
                )
            )
        except Exception as e:
            raise RuntimeError(f"Failed to load audio: {e}")

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

    def slice(self, audio_data, out_dir, rate, loudness):
        """
        Slice audio data into pieces and save wav file to out_dir.
        """
        ret = []
        _max = 0.9
        alpha = 0.25

        slicer = Slicer(
            sr=rate,
            threshold=int(
                loudness * 1.5
            ),
            min_length=int(
                2000
            ),
            min_interval=int(300),
            hop_size=int(
                100
            ),
            max_sil_kept=int(500),
        )

        name = "audio_slice"
        for chunk, start, end in slicer.slice(audio_data):
            tmp_max = np.abs(chunk).max()
            if tmp_max > 1:
                chunk /= tmp_max
            chunk = (chunk / tmp_max * (_max * alpha)) + (1 - alpha) * chunk
            path = "%s/%s_%010d_%010d.wav" % (out_dir, name, start, end)
            wavfile.write(path, rate, (chunk * 32767).astype(np.int16))
            ret.append({"path": path, "start": start, "end": end})
        return ret

    def get_srt(self, video_path, srt_path, md_path, rate):
        """
        convert video_path to srt file
        """
        info = get_media_info(video_path)
        if is_chinese_language(LANGUAGE_CODE):
            if info["width"] > info["height"]:
                char_per_line = 25
            else:
                char_per_line = 14
        else:
            if info["width"] > info["height"]:
                char_per_line = 40
            else:
                char_per_line = 20

        audio_data = self.load_audio(video_path, rate)
        logger.debug(f"duration {len(audio_data)/rate}")
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH)
        files = self.slice(audio_data, TMP_PATH, rate, info["loudness"])
        logger.debug(f"files {len(files)}")

        if ASR_MODEL == "local":
            texts = asr_local.do_asr(files)
        else:
            texts = asr_remote.do_asr(files)

        for x in files:
            os.remove(x["path"])

        
        while len(texts) > 0 and texts[-1]["text"] == "< No Speech >":
            texts.pop()
        # Extend the last paragraph to the end
        if len(texts) > 0:
            texts[-1]["end"] = len(audio_data)

        with open(md_path, "w") as f:
            for i, x in enumerate(texts):
                f.write(f"{x['text']}\n")

        SrtTools.get_instance().write_srt(
            texts, srt_path, rate=rate, char_per_line=char_per_line, no_speech="create"
        )
