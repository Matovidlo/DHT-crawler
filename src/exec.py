#!/usr/bin/env python3

'''
Execution script
'''
import monitor

if __name__ == '__main__':
	# TODO when true debug info is written to stdout
	monitor_obj = monitor.create_monitor(False)
	monitor_obj.parse_torrent()
	monitor_obj.crawl_begin()

	# monitor.monitor_main()
