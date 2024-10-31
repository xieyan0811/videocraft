English | [中文简体](./README_cn.md)

## Introduction

### Features

This is a video editing software that utilizes voice recognition, speech synthesis, and video editing technologies to automatically optimize issues like accent, stuttering, and errors in speech within videos, producing high-quality videos.

### Use Cases

When recording videos, we often encounter issues such as accents, stuttering, or incorrect content spoken by the recorder. To achieve a satisfactory final product, multiple takes are often required, which is time-consuming and labor-intensive. Sometimes, video editing software is needed, which adds to the learning curve.

This software can be viewed as a video optimization tool that automates some editing functions using technologies like voice recognition, speech synthesis, and video editing, thereby simplifying the video production process.

* Users can automatically recognize the audio content in a video and generate corresponding subtitles through commands;
* Users can manually edit the generated subtitles to correct errors or parts that are not smooth;
* By using commands again, users can regenerate audio using the corrected subtitles and combine the original video, corrected subtitles, and new audio while removing unnecessary non-audio segments, resulting in a new, optimized video.

## Usage

### Installation

It is recommended to install using Docker.

```shell
$ git clone https://github.com/xieyan0811/videocraft
$ cd videocraft
# Modify requirements.txt if you need to set up a local voice recognition/synthesis model
$ docker build . -t videocraft:xxx # Please adjust the image name in docker-compose.yml accordingly
$ docker-compose up -d
```

### How to Use

``` shell
$ cp default_env .env
# Set environment variables as needed
$ python main.py -g -v xxx.mp4 -o data/tmp.srt # Extract subtitles
# Manually edit subtitles, if subtitles need to be translated, ensure to set the appropriate LANGUAGE_CODE environment variable
$ python main.py -m -v xxx.mp4 -s data/tmp.srt -o data/8da.mp4 # Merge video, subtitles, replace audio, remove blank segments
```

## Program Description

### Program List

* main.py - Program entry
* tts.py - Speech synthesis
* ve_slicer.py - Audio slicing
* ve_asr.py - Subtitle recognition
* ve_clip.py - Video synthesis
* ve_config.py - Configuration file
* ve_utils.py - Support tools for subtitles, etc.

### Notes

* During recording, please pay attention to controlling speech speed to ensure clarity.
* When using edge_tts in mainland China, a proxy is required; otherwise, a 403 error may occur.
* For testing, it is recommended to start with a short video to ensure no issues before converting the official long video.
* If the conversion volume is small, it is recommended to use OpenAI's TTS or ASR services, as the configuration is relatively simple.
* If the conversion volume is large, it is recommended to set up local ASR and TTS services, which, although complicated, provide better results.