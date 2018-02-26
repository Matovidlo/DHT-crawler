#Docker file for containerization of this application
# TODO add multiple platforms

# fedora 25,26,27,28
#

FROM fedora:27

MAINTAINER Martin Vasko <xvasko12@stud.fit.vutbr.cz> <matovidlo2@gmail.com>

LABEL description="Docker image with various OS and environment with python3.6 / python3.5"

RUN dnf install -y python36 python3-pip python3-devel gcc redhat-rpm-config
RUN pip3.6 install bencoder.pyx bencode

COPY . /monitoring/
# FIXME copy successful
# RUN ls -la /monitoring/*
# TODO hashlib

WORKDIR /monitoring

