#!/usr/bin/bash

# IF first argument given, change it's duration
dur=600
if [ $1 ]; then
	dur=$1
fi

# TODO execute it multiple times and for longer duration to prove 
# that we could not crawl whole space
#watch -d -n 5 ./src/exec.py --duration $dur
watch -n 5 ./src/exec.py --duration $dur > log.out
