#!/usr/bin/bash

# IF first argument given, change it's duration
dur=600
if [ $1 ]; then
	dur=$1
fi

# TODO execute it multiple times and for longer duration to prove
# that we could not crawl whole space
# watch -d -n 5 ./src/exec.py --duration $dur
if [ ! -d "./logs" ]; then
	mkdir logs
fi

for i in `seq 1 24`;
do
	# start program 24 times, once per hour, print time of log, log$i.json
	# at the end of crawl get extraction of this results
	# TODO --country
	./src/exec.py --duration $dur $2 > ./logs/log$i.out
	sleep 3000
	# watch -n 5 ./src/exec.py --duration $dur > log.out
done
