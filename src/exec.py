#!/usr/bin/env python3

'''
Execution script
'''
from monitor import create_monitor

if __name__ == '__main__':
    CRAWL = create_monitor(False)
    if CRAWL.torrent.target_pool:
        for torrent in CRAWL.torrent.target_pool:
            CRAWL.crawl_begin(torrent)
    else:
        CRAWL.crawl_begin()