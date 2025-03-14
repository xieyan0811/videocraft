# VideoCraft

> 简化难度，快速推进，让创作更有动力！❇️

## 介绍

### 功能

这是一个视频编辑软件，通过语音识别、语音合成和视频剪辑技术，自动优化视频中的口音、结巴和说错问题，生成高质量的视频。

### 使用场景

#### 场景一

在录制视频时，我们常常遇到录制者的口音、结巴或口误等问题。为了获得满意的成品，往往需要多次反复录制，不仅耗时耗力，还可能需要借助视频编辑软件，增加了学习成本。

#### 场景二

有些作者可能对自己的声音不满意，或希望使用更稳定或具特色的声音。本工具可帮助您轻松实现声音替换。

#### 场景三

这还是一个用于视频翻译的简洁工具，能够将中文视频转换为英文视频并自动添加字幕。

很多人可能不具备熟练的英语说写能力，但通过结合自然语言模型，使用本工具即可轻松解决此难题。工作流程如下：首先提取中文视频中的文字并生成 SRT 字幕文件；然后借助 LLM 在保持格式的同时翻译 SRT；最终，将生成的新英文语音与原视频、英文字幕合成为全新的英文视频。

#### 解决方案

视频优化工具利用先进的语音识别、语音合成和视频剪辑技术，自动化部分编辑功能，简化视频制作的各个环节。

* 自动识别视频语音内容并生成字幕；
* 允许用户手动修正或翻译字幕，保证内容准确流畅；
* 使用修正后的字幕再次生成语音，去除多余的静音片段，调节音量，最终合成带字幕的优化视频。

### 原理

在视频编辑方面，主要使用 ffmpeg 系列工具来进行处理。

在语音识别和语音合成方面，我们使用了 OpenAI 和微软的系列工具，支持在线语音合成与识别，这些工具配置简单，学习成本低，并且占用较少的本地资源。此外，我们还支持在本地部署 FunASR 和 GPT_SoVITS 等深度学习模型，这种方式可以节省在线合成的费用，还能定制专属于自己的语音特色。

如果转换量较小，建议使用 OpenAI 的 TTS（文本到语音转换）或 ASR（自动语音识别）服务；如果转换量较大，请考虑自行搭建本地的 ASR 和 TTS 服务，以获取更佳的效果。

## 使用

### 安装

建议通过 docker 安装使用

```shell
$ git clone https://github.com/xieyan0811/videocraft
$ cd videocraft
# 如需在搭建本地语音识别/合成模型，请修改 requirements.txt 和 Dockerfile
$ docker build . -t videocraft:xxx 
# 编辑 docker-composite.yml，修改新镜像名及volume路径
$ docker-compose up -d

请先修改再运行

1. **`videocraft/Dockerfile`**: 使用代理或国内镜像源，缩短安装时间。
2. **`videocraft/docker-compose.yml`**: 自定义镜像名及volume路径。
3. **`videocraft/default_env`**: 在中国大陆使用 `edge_tts` 时，设置代理以防止 403 错误。
4. 如需在搭建本地语音识别/合成模型，请修改 requirements.txt (可选)

``` shell
$ docker build . -t videocraft:xxx 
$ docker-compose up -d
```

运行后服务器中存在一个不到2G 的 `videocraft:xxx` 镜像

### 调用

``` shell
$ docker exec -it videocraft bash # 进入容器
$ cp default_env .env
# 按需设置环境变量
$ python main.py -g -v xxx.mp4 -o data/tmp.srt # 提取字幕
# 手动编辑字幕，如果需要翻译字幕，注意设置相应的 LANGUAGE_CODE 环境变量
$ python main.py -m -v xxx.mp4 -s data/tmp.srt -o data/8da.mp4 # 合并视频，字幕，替换语音，去掉空白片断
```

## 注意事项

* 录音时请注意控制语速，确保内容清晰易懂。
* 建议先用短视频进行测试，确认无误后再处理正式长视频。
* 路径说明
    **输入**：自定义原始视频路径，运行首个命令时指定。
    **输出**：
        首个命令生成字幕文件，存放于 `data/tmp.srt`。
        第二个命令生成配音视频，存放于 `data/8da.mp4`。

## 许可证

此项目是根据 MIT 许可证授权的。有关详细信息，请参阅 [LICENSE](./LICENSE) 文件。

## 示例视频

[B站视频链接](https://www.bilibili.com/video/BV18ZQuY2ETP/)