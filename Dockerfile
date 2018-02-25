#Docker file for containerization of this application
FROM fedora25

MAINTAINER Martin Vasko <xvasko12@stud.fit.vutbr.cz> <matovidlo2@gmail.com>

LABEL description="Docker image with various OS and environment with python3.6 / python3.5"

RUN dnf install -y python3.6 pip
RUN pip install bencoder hashlib collections socket random

WORKDIR /monitoring

