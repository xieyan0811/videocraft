English | [中文简体](./README_cn.md)

# VideoCraft

> Simplify the Process, Accelerate Creativity, Ignite Your Passion! ❇️

## Introduction

### Features

This is a video editing software that automatically enhances videos by optimizing accents, stutters, and mistakes through speech recognition, speech synthesis, and video editing technologies, producing high-quality videos.

### Use Cases

#### Scenario 1

When recording videos, issues like accents, stuttering, or verbal slips often arise. Achieving a satisfactory result typically requires multiple recordings, which is time-consuming and demanding. Additionally, using video editing software may increase the learning curve.

#### Scenario 2

Some authors may be dissatisfied with their voices or wish to use a more stable or unique voice. This tool helps achieve voice replacement with ease.

#### Scenario 3

This tool also serves as a simple solution for translating videos, converting Chinese videos into English ones and automatically adding subtitles.

While many may lack proficiency in English, this tool leverages natural language models to address this challenge. The workflow is as follows: extract text from the Chinese video and generate an SRT subtitle file; translate the SRT using an LLM while maintaining its format; finally, synthesize new English audio with the original video and English subtitles to create a new English video.

#### Solution

The video optimization tool leverages advanced speech recognition, speech synthesis, and video editing technologies to automate parts of the editing process, simplifying various aspects of video production.

* Automatically recognizes spoken content in videos and generates subtitles;
* Allows users to manually correct or translate subtitles to ensure content accuracy and fluency;
* Regenerates audio using corrected subtitles, removes unnecessary silent segments, and composes an optimized video with subtitles.

### Principle

For video editing, we primarily use the ffmpeg toolset.

For speech recognition and synthesis, we use tools from OpenAI and Microsoft, supporting online synthesis and recognition. These tools are easy to configure, have a low learning curve, and require minimal local resources. We also support local deployment of deep learning models like FunASR and GPT_SoVITS, saving on online synthesis costs and allowing for custom voice features.

For small conversion needs, consider using OpenAI's TTS (Text-to-Speech) or ASR (Automatic Speech Recognition) services; for larger conversions, consider setting up local ASR and TTS services for better performance.

## Usage

### Installation

Installation via Docker is recommended.

```shell
$ git clone https://github.com/xieyan0811/videocraft
$ cd videocraft
# To set up local speech recognition/synthesis models, modify requirements.txt and Dockerfile
$ docker build . -t videocraft:xxx 
# Edit docker-compose.yml to modify the new image name and volume path
$ docker-compose up -d
```

### Usage

``` shell
$ docker exec -it videocraft bash # Enter the container
$ cp default_env .env
# Set environment variables as needed
$ python main.py -g -v xxx.mp4 -o data/tmp.srt # Extract subtitles
# Manually edit subtitles; set the appropriate LANGUAGE_CODE environment variable if translation is needed
$ python main.py -m -v xxx.mp4 -s data/tmp.srt -o data/8da.mp4 # Merge video, subtitles, replace audio, and remove blank segments
```

## Notes

* Control speaking speed during recording to ensure the content is clear and understandable.
* When using edge_tts in mainland China, set up a proxy to avoid a 403 error.
* It is advisable to test with short videos initially and confirm success before processing full videos.

## License

This project is licensed under the MIT License. For more details, please refer to the [LICENSE](./LICENSE) file.

## Demo

[Example Video](https://www.bilibili.com/video/BV1mAQgYVE2S/)