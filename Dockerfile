#Docker file for containerization of this application
# TODO add multiple platforms

# FIXME Archlinux
# fedora 25,26,27,28
#
ARG distribution
ARG version=latest
FROM $distribution:$version

MAINTAINER Martin Vasko <xvasko12@stud.fit.vutbr.cz> <matovidlo2@gmail.com>

LABEL description="Docker image with various OS and environment with python3.6 / python3.5"

# Fedora condition
RUN . /etc/os-release
RUN if [ "$NAME" == "fedora" ]; then dnf install -y python36 python3-pip python3-devel gcc redhat-rpm-config; pip3.6 install bencoder.pyx bencode; fi
#debian like distributions
# Ubuntu:latest
RUN if [ "$NAME" == "ubuntu" ]; then apt-get update; apt-get install -y python3-all-dev python3-pip; pip3 install bencoder.pyx bencode; fi

COPY . /monitoring/
# FIXME copy successful
# RUN ls -la /monitoring/*
# TODO hashlib

WORKDIR /monitoring

