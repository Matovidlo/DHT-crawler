#!/bin/bash

#################################
# Martin Vasko 3.FIT BIT	#
# Setup for bacherol thesis	#
# Installs docker		#
# Runs application tests	#
# Installs all necessary libs	#
#################################
# Sudo when install docker, if not
help()
{
	echo "Help message"
}

while [ $# -gt 0 ]
do
  opt=$1
  case $opt in
    "--help")
    	help
    	exit 0
    	;;
    "-h")
      help
      exit 0
      ;;
    "install")
      # NEED root pass
      if [ -f /etc/os-release ]; then
        # freedesktop.org and systemd
        . /etc/os-release
        OS=$NAME
        VER=$VERSION_ID
      elif type lsb_release >/dev/null 2>&1; then
        # linuxbase.org
        OS=$(lsb_release -si)
        VER=$(lsb_release -sr)
      elif [ -f /etc/lsb-release ]; then
        # For some versions of Debian/Ubuntu without lsb_release command
        . /etc/lsb-release
        OS=$DISTRIB_ID
        VER=$DISTRIB_RELEASE
      elif [ -f /etc/debian_version ]; then
        # Older Debian/Ubuntu/etc.
        OS=Debian
        VER=$(cat /etc/debian_version)
      elif [ -f /etc/SuSe-release ]; then
        # Older SuSE/etc.
        ...
      elif [ -f /etc/redhat-release ]; then
        # Older Red Hat, CentOS, etc.
        ...
      else
        # Fall back to uname, e.g. "Linux <version>", also works for BSD, etc.
        OS=$(uname -s)
        VER=$(uname -r)
      fi
      # FIXME we got all necessary
      echo -e "Operation system: " . $OS . " Version: " . $VER . "\n"
      echo "Remove older version of docker"
      echo -e "For next steps it is necessary to give sudo password!\n(Removal of old docker vesion, installing new one)"
      if [ "$OS" == "Fedora" ]; then
        sudo dnf remove docker docker-common docker-selinux docker-engine-selinux docker-engine
        sudo dnf -y install dnf-plugins-core
        sudo dnf confg-manager \
          --add-repo \
          https://download.docker.com/linux/fedora/docker-ce.repo
        sudo dnf -y install docker-devel
      fi
      exit 0
      ;;
    "run")
      # RUN program
      echo "Run "
      exit 0
      ;;
    "test")
      echo "Start unitest"
      exit 0
  esac
  shift
done
