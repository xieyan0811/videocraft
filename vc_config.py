import os
from dotenv import load_dotenv

load_dotenv()

RATE = os.environ.get("RATE", 16000)
RATE = int(RATE) if isinstance(RATE, str) and RATE.isdigit() else RATE
TTS_MODEL = os.environ.get("TTS_MODEL", "openai")  # edge/openai/local/original
ASR_MODEL = os.environ.get("ASR_MODEL", "remote")  # local/openai
LANGUAGE_CODE = os.environ.get("LANGUAGE_CODE", "zh") # zh/en

current_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(current_dir, "data"))
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
TMP_PATH = os.path.join(DATA_DIR, "tmp")
if not os.path.exists(TMP_PATH):
    os.makedirs(TMP_PATH)
TMP_MP3_PATH = os.path.join(TMP_PATH, "tmp.mp3")
TMP_WAV_PATH = os.path.join(TMP_PATH, "tmp.wav")
MD_OUT_PATH = os.path.join(TMP_PATH, "srt.md")  # Transcribed audio text in markdown format from the video
SRT_OUT_PATH = os.path.join(TMP_PATH, "out.srt")  # SRT adjusted based on TTS
NO_EMPTY_SRT_PATH = os.path.join(TMP_PATH, "no_empty.srt")  # SRT without silent segments
TMP_VIDEO_SRT_PATH = os.path.join(TMP_PATH, "tmp_srt.mp4")  # Temporary video with subtitles
TMP_VIDEO_MERGE_PATH = os.path.join(TMP_PATH, "tmp_merge.mp4")  # Merged video

