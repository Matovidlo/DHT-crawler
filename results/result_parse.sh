#!/usr/bin/bash

# can be wc -l
if [ $1 -a -z $2 ]; then
	cat $1  | grep -v timestamp | grep -v "}" | sort | uniq 
	exit
elif [ "$2" == "infopool" ]; then
	# Get ip address
	act=$(date +"%F:%T")
	#cat $1 | grep -Pv "\s+\d+" | grep -Pv "\s+]," | grep -Pv "\s+\"\d+\.\d+" | sort 
	cat $1 | grep -Pv "\s+\d+" | grep -Pv "\s+]," | grep -P "\s+\"\d+\.\d+" | sort | uniq > "ip$act.txt"
	cat $1 | grep -Pv "\s+\d+" | grep -Pv "\s+]," | grep -Pv "\s+\"\d+\.\d+" | sort | uniq > "info$act.txt"
else
	echo "First argument should be file"
fi
