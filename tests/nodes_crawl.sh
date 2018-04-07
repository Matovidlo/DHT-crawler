#!/usr/bin/bash
if [ ! -d "../logs/nodes_timer" ]; then
	mkdir ../logs/nodes_timer
fi

for i in `seq 600 800`;
do
	../src/exec.py --duration $i --file ../examples/Chasing\ Coral\ \(2017\)\ \[WEBRip\]\ \[1080p\]\ \[YTS.AM\].torrent > ../logs/nodes_timer/logF$i.out
	sleep 1
	../src/exec.py --duration $i --hash 11516A493655C6ED33E0B12D6BA9C70C9F2E22AA --bind_port 6693 > ../logs/nodes_timer/logH$i.out
done
