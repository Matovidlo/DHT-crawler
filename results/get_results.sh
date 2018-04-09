#!/usr/bin/bash

# TODO execute test before??

result=""
for filename in ../logs/nodes_timer/logF*.out; do
	result+="$filename\n"
	result+=$(head -1 $filename)
	result+="\n"
done
echo -e $result > outputF.txt

# Results for Chasing Corals
# Peer set is processed

sec=$(grep -Po "logF.*" outputF.txt)
sec=$(echo "$sec" | grep -Po "\d+")
val=$(grep -Po "\[PeerSet\]:\d+" outputF.txt)
val=$(echo $val | grep -Po "\d+")

for line in $val; do
	echo " $line )" >> val.txt
done
for line in $sec; do
	echo "( $line" >> sec.txt
done

result=$(paste -d ", " sec.txt val.txt)
echo "$result" > ./graphs/resultPF.txt
sort -k2 -n ./graphs/resultPF.txt > ./graphs/result.txt
mv ./graphs/result.txt ./graphs/resultPF.txt
echo -e "End of Peer Set Chasing Corals"

rm val.txt
# Results for Chasing Corals
# Node set is processed
val=$(grep -Po "\[NodeSet\]:\d+" outputF.txt)
val=$(echo $val | grep -Po "\d+")
for line in $val; do
	echo " $line )" >> val.txt
done

result=$(paste -d ", " sec.txt val.txt)
echo "$result" > ./graphs/resultNF.txt
sort -k2 -n ./graphs/resultNF.txt  > ./graphs/result.txt
mv ./graphs/result.txt ./graphs/resultNF.txt
echo -e "End of Node Set Chasing Corals"

rm sec.txt
rm val.txt

# Better torrent file
# More fluctuation
# TODO average

result=""
for filename in ../logs/nodes_timer/logH*.out; do
	result+="$filename\n"
	result+=$(head -1 $filename)
	result+="\n"
done
echo -e $result > outputH.txt

sec=$(grep -Po "logH.*" outputH.txt)
sec=$(echo $sec | grep -Po "\d+")
peer_val=$(grep -Po "\[PeerSet\]:\d+" outputH.txt)
peer_val=$(echo $peer_val | grep -Po "\d+")

for line in $peer_val; do
	echo " $line )" >> val.txt
done
for line in $sec; do
	echo "( $line" >> sec.txt
done

result=$(paste -d "," sec.txt val.txt)

echo "$result" > ./graphs/resultH.txt
sort -k2 -n ./graphs/resultH.txt  > ./graphs/result.txt
mv ./graphs/result.txt ./graphs/resultH.txt
echo -e "End of Peer Set infohash"

rm sec.txt
rm val.txt
# TODO magnet link


result=""
connection=""
for filename in ../logs/less_peers/*.out; do
	result+="$filename\n"
	# connection delay
	connection+="$filename\n"
	connection+=$(tail -1 $filename)
	connection+="\n"
	# sets
	result+=$(head -1 $filename)
	result+="\n"
done

echo -e $result > outputLess.txt
echo -e $connection > connection.txt

sec=$(grep -Po "log.*" outputLess.txt)
sec=$(echo $sec | grep -Po "\d+")

for line in $sec; do
	echo "($line" >> sec.txt
done

rm sec.txt


