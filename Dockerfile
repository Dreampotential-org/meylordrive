FROM ubuntu:latest

ENV PYTHONIOENCODING=utf-8

RUN apt-get update --fix-missing && \
    apt-get install -y wget libpq-dev mtools && \
    apt-get install -y ssh git portaudio19-dev python3-pyaudio alsa-utils

RUN wget https://www.python.org/ftp/python/3.11.0/Python-3.11.0.tgz && \
	tgz -x Python-3.11.0.tgz && cd Python-3.11.0 && \
	./configure --enable-optimizations && make sudo make install 



COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt
RUN apt install portaudio19-dev python3-pyaudio

COPY entrypoint.sh /entrypoint.sh
# RUN eval `ssh-agent -s`
# RUN ssh-add
# RUN ssh-add /opt/server-key
# RUN chmod 600 /opt/server-key
# RUN chown ubuntu:ubuntu /opt/server-key


WORKDIR /home/web/codes

