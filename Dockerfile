FROM ubuntu:latest

ENV PYTHONIOENCODING=utf-8

RUN apt-get update --fix-missing && \
    apt-get install -y wget libpq-dev mtools && \
    apt-get install -y ssh git portaudio19-dev python3-pyaudio alsa-utils


RUN apt-get update --fix-missing
RUN apt-get install -y build-essential \
		  checkinstall \
		  libssl-dev \
		  # libsqlite3-dev \
		  # tk-dev \
		  # libgdbm-dev \
		  # libc6-dev \
		  libbz2-dev \
		  zlib1g-dev \
		  openssl \
		  libffi-dev \
		  python3-pip \
		  # python3-setuptools \
		  ffmpeg \
		  wget


RUN apt-get install -y locales
RUN apt-get install -y ffmpeg



COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt --break-system-packages --ignore-installed cryptography
RUN apt install portaudio19-dev python3-pyaudio

COPY entrypoint.sh /entrypoint.sh
# RUN eval `ssh-agent -s`
# RUN ssh-add
# RUN ssh-add /opt/server-key
# RUN chmod 600 /opt/server-key
# RUN chown ubuntu:ubuntu /opt/server-key


WORKDIR /home/web/codes

