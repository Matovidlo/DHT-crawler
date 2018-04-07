#!/usr/bin/bash
if [ ! -d "../logs/nodes_timer" ]; then
	mkdir ../logs/nodes_timer
fi

for i in `seq 1 1600`;
do
	../src/exec.py --duration $i --file ../examples/Chasing\ Coral\ \(2017\)\ \[WEBRip\]\ \[1080p\]\ \[YTS.AM\].torrent > ../logs/nodes_timer/log$i.out
	sleep 1
done
