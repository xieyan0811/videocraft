'''
辅助工具
'''

import time
from datetime import datetime
import numpy as np
from moviepy.editor import VideoFileClip, AudioFileClip
from pyloudnorm import Meter, normalize
import soundfile as sf

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

    def time_str_to_seconds(self, time_str):
        print("xx", time_str)
        time_obj = datetime.strptime(time_str, '%H:%M:%S,%f')
        total_seconds = time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second + time_obj.microsecond / 1e6
        return total_seconds

    def read_srt(self, srt_path, unit = 'second', rate = None):
        with open(srt_path, "r", encoding='utf-8') as f:
            lines = f.readlines()
            lines = [x.strip() for x in lines]
            lines = [x for x in lines if x]
            ret = []
            for i in range(0, len(lines), 3):
                if unit == 'second' or rate is None:
                    dic = {
                        'start': self.time_str_to_seconds(lines[i+1].split(' ')[0]),
                        'end': self.time_str_to_seconds(lines[i+1].split(' ')[2]),
                        'text': lines[i+2]
                    }
                else:
                    dic = {
                        'start': int(self.time_str_to_seconds(lines[i+1].split(' ')[0]) * rate),
                        'end': int(self.time_str_to_seconds(lines[i+1].split(' ')[2]) * rate),
                        'text': lines[i+2]
                    }
                ret.append(dic)
            return ret

    def merge_no_speech(self, texts):
        # 连续多个< No Speech >合并成一个
        #print("before merge", texts)
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
        #print("after merge", texts)
        return ret

    def regular_text(self, text, char_per_line = -1):
        if text.endswith('。'):
            text = text[:-1]
        if text.find('\\n') != -1:
            return text
        if char_per_line > 0:
            arr = []
            for i in range(0, len(text), char_per_line):
                arr.append(text[i:i+char_per_line])
            text = '\\n'.join(arr)
        return text

    def write_srt(self, texts, srt_path, rate, char_per_line = -1, no_speech = 'keep'):
        '''
        支持三种情况：
        1. 有语音，无空白，生成空白 no_speech: create
        2. 有语音，有空白，保留空白 no_speech: keep
        3. 有语音，有空白，去掉空白 no_speech: remove
        '''
        if no_speech == 'keep':
            texts = self.merge_no_speech(texts)
        texts = self.merge_no_speech(texts)
        last = 0
        idx = 1
        with open(srt_path, "w", encoding='utf-8') as f:
            for dic in texts:
                text = dic['text']
                start = dic['start']/rate
                end = dic['end']/rate
                start_ms = int(start * 1000 % 1000)
                end_ms = int(end *1000 % 1000)
                if no_speech == 'create':
                    if start > last and len(text) > 0:
                        to = start
                        to_ms = start_ms
                        last_ms = int(last * 1000 % 1000)
                        f.write(f"{idx}\n")
                        idx+=1
                        f.write(f"{time.strftime('%H:%M:%S', time.gmtime(last))},{str(last_ms).zfill(3)} --> {time.strftime('%H:%M:%S', time.gmtime(to))},{str(to_ms).zfill(3)}\n")
                        f.write(f"< No Speech >\n\n")                    
                if no_speech != 'remove' or text != '< No Speech >':
                    text = self.regular_text(text, char_per_line)
                    if len(text) > 0:
                        f.write(f"{idx}\n")
                        idx+=1
                        f.write(f"{time.strftime('%H:%M:%S', time.gmtime(start))},{str(start_ms).zfill(3)} --> {time.strftime('%H:%M:%S', time.gmtime(end))},{str(end_ms).zfill(3)}\n")
                        if len(text) > 0:
                            f.write(f"{text}\n\n")
                        last = end
                    
def get_media_info(path):
    '''
    获取视频或音频的信息
    '''
    ret = {}
    if path.endswith('.mp3'):
        clip = AudioFileClip(path)
        ret['audio_sample_rate'] = clip.fps
        audio = clip
    else:
        clip = VideoFileClip(path)
        audio = clip.audio
        width, height = clip.size
        ret['width'] = width
        ret['height'] = height
        ret['audio_sample_rate'] = clip.audio.fps
    audio_arr = audio.to_soundarray(fps=22000)
    if len(audio_arr.shape) > 1:
        audio_arr = np.mean(audio_arr, axis=1)
    meter = Meter(rate=22000)  # 使用与音频相同的采样率
    ret['loudness'] = meter.integrated_loudness(audio_arr)
    ret['duration'] = clip.duration
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
