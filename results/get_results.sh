#!/usr/bin/bash

find ../logs -size  0 -print0 |xargs -0 rm

# result=""
# for filename in ../logs/nodes_timer/logF*.out; do
# 	result+="$filename\n"
# 	result+=$(head -1 $filename)
# 	result+="\n"
# done
# echo -e $result > outputF.txt

# # Results for Chasing Corals
# # Peer set is processed

# sec=$(grep -Po "logF.*" outputF.txt)
# sec=$(echo "$sec" | grep -Po "\d+")
# val=$(grep -Po "\[PeerSet\]:\d+" outputF.txt)
# val=$(echo $val | grep -Po "\d+")

# for line in $val; do
# 	echo " $line )" >> val.txt
# done
# for line in $sec; do
# 	echo "( $line" >> sec.txt
# done

# result=$(paste -d ", " sec.txt val.txt)
# echo "$result" > ./graphs/resultPF.txt
# sort -k2 -n ./graphs/resultPF.txt > ./graphs/result.txt
# mv ./graphs/result.txt ./graphs/resultPF.txt
# echo -e "End of Peer Set Chasing Corals"

# rm val.txt
# # Results for Chasing Corals
# # Node set is processed
# val=$(grep -Po "\[NodeSet\]:\d+" outputF.txt)
# val=$(echo $val | grep -Po "\d+")
# for line in $val; do
# 	echo " $line )" >> val.txt
# done

# result=$(paste -d ", " sec.txt val.txt)
# echo "$result" > ./graphs/resultNF.txt
# sort -k2 -n ./graphs/resultNF.txt  > ./graphs/result.txt
# mv ./graphs/result.txt ./graphs/resultNF.txt
# echo -e "End of Node Set Chasing Corals"

# rm sec.txt
# rm val.txt

# # Better torrent file
# # More fluctuation
# # TODO average

# result=""
# for filename in ../logs/nodes_timer/logH*.out; do
# 	result+="$filename\n"
# 	result+=$(head -1 $filename)
# 	result+="\n"
# done
# echo -e $result > outputH.txt

# sec=$(grep -Po "logH.*" outputH.txt)
# sec=$(echo $sec | grep -Po "\d+")
# peer_val=$(grep -Po "\[PeerSet\]:\d+" outputH.txt)
# peer_val=$(echo $peer_val | grep -Po "\d+")

# for line in $peer_val; do
# 	echo " $line )" >> val.txt
# done
# for line in $sec; do
# 	echo "( $line" >> sec.txt
# done

# result=$(paste -d "," sec.txt val.txt)

# echo "$result" > ./graphs/resultH.txt
# sort -k2 -n ./graphs/resultH.txt  > ./graphs/result.txt
# mv ./graphs/result.txt ./graphs/resultH.txt
# echo -e "End of Peer Set infohash"

# rm sec.txt
# rm val.txt
# # TODO magnet link


# result=""
# connection=""
# for filename in ../logs/less_peers/*.out; do
# 	result+="$filename\n"
# 	# connection delay
# 	connection+="$filename\n"
# 	connection+=$(tail -1 $filename)
# 	connection+="\n"
# 	# sets
# 	result+=$(head -1 $filename)
# 	result+="\n"
# done

# echo -e $result > outputLess.txt
# echo -e $connection > connection.txt

# sec=$(grep -Po "log.*" outputLess.txt)
# sec=$(echo $sec | grep -Po "\d+")

# for line in $sec; do
# 	echo "($line" >> sec.txt
# done

# rm sec.txt
# echo "End magnet Peer Set"
# #######################
# ### LIFO AND FIFO QUEUE
# #######################

# # LIFO
# ######
# rm ./graphs/lifoH.txt
# rm ./graphs/fifoH.txt
# rm ./graphs/lifoNF.txt
# rm ./graphs/fifoNF.txt


# num_lines=$(cat ../logs/lifo_queue/logH1.out | wc -l)
# ret=0
# nodes=0
# for i in `seq 1 $num_lines`; do
# 	for filename in ../logs/lifo_queue/logH*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))

# 		value=$(echo "$result" | grep -Po "\[NodeSet\]:\d+" )
# 		value=$(echo $value | grep -Po "\d+")

# 		nodes=$((nodes + value))
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 200))
# 	echo "( $num, $result )" >> ./graphs/lifoH.txt
# 	result=$((nodes / 200))
# 	echo "( $num, $result )" >> ./graphs/lifoNF.txt
# 	nodes=0
# 	ret=0
# done

# cat ./graphs/4experiment.tex ./graphs/lifoH.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_peerresult.pdf

# # cat ./graphs/3experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# # make -C ./graphs
# # mv ./graphs/auto.pdf lifo_peerpercentage.pdf

# # rm error.txt
# # rm error_perc.txt

# # FIFO
# ######

# num_lines=$(cat ../logs/fifo_queue/logH1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	# if [ $i -ge 30 ]; then
# 	# 	break
# 	# fi
# 	for filename in ../logs/fifo_queue/logH*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))

# 		value=$(echo "$result" | grep -Po "\[NodeSet\]:\d+" )
# 		value=$(echo $value | grep -Po "\d+")

# 		nodes=$((nodes + value))
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 200))
# 	echo "( $num, $result )" >> ./graphs/fifoH.txt
# 	result=$((nodes / 200))
# 	echo "( $num, $result )" >> ./graphs/fifoNF.txt
# 	nodes=0
# 	ret=0
# done

# cat ./graphs/4experiment.tex ./graphs/fifoH.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_peerresult.pdf

# cat ./graphs/3experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_peerpercentage.pdf

# rm error.txt
# rm error_perc.txt



# #mv ./graphs/auto.pdf fifo_noderesult.pdf

# echo "End Lifo and Fifo Peer Set Node Set"


# # TEST
# ######

# # result=""
# # for filename in ../logs/test/logH*.out; do
# # 	result+="$filename\n"
# # 	result+=$(tail -1 $filename)
# # 	result+="\n"
# # done
# # echo -e $result > testF.txt

# # sec=$(grep -Po "logH.*" testF.txt)
# # sec=$(echo $sec | grep -Po "\d+")
# # peer_val=$(grep -Po "\[PeerSet\]:\d+" testF.txt)
# # peer_val=$(echo $peer_val | grep -Po "\d+")

# # for line in $peer_val; do
# # 	echo " $line )" >> val.txt
# # done
# # for line in $sec; do
# # 	echo "( $line" >> sec.txt
# # done

# # result=$(paste -d "," sec.txt val.txt)

# # echo "$result" > ./graphs/testF.txt
# # sort -k2 -n ./graphs/testF.txt  > ./graphs/result.txt
# # mv ./graphs/result.txt ./graphs/testF.txt

# # cat ./graphs/1experiment.tex ./graphs/testF.txt ./graphs/last.tex > ./graphs/auto.tex
# # make -C ./graphs
# # mv ./graphs/auto.pdf test_peers.pdf

# # rm val.txt

# # val=$(grep -Po "\[NodeSet\]:\d+" testF.txt)
# # val=$(echo $val | grep -Po "\d+")

# # for line in $val; do
# # 	echo " $line )" >> val.txt
# # done

# # result=$(paste -d ", " sec.txt val.txt)
# # echo "$result" > ./graphs/testNF.txt
# # sort -k2 -n ./graphs/testNF.txt  > ./graphs/result.txt
# # mv ./graphs/result.txt ./graphs/testNF.txt

# # cat ./graphs/2experiment.tex ./graphs/testNF.txt ./graphs/last.tex > ./graphs/auto.tex
# # make -C ./graphs
# # mv ./graphs/auto.pdf test_nodes.pdf


# # rm sec.txt
# # rm val.txt

# # TODO Avg script
# #./graphs/avg/avg.py
# ######################
# ######################
# # Average 120 process to 1 with distribution error
# ##################################################
# rm error.txt
# rm error_perc.txt

# num_lines=$(cat ../logs/error/logH1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	if [ $i -ge 30 ]; then
# 		break
# 	fi
# 	for filename in ../logs/error/logH*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))
# 		result+="\n"
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 120))
# 	echo "( $num, $result )" >> error.txt
# 	percentage=$(echo "(3000 - $result) / 3000" | bc -l)
# 	echo "( $num, $percentage )" >> error_perc.txt
# 	ret=0
# done

# cat ./graphs/7experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_error_peers.pdf

# cat ./graphs/3experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_error_percentage.pdf

# mv ./error_perc.txt lifo_error.txt

# rm error.txt
# rm error_perc.txt

# #################

# num_lines=$(cat ../logs/error/logF1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	if [ $i -ge 30 ]; then
# 		break
# 	fi
# 	for filename in ../logs/error/logF*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))
# 		result+="\n"
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 120))
# 	echo "( $num, $result )" >> error.txt
# 	percentage=$(echo "(3000 - $result) / 3000" | bc -l)
# 	echo "( $num, $percentage )" >> error_perc.txt
# 	ret=0
# done

# cat ./graphs/7experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_error_peers.pdf

# cat ./graphs/3experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_error_percentage.pdf

# rm error.txt
# rm error_perc.txt


# echo "End of LIFO and FIFO Peers error Greatest Showman"
# #####################################
# ########## Ubuntu lifo and fifo error
# #####################################

# num_lines=$(cat ../logs/lifo_less/logU1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	if [ $i -ge 100 ]; then
# 		break
# 	fi
# 	for filename in ../logs/lifo_less/logU*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))
# 		result+="\n"
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 200))
# 	echo "( $num, $result )" >> error.txt
# 	percentage=$(echo "(1000 - $result) / 1000" | bc -l)
# 	echo "( $num, $percentage )" >> error_perc.txt
# 	ret=0
# done

# cat ./graphs/8experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_ubuntu.pdf

# cat ./graphs/6experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_ubuntu_error_percentage.pdf

# rm error.txt
# rm error_perc.txt




# num_lines=$(cat ../logs/fifo_less/logH1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	if [ $i -ge 100 ]; then
# 		break
# 	fi
# 	for filename in ../logs/fifo_less/logH*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))
# 		result+="\n"
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 200))
# 	echo "( $num, $result )" >> error.txt
# 	percentage=$(echo "(1000 - $result) / 1000" | bc -l)
# 	echo "( $num, $percentage )" >> error_perc.txt
# 	ret=0
# done

# cat ./graphs/8experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_ubuntu.pdf

# cat ./graphs/6experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_ubuntu_error_percentage.pdf

# rm error.txt
# rm error_perc.txt

# echo "End ubuntu"
# ####################################################
# ################### Fedora error, less popular too
# ####################################################
# num_lines=$(cat ../logs/error/logFi1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	if [ $i -ge 100 ]; then
# 		break
# 	fi
# 	for filename in ../logs/error/logFi*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))
# 		result+="\n"
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 120))
# 	echo "( $num, $result )" >> error.txt
# 	percentage=$(echo "(100 - $result) / 100" | bc -l)
# 	echo "( $num, $percentage )" >> error_perc.txt
# 	ret=0
# done

# cat ./graphs/7experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_fedora_less.pdf

# cat ./graphs/3experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf fifo_fedora_error_percentage.pdf

# rm error.txt
# rm error_perc.txt

# #####################
# # LIFO
# #####################

# num_lines=$(cat ../logs/error/logLi1.out | wc -l)
# ret=0
# for i in `seq 1 $num_lines`; do
# 	if [ $i -ge 100 ]; then
# 		break
# 	fi
# 	for filename in ../logs/error/logLi*.out; do
# 		tmp=$(head -$i $filename)
# 		result=$(echo -e "$tmp" | tail -1)

# 		value=$(echo "$result" | grep -Po "\[PeerSet\]:\d+")
# 		value=$(echo "$value" | grep -Po "\d+")

# 		ret=$((ret + value))
# 		result+="\n"
# 	done
# 	num=$(($i * 5))
# 	result=$(($ret / 120))
# 	echo "( $num, $result )" >> error.txt
# 	percentage=$(echo "(100 - $result) / 100" | bc -l)
# 	echo "( $num, $percentage )" >> error_perc.txt
# 	ret=0
# done

# cat ./graphs/7experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_fedora_less.pdf

# cat ./graphs/3experiment.tex error_perc.txt ./graphs/last.tex > ./graphs/auto.tex
# make -C ./graphs
# mv ./graphs/auto.pdf lifo_fedora_error_percentage.pdf

# rm error.txt
# rm error_perc.txt

########################
# Bernoulli process LIFO and FIFO
########################
num_lines=$(cat ../logs/test/logBL1.out | wc -l)
num_lines=$((num_lines-1))
for i in `seq 1 $num_lines`; do
	value=0
	for filename in ../logs/test/logBL*.out; do
		tmp=$(head -$i $filename)
		result=$(echo -e "$tmp" | tail -1)

		value=$(echo "$result" | grep -Po "\[Bernoulli process\]:\s+\d+\.\d+")
		value=$(echo "$value" | grep -Po "\d+\.\d+")
	done
	num=$(($i * 5))
	echo "( $num, $value )" >> error.txt
done

cat ./graphs/10experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
make -C ./graphs
mv ./graphs/auto.pdf bernoulli_lifo.pdf

rm error.txt

num_lines=$(cat ../logs/test/logBF1.out | wc -l)
num_lines=$((num_lines-1))
for i in `seq 1 $num_lines`; do
	value=0
	for filename in ../logs/test/logBF*.out; do
		tmp=$(head -$i $filename)
		result=$(echo -e "$tmp" | tail -1)

		value=$(echo "$result" | grep -Po "\[Bernoulli process\]:\s+\d+\.\d+")
		value=$(echo "$value" | grep -Po "\d+\.\d+")
	done
	num=$(($i * 5))
	echo "( $num, $value )" >> error.txt
done

cat ./graphs/10experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
make -C ./graphs
mv ./graphs/auto.pdf bernoulli_fifo.pdf

rm error.txt


##########################
# UDP packet delay
##########################
ret=0
i=1
for filename in ../logs/respond/log*.out; do
	result=$(tail -1 $filename)
	value=$(echo "$result" | grep -Po "\d+\.\d+")
	ret=$(echo "$ret + $value" | bc -l)
	step=$((i*5))
	echo "( $step, $ret )" >> error.txt

	# increment
	i=$((i+1))
	ret=0
done
# result=$(echo "$ret / 100" | bc -l)
# echo $result
# echo "( 600, $result )" >> error.txt

cat ./graphs/11experiment.tex error.txt ./graphs/last.tex > ./graphs/auto.tex
make -C ./graphs
mv ./graphs/auto.pdf delay.pdf

rm error.txt



rm val.txt
rm sec.txt
rm outputLess.txt
rm testF.txt
rm outputH.txt
rm outputF.txt
rm lifoH.txt
rm fifoH.txt
rm lifo_error.txt
rm connection.txt