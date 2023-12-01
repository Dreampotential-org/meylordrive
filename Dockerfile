FROM ubuntu:latest

ENV PYTHONIOENCODING=utf-8

RUN apt-get update --fix-missing && \
    apt-get install -y python3 libpq-dev && \
    apt-get install -y python3-pip ssh git portaudio19-dev python3-pyaudio alsa-utils



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

