'''
生成字幕
'''

import os
import traceback
import ffmpeg
import numpy as np

from slicer2 import Slicer
from scipy.io import wavfile
from ve_utils import SrtTools,get_media_info

TMP_PATH = '/tmp/audio/'

class VideoSrt:
    '''
    视频字幕生成
    '''
    _instance = None

    @staticmethod
    def get_instance():
        if VideoSrt._instance is None:
            VideoSrt._instance = VideoSrt()
        return VideoSrt._instance

    def __init__(self):
        self.model = None

    def load_audio(self, file: str, sr: int) -> np.ndarray:
        '''
        Load mp4 file's audio into numpy array.
        '''    
        try:
            out, _ = (
                ffmpeg.input(file, threads=0)
                .output("-", format="s16le", acodec="pcm_s16le", ac=1, ar=sr)
                .run(cmd=["ffmpeg", "-nostdin"], capture_stdout=True, capture_stderr=True)
            )
        except ffmpeg.Error as e:
            raise RuntimeError(f"Failed to load audio: {e.stderr.decode()}") from e

        return np.frombuffer(out, np.int16).flatten().astype(np.float32) / 32768.0

    def slice(self, audio_data, out_dir, rate, loudness):
        '''
        Slice audio data into pieces and save wav file to out_dir.
        '''
        ret = []
        _max = 0.9
        alpha = 0.25

        slicer = Slicer(
            sr=rate,  # 长音频采样率
            threshold=      int(loudness * 1.5),  # 音量小于这个值视作静音的备选切割点 # base -34
            min_length=     int(2000),  # 每段最小多长，如果第一段太短一直和后面段连起来直到超过这个值 # base 4000
            min_interval=   int(300),  # 最短切割间隔
            hop_size=       int(100),  # 怎么算音量曲线，越小精度越大计算量越高（不是精度越大效果越好）
            max_sil_kept=   int(500),  # 切完后静音最多留多长，**可调**
        )

        name = 'audio_slice'
        for chunk, start, end in slicer.slice(audio_data):  # start和end是帧数
            tmp_max = np.abs(chunk).max()
            if(tmp_max>1):chunk/=tmp_max
            chunk = (chunk / tmp_max * (_max * alpha)) + (1 - alpha) * chunk
            path = "%s/%s_%010d_%010d.wav" % (out_dir, name, start, end)
            wavfile.write(path, rate, (chunk * 32767).astype(np.int16))
            ret.append({'path':path, 'start':start, 'end':end})
        return ret

    def load_audio_model(self):
        from funasr import AutoModel
        path_asr  = 'tools/asr/models/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch'
        path_vad  = 'tools/asr/models/speech_fsmn_vad_zh-cn-16k-common-pytorch'
        path_punc = 'tools/asr/models/punc_ct-transformer_zh-cn-common-vocab272727-pytorch'
        path_asr  = path_asr  if os.path.exists(path_asr)  else "iic/speech_paraformer-large_asr_nat-zh-cn-16k-common-vocab8404-pytorch"
        path_vad  = path_vad  if os.path.exists(path_vad)  else "iic/speech_fsmn_vad_zh-cn-16k-common-pytorch"
        path_punc = path_punc if os.path.exists(path_punc) else "iic/punc_ct-transformer_zh-cn-common-vocab272727-pytorch"

        return AutoModel(
            model               = path_asr,
            model_revision      = "v2.0.4",
            vad_model           = path_vad,
            vad_model_revision  = "v2.0.4",
            punc_model          = path_punc,
            punc_model_revision = "v2.0.4",
        )

    def do_asr(self, model, files):
        arr = []
        for dic in files:
            try:
                dic['text'] = model.generate(input=dic['path'])[0]["text"]
            except:
                dic['text'] = ''
                print(traceback.format_exc())
            arr.append(dic)
        return arr

    def get_srt(self, video_path, srt_path, md_path, rate):
        '''
        convert video_path to srt file
        '''
        if self.model is None:
            self.model = self.load_audio_model()

        info = get_media_info(video_path)
        if info['width'] > info['height']:
            char_per_line = 25
        else:
            char_per_line = 14

        audio_data = self.load_audio(video_path, rate)
        print(f"duration {len(audio_data)/rate}")
        if not os.path.exists(TMP_PATH):
            os.makedirs(TMP_PATH)
        files = self.slice(audio_data, TMP_PATH, rate, info['loudness'])
        print(f'files {len(files)}')

        texts = self.do_asr(self.model, files)
        for x in files:
            os.remove(x['path'])

        # 去除text最后的所有静音段
        while len(texts) > 0 and texts[-1]['text'] == '< No Speech >':
            texts.pop()
        # 将最后一个段落延长到最后
        if len(texts) > 0:
            texts[-1]['end'] = len(audio_data)
        
        with open(md_path,'w') as f:
            for i,x in enumerate(texts):
                print(x['text'], x['start']/rate, x['end']/rate)
                f.write(f"{x['text']}\n")

        SrtTools.get_instance().write_srt(texts, srt_path, rate=rate, char_per_line=char_per_line, no_speech='create')
