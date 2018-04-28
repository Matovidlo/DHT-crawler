#!/usr/bin/bash

# fifo fronta
../../dht_crawler/exec.py --duration 120 --db_format --fifo --file \
	../../examples/Chasin_Coral2017_1080p.torrent --bind_port 1234 > ../../logs/client_send/send.out
sleep 1
python3 ../../logs/client-socket.py -s ../../logs/client_send/send.out

# lifo fronta
../../dht_crawler/exec.py --duration 120 --db_format --file \
	../../examples/Chasin_Coral2017_1080p.torrent --bind_port 1234 > ../../logs/client_send/send.out
sleep 1
python3 ../../logs/client-socket.py -s ../../logs/client_send/send.out
