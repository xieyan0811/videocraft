import os

RATE=16000

now_dir = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(now_dir, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)
TMP_PATH = os.path.join(now_dir, 'tmp')
if not os.path.exists(TMP_PATH):
    os.mkdir(TMP_PATH)

MD_OUT_PATH = os.path.join(TMP_PATH, 'srt.md') # 从视频中识别的md格式的音频文字
SRT_OUT_PATH = os.path.join(TMP_PATH, 'out.srt') # 根据tts调整后的srt
TMP_AUDIO_PATH = os.path.join(DATA_DIR, 'tmp.mp3') # 中间生成的音频
NO_EMPTY_SRT_PATH = os.path.join(TMP_PATH, 'no_empty.srt') # 去掉无声片段的srt
TMP_VIDEO_SRT_PATH = os.path.join(TMP_PATH, 'tmp_srt.mp4') # 加了字幕的临时视频
TMP_VIDEO_MERGE_PATH = os.path.join(TMP_PATH, 'tmp_merge.mp4') # 合并后的视频

