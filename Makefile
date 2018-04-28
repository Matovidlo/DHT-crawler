all:
	#@cd ./logs/ && ./logs/clean.sh
	zip xvasko12.zip dht_crawler/* logs/* doc/* Dockerfile setup.sh setup.py requirements.txt README.md monitor.1\
		results/* tests/* examples/*

clean:
	rm xvasko12.zip
