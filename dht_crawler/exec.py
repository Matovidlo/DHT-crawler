#!/usr/bin/env python3

'''
Execution script
'''
import sys
from monitor import create_monitor

if __name__ == '__main__':
    try:
        CRAWL = create_monitor(False)
    except TypeError:
        print("Input file was not valid!")
        sys.exit(1)

    if CRAWL.torrent.target_pool:
        for torrent in CRAWL.torrent.target_pool:
            CRAWL.crawl_begin(torrent)
    else:
        CRAWL.crawl_begin()
