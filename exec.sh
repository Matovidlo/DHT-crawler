#!/usr/bin/bash

# IF first argument given, change it's duration
dur=600
if [ $1 ]; then
	dur=$1
fi

watch -n 5 ./src/processOutput.py --duration $dur
