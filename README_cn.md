## 介绍

### 功能

这是一个视频编辑软件，通过语音识别、语音合成和视频剪辑技术，自动优化视频中的口音、结巴和说错问题，生成高质量的视频。

### 使用场景

我们在录制视频时，常常会遇到录制者带有口音、说话结巴或说错内容等问题。为了得到一个满意的成品，往往需要反复多次录制，这不仅耗时耗力，有时还需要借助视频编辑软件，而这又带来了一定的学习成本。

本软件可以被视为一种视频优化工具，它利用语音识别、语音合成和视频剪辑等技术，将部分编辑功能自动化，从而简化视频制作流程。

* 用户可以通过命令，自动识别视频中的语音内容并生成相应的字幕；
* 用户可以手动编辑生成的字幕，修正其中的错误或不流畅的部分；
* 用户再次通过命令，利用已修正的字幕重新生成语音，并将原始视频、修正后的字幕以及新的音频进行组合，同时去除多余的无语音部分，最终生成一个全新的、优化后的视频。

## 使用方法

### 安装方法

建议通过 docker 安装使用

```shell
$ git clone https://github.com/xieyan0811/videocraft
$ cd videocraft
# 如需在搭建本地语音识别/合成模型，请修改 requirements.txt
$ docker build. -t videocraft:xxx # 请调整 docker-composite.yml 中对应的镜像名
$ docker-composite up -d
```

### 使用方法

``` shell
$ cp default_env .env
# 按需设置环境变量
$ python main.py -g -v xxx.mp4 -o data/tmp.srt # 提取字幕
# 手动编辑字幕，如果需要翻译字幕，注意设置相应的 LANGUAGE_CODE 环境变量
$ python main.py -m -v xxx.mp4 -s data/tmp.srt -o data/8da.mp4 # 合并视频，字幕，替换语音，去掉空白片断
```

## 程序说明

### 程序列表

* main.py 程序入口
* tts.py 语音合成
* ve_slicer.py 音频切片
* ve_asr.py 字幕识别
* ve_clip.py 视频合成
* ve_config.py 配置文件
* ve_utils.py 字幕等相关工具支持

### 注意事项

* 录音时请注意控制语速，确保清晰可懂。
* 在中国大陆使用 edge_tts 时，需要设置代理，否则可能会遇到 403 错误。
* 进行测试时，建议先使用一个短视频进行试验，确保没有问题后再转换正式的长视频。
* 如果转换量不大，建议使用 OpenAI 的 TTS 或 ASR 服务，配置环境比较简单。
* 如果转换量大，请自行搭建本地 ASR 和 TTS 服务，虽然麻烦，但效果较好。