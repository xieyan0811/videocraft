import ffmpeg
from datetime import time
from loguru import logger
import pysrt
from utils import SrtTools, is_chinese_language
from vc_config import *


def time_to_seconds(t: time) -> float:
    return t.hour * 3600 + t.minute * 60 + t.second + t.microsecond / 1e6


class VideoCutter:
    def __init__(self, input_path, srt_file, output_path):
        self.input_path = input_path
        self.srt_file = srt_file
        self.output_path = output_path

    def read_srt_intervals(self):
        # parse srt file and get intervals
        subtitles = pysrt.open(self.srt_file, encoding="utf-8")
        intervals = [
            (time_to_seconds(sub.start.to_time()), time_to_seconds(sub.end.to_time()))
            for sub in subtitles
        ]
        return intervals

    def do_cut(self, debug=False):
        intervals = self.read_srt_intervals()
        output_clips = []

        for idx, (start, end) in enumerate(intervals):
            clip_output = os.path.join(TMP_PATH, f"clip_{idx}.mp4")
            if debug:
                logger.debug(f"Processing clip {idx}: {start} to {end}")

            (
                ffmpeg.input(self.input_path, ss=start, to=end)
                .output(clip_output, vcodec="libx264", acodec="aac")
                .run(overwrite_output=True)
            )
            output_clips.append(clip_output)

        concat_file = os.path.join(DATA_DIR, "concat_list.txt")
        with open(concat_file, "w") as f:
            for clip in output_clips:
                f.write(f"file '{clip}'\n")

        ffmpeg.input(concat_file, format="concat", safe=0).output(
            self.output_path, c="copy"
        ).run(overwrite_output=True)
        logger.debug(f"Final output saved as {self.output_path}")


class VideoTools:
    """
    Post process video
    """

    _instance = None

    @staticmethod
    def get_instance():
        if VideoTools._instance is None:
            VideoTools._instance = VideoTools()
        return VideoTools._instance

    def add_subtitle(self, input_path, srt_path, output_path, force=False):
        """
        Remove nospeech from srt
        """
        srt_without_nospeech = SrtTools.get_instance().read_srt(srt_path, unit="second")
        SrtTools.get_instance().write_srt(
            srt_without_nospeech, NO_EMPTY_SRT_PATH, rate=1, no_speech="remove"
        )
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH)
        if is_chinese_language(LANGUAGE_CODE):
            subtitle_style = "FontName=Source Han Sans SC VF,Bold=-1,Fontsize=12,outline=0.3,Shadow=0.2,OutlineColour=&H555555&"
        else:
            subtitle_style = "FontName=Arial,Bold=-1,Fontsize=12,outline=0.3,Shadow=0.2,OutlineColour=&H555555&"
        if os.path.exists(output_path):
            if force:
                os.remove(output_path)
            else:
                return
        stream = ffmpeg.input(input_path)
        stream = stream.filter(
            "subtitles", NO_EMPTY_SRT_PATH, force_style=subtitle_style
        )
        stream = stream.output(output_path, format="mp4")
        stream.global_args("-loglevel", "error")
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

    def merge_audio_video(self, video_path, audio_path, output_path, force=False):
        """
        Merge audio and video
        """
        if os.path.exists(output_path):
            if force:
                os.remove(output_path)
            else:
                return
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)
        stream = ffmpeg.output(input_video.video, input_audio.audio, output_path)
        stream.global_args("-loglevel", "error")
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

    def do_cut(self, input_video, output_video, srt_file, debug=True):
        """
        Remove silent segments from video based on SRT file
        """
        cutter = VideoCutter(input_video, srt_file, output_video)
        cutter.do_cut()

    def post_process(
        self,
        video_input_path,
        audio_input_path,
        video_output_path,
        srt_path,
        force=False,
    ):
        """
        Post process video interface function
        """
        self.add_subtitle(video_input_path, srt_path, TMP_VIDEO_SRT_PATH, force=force)
        self.merge_audio_video(
            TMP_VIDEO_SRT_PATH, audio_input_path, TMP_VIDEO_MERGE_PATH, force=force
        )
        self.do_cut(TMP_VIDEO_MERGE_PATH, video_output_path, srt_path)
        # os.remove(TMP_VIDEO_SRT_PATH)
        # os.remove(TMP_VIDEO_MERGE_PATH)
