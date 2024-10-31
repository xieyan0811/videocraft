FROM cnstark/pytorch:2.0.1-py3.9.17-cuda11.8.0-ubuntu20.04

ENV DEBIAN_FRONTEND=noninteractive
ENV TZ=Etc/UTC
RUN apt-get update && \
    apt-get install -y --no-install-recommends tzdata ffmpeg libsox-dev parallel aria2 git git-lfs vim openssh-server && \
    git lfs install && \
    rm -rf /var/lib/apt/lists/*

COPY res/simsun.ttf /usr/share/fonts/truetype/
COPY res/SourceHanSansSC-VF.ttf /usr/share/fonts/truetype/
COPY res/sshd_config /etc/ssh/sshd_config
RUN fc-cache -v
RUN fc-list :lang=zh
RUN /etc/init.d/ssh restart
RUN echo "root:1" | chpasswd

WORKDIR /workspace
COPY requirements.txt /workspace/
RUN pip install --no-cache-dir -r requirements.txt

ARG IMAGE_TYPE=full

COPY . /workspace

CMD ["/usr/sbin/sshd", "-D"]
