import os
from dotenv import load_dotenv
from loguru import logger
import ffmpeg
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

    # When TTS_MODEL is "original", extract the original audio and pass it to do_tts
    original_audio_path = None
    if TTS_MODEL == "original":
        # Extract original audio
        original_audio_path = os.path.join(TMP_PATH, "original_audio.wav")
        
        video_tools = VideoTools.get_instance()
        video_tools.extract_audio(input_video_path, original_audio_path)
    
    # Pass the original audio path to do_tts
    TtsTools.get_instance().do_tts(
        input_srt_path, mp3_path, SRT_OUT_PATH, rate=RATE, original_audio_path=original_audio_path
    )
    
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

    logger.info(f"TTS_MODEL: {TTS_MODEL}")
    logger.info(f"ASR_MODEL: {ASR_MODEL}")
    args = parse_arguments()
    if args.get_srt:
        get_srt(args.video, args.output)
    elif args.make_video:
        make_video(args.video, args.srt, args.output)
