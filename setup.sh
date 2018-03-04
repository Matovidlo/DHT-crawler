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

verify()
{
	sudo systemctl start docker
	sudo docker run hello-world
}

get_os()
{
	if [ -f /etc/os-release ]; then
		# freedesktop.org and systemd
		. /etc/os-release
		local OS=$NAME
		local VER=$VERSION_ID
	elif type lsb_release >/dev/null 2>&1; then
		# linuxbase.org
		local OS=$(lsb_release -si)
		local VER=$(lsb_release -sr)
	elif [ -f /etc/lsb-release ]; then
		# For some versions of Debian/Ubuntu without lsb_release command
		. /etc/lsb-release
		local OS=$DISTRIB_ID
		local VER=$DISTRIB_RELEASE
	elif [ -f /etc/debian_version ]; then
		# Older Debian/Ubuntu/etc.
		local OS=Debian
		local VER=$(cat /etc/debian_version)
	elif [ -f /etc/SuSe-release ]; then
		# Older SuSE/etc.
		...
	elif [ -f /etc/redhat-release ]; then
		# Older Red Hat, CentOS, etc.
		...
	else
		# Fall back to uname, e.g. "Linux <version>", also works for BSD, etc.
		local OS=$(uname -s)
		local VER=$(uname -r)
	fi
	echo "$OS"
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
		"install-docker")
			# NEED root pass
			OS=$(get_os)
			# FIXME we got all necessary
			echo -e "Operation system: " . $OS . " Version: " . $VER . "\n"
			echo "Remove older version of docker"
			echo -e "For next steps it is necessary to give sudo password!\n(Removal of old docker vesion, installing new one)"
			if [ "$OS" == "Fedora" ]; then
				verify=false
				case "$2" in
					"--remove_old")
						sudo dnf remove docker docker-common docker-selinux docker-engine-selinux docker-engine
						sudo dnf -y install dnf-plugins-core
						;;
					# verify that all is installed correctly
					"--verify")
						verify=true
						;;
				esac
				# alias
				case "$3" in
					"--remove_old")
						sudo dnf remove docker docker-common docker-selinux docker-engine-selinux docker-engine
						sudo dnf -y install dnf-plugins-core
						;;
					# verify that all is installed correctly
					"--verify")
						verify=true
						;;
				esac
				# Install
				sudo dnf config-manager \
					--add-repo \
					https://download.docker.com/linux/fedora/docker-ce.repo
				sudo dnf -y install docker-devel docker-ce bats
				grep 'docker' /etc/group | grep $USER
				if [ $? -eq 1 ]; then
					sudo groupadd docker
					sudo usermod -aG docker $USER
					session=$(echo $DESKTOP_SESSION | grep -Eo gnome)
					if [ "$session" == "gnome" ]; then
						gnome-session-quit
					fi
				fi
				# Verify

				if [ $verify = true ]; then
					verify
				fi

			fi
			exit 0
			;;

		"install")
			OS=$(get_os)
			echo -e "Operation system: " . $OS
			if [ "$OS" == "Fedora" ]; then
				sudo dnf -y install python-devel python36
				pip3.6 install bencoder hashlib
			fi
			exit 0
			;;
		"run")
			# RUN program
			./src/monitor.py
			exit 0
			;;
		"run-docker")
			sudo systemctl status docker &> /dev/null
			if [ $? == 3 ]; then
				sudo systemctl start docker
			fi
			docker build -t monitor-dht . --build-arg distribution=fedora --build-arg version=27
			docker run --rm --name monitor-dht -v /$(pwd):/monitoring monitor-dht ./setup.sh run
			exit 0
			;;
		"test")
			echo "Start unitest"
			# TODO bats
			# bats
			exit 0
	esac
	shift
done

exit 0
