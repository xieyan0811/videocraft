import os
import torch
import config as global_config
import soundfile as sf
import numpy as np

from scipy.signal import resample
from ve_utils import SrtTools

from command.inference import get_tts_wav, g_infer # 时间很长，后面优化 (g_infer)

TMP_WAV = '/tmp/output.wav'

class TtsTools:
    _instance = None

    @staticmethod
    def get_instance():
        if TtsTools._instance is None:
            TtsTools._instance = TtsTools()
        return TtsTools._instance
    
    def __init__(self):
        self.config = global_config.Config()
        os.chdir('/opt/xieyan/git/GPT-SoVITS_cmd')

        self.dic_args = {'model_name':'zhaozx',
                    'sovits_path':self.config.sovits_path,
                    'gpt_path':self.config.gpt_path,
                    'default_refer_path':'',
                    'default_refer_text':'',
                    'default_refer_language':'',
                    'device':"cuda" if torch.cuda.is_available() else "cpu",
                    'bind_addr':'0.0.0.0',
                    'port':9880,
                    'full_precision':False,
                    'half_precision':False,
                    'hubert_path':self.config.cnhubert_path,
                    'bert_path':self.config.bert_path}

        g_infer.load(self.config, self.dic_args)

    def handle(self, refer_wav_path, prompt_text, prompt_language, text, text_language):
        '''
        合成一句音频
        '''
        if (
                refer_wav_path == "" or refer_wav_path is None
                or prompt_text == "" or prompt_text is None
                or prompt_language == "" or prompt_language is None
        ):
            refer_wav_path, prompt_text, prompt_language = (
                g_infer.model_info.path,
                g_infer.model_info.text,
                g_infer.model_info.language,
            )
            if not g_infer.model_info.is_ready():
                return None

        text = text.replace('\\n', '')
        with torch.no_grad():
            gen = get_tts_wav(
                refer_wav_path, prompt_text, prompt_language, text, text_language
            )
            sampling_rate, audio_data = next(gen)

        sf.write(TMP_WAV, audio_data, sampling_rate, format="wav")
        torch.cuda.empty_cache()
        if self.dic_args['device'] == "mps":
            print('executed torch.mps.empty_cache()')
            torch.mps.empty_cache()

    def do_tts(self, in_srt_path, out_mp3_path, out_srt_path, rate):
        '''
        生成音频
        '''
        tts_rate = 32000 # 先以 tts_rate 为基准构建音频
        scale = tts_rate / rate
        texts_in = SrtTools.get_instance().read_srt(in_srt_path, unit='frame', 
                                                rate=tts_rate)
        texts_out = []
        g_infer.load(self.config, self.dic_args)
        #g_infer.hps.data.sampling_rate = rate # 设了没用
        pos = 0
        data = np.zeros(0)

        for x in texts_in:
            length = (x['start'] - pos)
            #print("@@@@@@@@@@@@@@@@@@@@@@@", x['text'], x['start'], x['end'], pos)
            if length > 0:
                silence = np.zeros(int(length))
                data = np.concatenate([data, silence])
            if x['text'] != '< No Speech >':
                self.handle(None, None, None, x['text'], 'zh')
                audio_data_1,r = sf.read(TMP_WAV)
            else:
                audio_data_1 = np.zeros(int(x['end']-x['start']))
            pos_start = len(data)
            data = np.concatenate([data, audio_data_1])
            pos = len(data)
            x_new = {'start':pos_start, 'end':pos, 'text':x['text']}
            texts_out.append(x_new)
            print("####", (x['start'] + int(len(audio_data_1))), pos)
        
        if rate != tts_rate:
            resampled_data = resample(data, int(len(data) // scale))
        sf.write(out_mp3_path, resampled_data, rate, format="wav")
        SrtTools.get_instance().write_srt(texts_out, out_srt_path, rate=tts_rate, no_speech='keep')
