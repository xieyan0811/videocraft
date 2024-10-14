import os

now_dir = os.path.dirname(os.path.abspath(__file__))

RATE=16000

DATA_DIR = os.path.join(now_dir, 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

srt_path_adj = os.path.join(DATA_DIR, 'tmp_modify.srt')
srt_path_base = os.path.join(DATA_DIR, 'tmp.srt')
md_path = os.path.join(DATA_DIR, 'txt.md')
mp4_input_path = os.path.join(DATA_DIR, 'base.mp4')
mp4_output_path = os.path.join(DATA_DIR, 'base_new.mp4')
mp3_tmp_path = os.path.join(DATA_DIR, 'tmp.mp3')

TMP_PATH = '/tmp/video/'
NO_EMPTY_SRT_PATH = os.path.join(TMP_PATH, 'no_empty.srt')
ADJ_SRT_PATH = os.path.join(TMP_PATH, 'adj.srt')
TMP_VIDEO_SRT_PATH = os.path.join(TMP_PATH, 'tmp_srt.mp4')
TMP_VIDEO_MERGE_PATH = os.path.join(TMP_PATH, 'tmp_merge.mp4')
