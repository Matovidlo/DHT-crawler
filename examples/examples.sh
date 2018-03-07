#!/usr/bin/bash

# monitor for 600 seconds = 10 minutes
act=$(date +"%F:%T")
# TODO country
#../src/exec.py --duration 60 --country > "../results/$act.json"
#../results/result_parse.sh "../results/$act.json" country

# 60 second example
../src/exec.py --duration 60 > "../results/$act.json"
../results/result_parse.sh "../results/$act.json" infopool

# 30 second example with torrent
../src/exec.py --duration 30 --file dht_example.torrent > "../results/$act.json" 
../results/result_parse.sh "../results/$act.json" infopool

# only infohash
../src/exec.py --duration 10 --hash 
