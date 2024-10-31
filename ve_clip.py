import ffmpeg
from ve_utils import SrtTools
from ve_config import *
import srt

class VideoCutter:
    def __init__(self, input_path, srt_file, output_path):
        self.input_path = input_path
        self.srt_file = srt_file
        self.output_path = output_path

    def read_srt_intervals(self):
        # 从srt文件解析时间片段
        with open(self.srt_file, 'r', encoding='utf-8') as f:
            subtitles = list(srt.parse(f))
        intervals = [(sub.start.total_seconds(), sub.end.total_seconds()) for sub in subtitles]
        return intervals

    def do_cut(self, debug=True):
        # 获取srt的时间片段
        intervals = self.read_srt_intervals()
        output_clips = []
        
        for idx, (start, end) in enumerate(intervals):
            # 生成每个剪辑片段的文件路径
            clip_output = os.path.join(DATA_DIR, f"clip_{idx}.mp4")
            if debug:
                print(f"Processing clip {idx}: {start} to {end}")
                
            # 使用ffmpeg切割视频片段
            (
                ffmpeg
                .input(self.input_path, ss=start, to=end)
                .output(clip_output, vcodec='libx264', acodec='aac')
                .run(overwrite_output=True)
            )
            output_clips.append(clip_output)

        # 将所有视频片段合并
        concat_file = os.path.join(DATA_DIR, 'concat_list.txt')
        with open(concat_file, 'w') as f:
            for clip in output_clips:
                f.write(f"file '{clip}'\n")

        ffmpeg.input(concat_file, format='concat', safe=0).output(self.output_path, c='copy').run(overwrite_output=True)
        print(f"Final output saved as {self.output_path}")
        
class VideoTools:
    '''
    视频后期处理
    '''
    _instance = None

    @staticmethod
    def get_instance():
        if VideoTools._instance is None:
            VideoTools._instance = VideoTools()
        return VideoTools._instance
    
    def add_subtitle(self, input_path, srt_path, output_path, force=False):
        '''
        视频加字幕
        '''
        # 去掉无声片段
        srt_without_nospeech = SrtTools.get_instance().read_srt(srt_path, unit='second')
        SrtTools.get_instance().write_srt(srt_without_nospeech, NO_EMPTY_SRT_PATH, rate=1, no_speech='remove')
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH)
        subtitle_style = "FontName=Source Han Sans SC VF,Bold=-1,Fontsize=12,outline=0.3,Shadow=0.2,OutlineColour=&H555555&"
        if os.path.exists(output_path):
            if force:
                os.remove(output_path)
            else:
                return
        stream = ffmpeg.input(input_path)
        stream = stream.filter('subtitles', NO_EMPTY_SRT_PATH, force_style=subtitle_style)
        stream = stream.output(output_path, format='mp4')
        stream.global_args('-loglevel', 'error')
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

    def merge_audio_video(self, video_path, audio_path, output_path, force=False):
        '''
        替换视频中的音频
        '''
        if os.path.exists(output_path):
            if force:
                os.remove(output_path)    
            else:
                return
        input_video = ffmpeg.input(video_path)
        input_audio = ffmpeg.input(audio_path)
        stream = ffmpeg.output(input_video.video, input_audio.audio, output_path)
        stream.global_args('-loglevel', 'error')
        ffmpeg.run(stream, capture_stdout=True, capture_stderr=True)

    def do_cut(self, input_video, output_video, srt_file, debug=True):
        '''
        去除无声片断
        (太长的视频，需要分段存储，后面再说)
        '''
        cutter = VideoCutter(input_video, srt_file, output_video)
        cutter.do_cut()
    
    def post_process(self, video_input_path, audio_input_path, video_output_path, srt_path, force=False):
        '''
        视频后期处理调用入口
        '''
        self.add_subtitle(video_input_path, srt_path, TMP_VIDEO_SRT_PATH, force=force)
        self.merge_audio_video(TMP_VIDEO_SRT_PATH, audio_input_path, TMP_VIDEO_MERGE_PATH, force=force)
        self.do_cut(TMP_VIDEO_MERGE_PATH, video_output_path, srt_path)
        #os.remove(TMP_VIDEO_SRT_PATH)
        #os.remove(TMP_VIDEO_MERGE_PATH)

