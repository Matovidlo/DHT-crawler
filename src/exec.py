#!/usr/bin/env python3

'''
Execution script
'''
from monitor import create_monitor

if __name__ == '__main__':
    CRAWL = create_monitor(False)
    CRAWL.crawl_begin()
