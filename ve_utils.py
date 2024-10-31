'''
辅助工具
'''

import numpy as np
from pyloudnorm import Meter, normalize
import soundfile as sf
import ffmpeg
from pyloudnorm import Meter
import pysrt

class SrtTools:
    '''
    SRT文件处理
    '''
    _instance = None

    @staticmethod
    def get_instance():
        if SrtTools._instance is None:
            SrtTools._instance = SrtTools()
        return SrtTools._instance

    def read_srt(self, srt_path, unit='second', rate=None):
        subs = pysrt.open(srt_path, encoding='utf-8')
        ret = []
        for sub in subs:
            start_seconds = sub.start.hours * 3600 + sub.start.minutes * 60 + sub.start.seconds + sub.start.milliseconds / 1000
            end_seconds = sub.end.hours * 3600 + sub.end.minutes * 60 + sub.end.seconds + sub.end.milliseconds / 1000
            if unit == 'second' or rate is None:
                dic = {
                    'start': start_seconds,
                    'end': end_seconds,
                    'text': sub.text
                }
            else:
                dic = {
                    'start': int(start_seconds * rate),
                    'end': int(end_seconds * rate),
                    'text': sub.text
                }
            ret.append(dic)
        return ret

    def merge_no_speech(self, texts):
        # 连续多个< No Speech >合并成一个
        ret = []
        last = None
        for x in texts:
            if x['text'] == '< No Speech >':
                if last is None:
                    last = x
                else:
                    last['end'] = x['end']
            else:
                if last is not None:
                    ret.append(last)
                    last = None
                ret.append(x)
        if last is not None:
            ret.append(last)
        return ret

    def regular_text(self, text, char_per_line=-1):
        if text.endswith('。'):
            text = text[:-1]
        if text.find('\\n') != -1:
            return text
        if char_per_line > 0:
            arr = [text[i:i+char_per_line] for i in range(0, len(text), char_per_line)]
            text = '\\n'.join(arr)
        return text

    def write_srt(self, texts, srt_path, rate=1, char_per_line=-1, no_speech='keep'):
        '''
        支持三种情况：
        1. 有语音，无空白，生成空白 no_speech: create
        2. 有语音，有空白，保留空白 no_speech: keep
        3. 有语音，有空白，去掉空白 no_speech: remove
        '''
        subs = pysrt.SubRipFile()
        if no_speech == 'keep':
            texts = self.merge_no_speech(texts)
        last = 0
        idx = 1
        for dic in texts:
            text = dic['text']
            start = dic['start'] / rate
            end = dic['end'] / rate

            # 将 start 和 end 转换为 SubRipTime
            start_srt = pysrt.SubRipTime(seconds=int(start))
            start_srt.milliseconds = int((start - int(start)) * 1000)
            
            end_srt = pysrt.SubRipTime(seconds=int(end))
            end_srt.milliseconds = int((end - int(end)) * 1000)

            if no_speech == 'create':
                if start > last and len(text) > 0:
                    no_speech_sub = pysrt.SubRipItem(
                        index=idx,
                        start=pysrt.SubRipTime(seconds=int(last)),
                        end=start_srt,
                        text='< No Speech >'
                    )
                    subs.append(no_speech_sub)
                    idx += 1

            if no_speech != 'remove' or text != '< No Speech >':
                text = self.regular_text(text, char_per_line)
                if text:
                    sub = pysrt.SubRipItem(
                        index=idx,
                        start=start_srt,
                        end=end_srt,
                        text=text
                    )
                    subs.append(sub)
                    idx += 1
                last = end

        # 写入文件
        subs.save(srt_path, encoding='utf-8')
        
def get_media_info(path):
    '''
    获取视频或音频的信息
    '''
    ret = {}

    # 获取基本信息
    probe = ffmpeg.probe(path)
    format_info = probe.get('format', {})
    duration = float(format_info.get('duration', 0))
    ret['duration'] = duration

    # 获取音频和视频流信息
    audio_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'audio'), None)
    video_stream = next((stream for stream in probe['streams'] if stream['codec_type'] == 'video'), None)

    # 处理音频信息
    if audio_stream:
        ret['audio_sample_rate'] = int(audio_stream['sample_rate'])
        
        # 提取音频数据
        out, _ = (
            ffmpeg
            .input(path)
            .output('pipe:', format='wav', acodec='pcm_s16le', ar=22000)
            .run(capture_stdout=True, capture_stderr=True)
        )
        
        # 将音频数据转换为数组
        audio_arr = np.frombuffer(out, np.int16).astype(np.float32) / 32768.0
        if audio_stream.get('channels', 1) > 1:
            audio_arr = audio_arr.reshape(-1, 2).mean(axis=1)
        
        # 计算响度
        meter = Meter(rate=22000)  # 使用 22000 Hz 的采样率
        ret['loudness'] = meter.integrated_loudness(audio_arr)
    
    # 处理视频信息
    if video_stream:
        ret['width'] = int(video_stream['width'])
        ret['height'] = int(video_stream['height'])
    
    return ret

def regular_audio(in_path, out_path, target_loudness=-20.0):
    '''
    将音频调整为统一的音量
    '''
    audio_arr, rate = sf.read(in_path)
    if len(audio_arr.shape) > 1:
        audio_arr = np.mean(audio_arr, axis=1)

    meter = Meter(rate)
    loudness = meter.integrated_loudness(audio_arr)
    print("Original Loudness: ", loudness)

    normalized_audio = normalize.loudness(audio_arr, loudness, target_loudness)
    new_loudness = meter.integrated_loudness(normalized_audio)
    print("New Loudness: ", new_loudness)
    sf.write(out_path, normalized_audio, rate)
