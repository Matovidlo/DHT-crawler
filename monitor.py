#!/usr/bin/env python3

'''
Created by Martin Vasko
3BIT, Brno, Faculty of Information Technology.

Brief information:
This is implementation of monitoring bittorrent with Kademlia DHT.
Code is implemented with use of libtorrent library which is wrapped trough C++.
'''
import argparse as arg
import inspect

from torrentDHT import *
'''
This part is about parsing input arguments. Using argparse for standardized use
'''

# first parse paramters of program
def argParse():
  parser = arg.ArgumentParser()

  parser.add_argument('--hash=', dest='hash', action='store', help='Specifies info_hash of torrent file which can be get from magnet-link.')
  parser.add_argument('--regex=', dest='regex', action='store',
					  help='Filters output by this regular expression.')
  parser.add_argument('--file=', nargs='+', dest='file', action='store',
					 help='Gets torrent file, which decompose and start monitoring from DHT nodes in this file or from tracker (swarm).')
  parser.add_argument('--random', action='store_true',
					  help='Info_hash is randomly generated for monitoring.')

  ## settings for dht
  parser.add_argument('--counter=', type=int, dest='counter', action='store',
					  help='Counter specifies how long to wait after a queue with nodes is empty')
  parser.add_argument('--max-peers', type=int, dest='max_peers', action='store',
					  help='When file has more functions with same name, XML file stores only first of them. When parameter is missing, XML file saves all functions with same name.')
  parser.add_argument('--block-timeout', action='store_true',
					  help='Removes from content of attributes `rettype` and `type` all exceeded whitespaces.')
  return parser

# Parse it from class methods to monitor class where we want to exchange this information. Start monitoring and initialize all necessary things at first
class Monitor:
	def __init__(self, arguments, torrent):
		self.regex = "None"
		self.file = "None"
		self.random = False
		self.counter = 10
		self.torrent = torrent
		self.infohash = self.torrent.random_infohash()
		# Set when arguments are given
		if arguments.hash is not None:
			self.infohash = sha1(arguments.hash.encode('utf-8'))
		if arguments.regex is not None:
			self.regex = arguments.regex
		if arguments.file is not None:
			self.file = arguments.file
		if arguments.random is not None:
			self.random = arguments.random
		if arguments.counter is not None:
			self.counter = arguments.counter
		# local variables for class
		self.tn = 0				# Number of nodes in a specified n-bit zone


	def __str__(self):
		return "Hash: {},\nRegex: {},\nFile: {},\nIsRandom: {},\nCounter: {}".format(self.infohash, self.regex, self.file, self.random, self.counter)

	def start_listener(self):
		while self.counter:
			try:
				msg, addr = self.torrent.query_socket.recvfrom(1024)
				print (self.torrent.decode_krpc(msg))
			except Exception:
				print ("Exception in creating listener")
				# msgTID, msgType, msgContent = self.torrent.krpc_decode(msg)
	def start_sender(self):
		while self.counter:
			# try:
			hexDig1 = int.from_bytes(self.infohash, byteorder='big')
			hexDig2 = int.from_bytes(self.torrent.infohash, byteorder='big')
			if((hexDig1 ^ hexDig2)>>148) == 0:
				self.torrent.find_node(self.infohash)
			elif self.tn < 2000:
				self.torrent.find_node(self.infohash)
			self.counter = self.counter - 1
			# except Exception:
				# print ("Exception in creating sender")

#################
# Start of main #
#################
if __name__ == "__main__":
	# execute only if run as a script
	args = argParse()
	args = args.parse_args()

	# FIXME Inspec
	# print(libtorrent.version)
	# print(inspect.getmembers(libtorrent))
	dht_socket = torrentDHT(LogDHT(), verbosity = True)
	# print(dht_socket)

	monitor = Monitor(args, dht_socket)
	monitor.start_sender()
	monitor.counter = 10
	monitor.start_listener()
	# print(monitor)





# create log files for storing important information (based on filename as paramter)

# parameters - ....

