import os
from loguru import logger
from vc_config import *
from asr import VideoSrt
from tts import TtsTools
from clip import VideoTools
from utils import get_media_info, regular_audio
import argparse


def get_srt(input_path, output_path):
    # ASR and generate SRT
    VideoSrt.get_instance().get_srt(input_path, output_path, MD_OUT_PATH, rate=RATE)


def make_video(input_video_path, input_srt_path, output_video_path):
    ## TTS
    mp3_path = TMP_MP3_PATH
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    logger.info(f"do_tts, input_srt_path {input_srt_path}")
    TtsTools.get_instance().do_tts(input_srt_path, mp3_path, SRT_OUT_PATH, rate=RATE)
    logger.info(f"{get_media_info(mp3_path)}")
    regular_audio(mp3_path, mp3_path)
    logger.info(f"{get_media_info(mp3_path)}")

    ## Merge VIDEO and AUDIO
    VideoTools.get_instance().post_process(
        input_video_path, mp3_path, output_video_path, SRT_OUT_PATH, force=True
    )


def parse_arguments():
    parser = argparse.ArgumentParser(description="Video Editing")
    parser.add_argument("-v", "--video", help="Input video file")
    parser.add_argument("-s", "--srt", help="Input srt file")
    parser.add_argument("-o", "--output", help="Output file")
    parser.add_argument(
        "-g", "--get_srt", action="store_true", help="Generate srt file"
    )
    parser.add_argument("-m", "--make_video", action="store_true", help="Make video")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_arguments()
    if args.get_srt:
        get_srt(args.video, args.output)
    elif args.make_video:
        make_video(args.video, args.srt, args.output)
