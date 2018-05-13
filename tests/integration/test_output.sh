#!/usr/bin/bash

../../dht_crawler/exec.py --duration 120 --db_format  --file \
	../../examples/Chasin_Coral2017_1080p.torrent --bind_port 1234

../../dht_crawler/exec.py --duration 120 --print_as_country  --file \
	../../examples/Chasin_Coral2017_1080p.torrent --bind_port 1234
echo
echo "Print country with DB fromat"
echo
../../dht_crawler/exec.py --duration 120 --db_format --print_as_country --fifo --file \
	../../examples/Chasin_Coral2017_1080p.torrent --bind_port 1234

../../dht_crawler/exec.py --duration 120 --file \
	../../examples/Chasin_Coral2017_1080p.torrent --bind_port 1234

