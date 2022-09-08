FROM ubuntu:latest

ENV PYTHONIOENCODING=utf-8

RUN apt-get update --fix-missing && \
    apt-get install -y python3 libpq-dev && \
    apt-get install -y python3-pip ssh git

COPY server-key /opt/server-key

COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

COPY entrypoint.sh /entrypoint.sh
RUN eval `ssh-agent -s`
RUN ssh-add
RUN ssh-add server-key


WORKDIR /home/web/codes

