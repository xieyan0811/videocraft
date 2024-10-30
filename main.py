import os
from ve_config import *
from ve_asr import VideoSrt
from tts import TtsTools
from ve_clip import VideoTools
from ve_utils import get_media_info, regular_audio
import argparse

def get_srt(input_path, output_path):
    # 语音识别，生成 srt 文件
    VideoSrt.get_instance().get_srt(input_path, output_path, MD_OUT_PATH, 
                                    rate=RATE)

def make_video(input_video_path, input_srt_path, 
               output_video_path):
    ## 语音合成
    mp3_path = TMP_AUDIO_PATH
    os.environ['TOKENIZERS_PARALLELISM'] = 'false'
    print('input_srt_path', input_srt_path)
    TtsTools.get_instance().do_tts(input_srt_path, mp3_path, SRT_OUT_PATH, rate=RATE)
    print(get_media_info(mp3_path))
    regular_audio(mp3_path, mp3_path)
    print(get_media_info(mp3_path))

    ## 视频合成
    VideoTools.get_instance().post_process(input_video_path, mp3_path, output_video_path, 
                                    SRT_OUT_PATH, force=True)

def parse_arguments():
    parser = argparse.ArgumentParser(description='Video Editing')
    parser.add_argument('-v', '--video', help='Input video file')
    parser.add_argument('-s', '--srt', help='Input srt file')
    parser.add_argument('-o', '--output', help='Output file')
    parser.add_argument('-g', '--get_srt', action='store_true', help='Generate srt file')
    parser.add_argument('-m', '--make_video', action='store_true', help='Make video')
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_arguments()
    if args.get_srt:
        get_srt(args.video, args.output)
    elif args.make_video:
        make_video(args.video, args.srt, args.output)

