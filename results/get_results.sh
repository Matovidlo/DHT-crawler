#!/usr/bin/bash

result=""
for filename in ../logs/nodes_timer/logF*.out; do
	result+=$(head -1 filename)
done
echo $result > outputF.txt

result=""
for filename in ../logs/nodes_timer/logH*.out; do
	result+=$(head -1 filename)
done
echo $result > outputH.txt
