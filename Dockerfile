FROM ubuntu:latest

ENV PYTHONIOENCODING=utf-8

RUN apt-get update --fix-missing && \
    apt-get install -y python3 libpq-dev && \
    apt-get install -y python3-pip


COPY ./requirements.txt /tmp/requirements.txt

RUN pip3 install -r /tmp/requirements.txt

COPY entrypoint.sh /entrypoint.sh

WORKDIR /home/web/codes

