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
import time
import os,sys
import datetime
from torrentDHT import *
'''
This part is about parsing input arguments. Using argparse for standardized use
'''

# first parse paramters of program


def argParse():
	parser = arg.ArgumentParser()

	parser.add_argument('--hash', dest='hash', action='store', help='Specifies info_hash of torrent file which can be get from magnet-link.')
	parser.add_argument('--regex', dest='regex', action='store',
					  help='Filters output by this regular expression.')
	parser.add_argument('--file', nargs='+', dest='file', action='store',
					 help='Gets torrent file, which decompose and start monitoring from DHT nodes in this file or from tracker (swarm).')
	parser.add_argument('--duration', type=int, dest='duration', action='store',
					 help='Set for how long should program monitor continuously')
	## settings for dht
	parser.add_argument('--counter', type=int, dest='counter', action='store',
					  help='Counter specifies how long to wait after a queue with nodes is empty')
	parser.add_argument('--max-peers', type=int, dest='max_peers', action='store',
					  help='Specifies maximum number of peers in queue. This is set by default on value of 200.')
	parser.add_argument('--block-timeout', type=int ,action='store',
					  help='Timeout for how long should be our connection blocked.')
	parser.add_argument('--test', action='store_true', help='Tests connection to remote(local) server.')
	# TODO add --additional for additional information: connect with TCP socket on node to extract more information
	return parser

# Parse it from class methods to monitor class where we want to exchange this information. Start monitoring and initialize all necessary things at first

class Monitor:
	def __init__(self, arguments, torrent):
		self.regex = None
		self.file = None
		self.random = False
		self.counter = 10
		self.torrent = torrent
		self.infohash = self.torrent.random_infohash()
		self.test = False
		self.duration = 600
		# Set when arguments are given
		if arguments.hash is not None:
			self.infohash = sha1(arguments.hash.encode('utf-8')) # infohash of some file on internet, if not specified randomly generate infohash
		if arguments.regex is not None:
			self.regex = arguments.regex 						 # regular expression which should parse output/input
		if arguments.file is not None:
			self.file = arguments.file 							 # file which should be parsed !!
		if arguments.counter is not None:
			self.counter = arguments.counter 					 # How long should wait after queue is empty
		if arguments.test is not None:
			self.test = arguments.test 							 # Test of connection !
		if arguments.duration is not None:
			self.duration = arguments.duration 					 # Duration of crawl
		# local variables for class
		self.tn = 0				# Number of nodes in a specified n-bit zone
		self.tnspeed = 0
		self.infoPool = {} 		# infohashes already found
		self.addrPool = {} 		# Addr recieved from
		self.respondent = 0		# Number of respondents


	def __str__(self):
		return "Hash: {},\nRegex: {},\nFile: {},\nDuration of crawl: {},\nCounter: {}".format(self.infohash, self.regex, self.file, self.duration, self.counter)


	def hasNode(self, id, host, port):
		r = None
		for n in self.infoPool[id]:
			if n[0] == host and n[1] == port:
			    r = n
			    break
		return r

	def decode_message(self, msg):
		nodes = []
		for key,value in msg.items():
			if str(key)[2] == "r":
				# print(key)
				for lkey, lvalue in value.items():
					nodes = self.decode_nodes(lvalue)
		return nodes

	def decode_nodes(self, nodes):
		n = []
		try:
			length = len(nodes)
		except:
			# TODO fix this
			length = 0
			# print(nodes)
			pass
		if (length % 26) != 0:
			return n
		#nodes in raw state
		for i in range(0, length, 26):
			nid = nodes[i:i+20]
			ip = socket.inet_ntoa(nodes[i+20:i+24])
			port = unpack("!H", nodes[i+24:i+26])[0]
			n.append((nid, ip ,port))

			nid = binascii.hexlify(nid).decode("utf-8")
			if nid not in self.infoPool:
				self.infoPool[nid] = [(ip,port)]
			else:
				if not self.hasNode(nid, ip, port):
					self.infoPool[nid].append((ip,port))
				else:
					# duplicates
					pass
		return n

		#####################
		# START OF CRAWLING #
		#####################

	def start_listener(self):
		while True:
			# try:
			msg, addr = self.torrent.query_socket.recvfrom(1024)
			try:
				msg = self.torrent.decode_krpc(msg)
			except:
				# TODO probably malformed message
				continue
			nodes = self.decode_message(msg)
			for node in nodes:
				if self.torrent.info.empty():
					self.torrent.info.put((node))
				elif node[0] != self.torrent.info.get(True):
					self.torrent.info.put((node))

			self.addrPool[addr] = {"timestamp":time.time()}
			self.respondent += 1
			# TODO respondent info
			# print("Current pool:")
			print(self.addrPool)
			# print()
			# except Exception:
				# print ("Exception in creating listener")
				# msgTID, msgType, msgContent = self.torrent.krpc_decode(msg)

	def start_sender(self, test=False):
		if not test:
			while True:
				# try:
				node = self.torrent.info.get(True)
				hexDig1 = int.from_bytes(self.infohash, byteorder='big')
				hexDig2 = int.from_bytes(node[0], byteorder='big')
				# if((hexDig1 ^ hexDig2)>>148) == 0:
					# print(node)
					# TODO
					# self.torrent.find_node(node)
					# for i in range(1,5):
					# 	tid = self.torrent.get_neighbor(self.infohash, self.target)
					# 	self.find_node(tid, node)
				# elif self.tn < 2000:
				# FIXME debug
				# print("Node:")
				# print(node)
				# print()
				self.torrent.find_node(node)
				# TODO
				# print("End Send thread")
				# except Exception:
				# 	print ("Exception in creating sender")
		# FIXME testing connection
		node = self.torrent.info.get(True)
		hexDig1 = int.from_bytes(self.infohash, byteorder='big')
		hexDig2 = int.from_bytes(node[0], byteorder='big')
		self.torrent.find_node(node)
		self.torrent.rejoin.cancel()

	def start_timer(self):
		time.sleep(self.duration)
		# TODO raise or kill all threads??
		print("END")
		self.torrent.rejoin.cancel()
		raise TimerExhausted('Duration of crawl was exceeded')

	def crawl_begin(self):
		send_thread = Thread(target=self.start_sender, args=())
		send_thread.daemon = True
		send_thread.start()
		listen_thread = Thread(target=self.start_listener, args=())
		listen_thread.daemon = True
		listen_thread.start()
		duration_thread = Thread(target=self.start_timer, args=())
		duration_thread.daemon = True
		duration_thread.start()

		while self.counter:
			try:
				self.counter = 10 if self.torrent.info.qsize() else self.counter - 1
				# self.info()
				time.sleep(1)
			except KeyboardInterrupt:
				break
			except Exception as err:
				print("Expcetion: Crawler start threads()", err.args)
		pass


	def info(self):
		# [Dup]:%.2f%% ,  self.duplicates*100.0/self.total
		print ("[NodeSet]:%i\t\t[12-bit Zone]:%i [%i/s]\t\t[Response]:%.2f%%\t\t[Queue]:%i\t\t" % \
			  (len(self.nodePool), self.tn, self.tnspeed,
			   self.respondent*100.0/max(1,len(self.nodePool)),
			   self.torrent.info.qsize()))
		pass

	def parse_torrent_info(self, pieces, values):
		pieces = pieces.decode("utf-8")
		if pieces == "name":
			print("File name: {}".format(values.decode("utf-8")))
		if pieces == "pieces":
			return values

	def parse_torrent(self):
		for file in self.file:
			file_r = open(file, "rb")
			content = file_r.read()
			info_hash = None
			print("Torrent file content")
			for key,value in self.torrent.decode_krpc(content).items():
				key = key.decode('utf-8')
				if key == "creation date":
					print("Creation of file: ")
					print(datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S"))
				if key == "info":
					for info_key, info_value in value.items():
						info_hash = self.parse_torrent_info(info_key, info_value)
						pass
				if key == "nodes":
					self.torrent.change_bootstrap(info_hash, value)
					pass
			file_r.close()
			pass
		else:
			pass

#################
# Start of main #
#################
if __name__ == "__main__":
	# execute only if run as a script
	args = argParse()
	args = args.parse_args()
	dht_socket = torrentDHT(LogDHT(), verbosity = True)


	monitor = Monitor(args, dht_socket)
	if monitor.test:
		monitor.start_sender(test=True)
		exit(2)
	else:
		monitor.parse_torrent()
		monitor.crawl_begin()
	# print(monitor)





# create log files for storing important information (based on filename as paramter)

# parameters - ....

