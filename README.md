### Linux 系统安装字体支持中文字幕

``` shell
$ cp res/simsun.ttf /usr/share/fonts/truetype/
$ cp res/SourceHanSansSC-VF.ttf /usr/share/fonts/truetype/
$ fc-cache -v
$ fc-list :lang=zh
```

### 安装支持工具

``` shell
$ apt-get install ffmpeg
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
$ python main.py -g -v /exports/tmp/240417/8da802015ec1f6fac1ea3e60da19c782.mp4 -o data/tmp.srt
$ python main.py -m -v /exports/tmp/240417/8da802015ec1f6fac1ea3e60da19c782.mp4 -s data/tmp.srt -o data/8da.mp4
```

=== 新增241016 ===
## 功能

本项目旨在制作一个视频后期处理自动化工具，实现视频的粗剪辑。

1. **AI音频替换**：将视频中的音频更换为AI生成的语音。
2. **字幕处理**：
- 自动生成提高准确性和可读性。
- 支持字幕手动调整
3. **停顿优化**：智能识别并去除视频中的无声片段，使内容更连贯。
## 容器操作

假设用户当前位于 /exports，视频数据存放于 `/exports/tmp/240417/xxx.mp4`, 之后生成的字幕、新视频将存于 `/exports/data/xxx.mp4` 和 `/exports/data/xxx.srt`

- 下载源码，制作镜像
```bash
cd /exports
mkdir -p tmp/240417 # 已有的视频放在该路径下
mkdir data
git clone https://github.com/xieyan0811/videocraft.git
cd videocraft
docker build -t videocraft:0.0.2 .
```
运行后服务器中存在一个 6.56GB 大小的 `videocraft:0.0.2` 镜像

- 启动服务

```bash
docker-compose up -d
```

- 进入容器
```bash
docker exec -it videocraft bash
```

检查容器映射路径
```bash
cd /exports/ # 路径预期包含tmp和data文件夹，如果没有需要创建
cd /workspace
```

- 调用脚本

将 `/exports/tmp/240417/8da802015ec1f6fac1ea3e60da19c782.mp4` 视频生成字幕 `data/tmp.srt`, 4min 多的视频，转成字幕后耗时约 2 分钟左右
```bash
python main.py -g -v /exports/tmp/240417/xxx.mp4 -o /exports/data/tmp.srt
```

根据视频、字幕生成配音后视频 `data/8da.mp4`
```bash
python main.py -m -v /exports/tmp/240417/xxx.mp4 -s /exports/data/tmp.srt -o /exports/data/8da.mp4
```

## 停止容器

```bash
cd /exports
docker-compose stop
```
## 问题及解答

如果用户数据和代码路径存放和上面不一致，请进入 docker-compose.yml 根据实际情况修改 volumes 下的路径。
修改示例：我的代码位于 `/root/test` 下，我的 mp4数据位于 `/root/test/tmp/240417/xxx.mp4`。修改docker-compose.yml 为
`/exports:/exports` -> `/root/test:/exports`
