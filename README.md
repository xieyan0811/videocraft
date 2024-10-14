### Linux 系统安装字体支持中文字幕

``` shell
$ cp /opt/xieyan/tmp/240318/simsun.ttf /usr/share/fonts/truetype/
$ cp /opt/xieyan/tmp/SourceHanSansSC-VF.ttf /usr/share/fonts/truetype/
$ fc-cache -v
$ fc-list :lang=zh
```

### 程序列表
* main.py 程序入口
* tts.py  语音合成
* ve_asr.py   字幕识别
* ve_clip.py  视频合成
* ve_config.py  配置文件
* ve_utils.py 字幕等相关工具支持

### 录音注意事项
* 控制语速


### 调用示例
``` shell
$ python main.py -g -v /opt/xieyan/tmp/240417/8da802015ec1f6fac1ea3e60da19c782.mp4 -o data/tmp.srt
$ python main.py -m -v /opt/xieyan/tmp/240417/8da802015ec1f6fac1ea3e60da19c782.mp4 -s /opt/xieyan/git/GPT-SoVITS_cmd/video_edit/data/tmp.srt -o /opt/xieyan/git/GPT-SoVITS_cmd/video_edit/data/8da.mp4
```