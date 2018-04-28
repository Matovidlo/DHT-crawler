# DHT-crawler

This project was created as part of bacherol thesis. DHT-crawler is supposed to monitor
BitTorrent traffic with use of DHT tables. Tool has variety of usage and plenty
of space to expand.

## Build:
[![Build Status](https://travis-ci.com/Matovidlo/DHT-crawler.svg?token=fq9GsJS6Do3MQ8iWuHo3&branch=master)](https://travis-ci.com/Matovidlo/DHT-crawler)

### Getting Started
To run this program you are supposed to install prerequisites. When you do not want to
use it on your machine, there is a docker image to make container which is created for
safety. Setup.py installs script with sudo privileges to /usr/env/python. From there
you have to execute it from this repository with sudo privileges. There is only 1
file which is executable found at ./dht_crawler/exec.py.

### Prerequisites

To run this application you need python 3 and more. Bencoder and bencoder.pyx package.
```
pip3 install -r requirements.txt
or
pip3 install bencoder bencoder.pyx
```

### Outputs

Program has 3 types of output.
1. db_format, which can be send over client to server.
2. print_as_country format, which have translate IP-addresses to geolocation.
3. without formatting, which has every 5 seconds tells you about current status of crawling.

### Tests

There are unit tests which are supposed to rely on application, that is still runnable.
Integration tests, which are supposed to give results which are transformable with
help of results/get_results.sh script. Automatically transform those results with help
of pgfplots and tex to nice looking graphs of result output.

### Contribution

There is possiblity to contribute, when something is not working or something should be 
done better even refactor some part of library. Project is not well modularized so
there is probably good call to get better structure of this property.