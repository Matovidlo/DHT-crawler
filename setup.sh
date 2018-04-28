#!/bin/bash

#################################
# Martin Vasko 3.FIT BIT	#
# Setup for bacherol thesis	#
# Installs docker		#
# Runs application tests	#
# Installs all necessary libs	#
#################################
# Sudo when install docker, if not


# Prerequisities:
# docker for using dockerfile
# python bencoder.pyx using pip
# python3 and more

# Testing:
# For testing you need to install bats.
# Most of scripts and runnable wihout any prerequisities
# There is possibility to install all necessities with ./setup install

help()
{
	echo "Usage: install-docker when you want to install docker."
	echo "\t this option can be enchanced with --remove_old to remove old docker."
	echo "\t also we can add --verify to verify, that docker is installed correctly."
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

			else
				# Other operation system
				case "$2" in
					"--remove_old")
						sudo apt-get remove docker docker-engine docker.io
						sudo apt-get update
						;;
					"--verify")
						verify=true
						;;
				esac
				case "$3" in
					"--remove_old")
						sudo apt-get remove docker docker-engine docker.io
						sudo apt-get update
						;;
					"--verify")
						verify=true
						;;
				esac
				sudo apt-get install docker-ce
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
				sudo dnf -y install python-devel python36 bats
				pip3.6 install --user bencoder.pyx bencode
			else
				sudo apt-get install -y build-essential libssl-dev libffi-dev python-dev
				sudo apt-get install -y python3-pip
				pip3 install --user bencoder.pyx bencode
			fi
			exit 0
			;;
		"run")
			# RUN program
			./src/exec.py --duration 60
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
			./tests/unit/tests.py
			exit 0
			;;
			
	esac
	shift
done

help
exit 0
