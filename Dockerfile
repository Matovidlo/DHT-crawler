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

# Maybe rework to ENV variable
COPY . /monitoring/

# Fedora condition
RUN cat /etc/*-release | grep "NAME=Fedora" | grep =.* | cut -d "=" -f2 > /monitoring/name.txt
RUN if test $(cat /monitoring/name.txt) = "Fedora" ; then dnf install -y python36 python3-pip python3-devel gcc redhat-rpm-config; fi
RUN if test $(cat /monitoring/name.txt) = "Fedora" ; then pip3.6 install bencoder.pyx bencoder --user; fi

#debian like distributions
# Ubuntu:latest
RUN cat /etc/*-release | grep DISTRIB_ID | grep -o =.* | cut -d "=" -f 2 > /monitoring/name.txt
RUN if test $(cat /monitoring/name.txt)  = "Ubuntu" ; then apt-get update; apt-get install -y python3-all-dev python3-pip; fi
RUN if test $(cat /monitoring/name.txt) = "Ubuntu" ; then pip3 install bencoder.pyx bencoder urllib3 --user; fi
# RUN ls -la /monitoring/*

WORKDIR /monitoring
RUN ./setup.sh install
