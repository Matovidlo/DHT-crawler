#!/usr/bin/env python3

'''
Created by Martin Vasko
3BIT, Brno, Faculty of Information Technology.

Brief information:
This is implementation of monitoring BiTtorrent with Kademlia DHT.
Whole monitor class which will be presented next is going to be supported by torrentDHT implementation, which was implemented by Martin Vasko.
'''
import argparse as arg
import inspect
import signal
import time
import os,sys
import datetime
import json
from torrentDHT import *
from processOutput import *

'''
This part is about parsing input arguments. Using argparse for standardized use
'''
# first parse paramters of program


def argParse():
	parser = arg.ArgumentParser()

	parser.add_argument('--hash', type=str, dest='hash', action='store', help='Specifies info_hash of torrent file which can be get from magnet-link.')
	parser.add_argument('--regex', type=str, dest='regex', action='store',
					  help='Filters output by this regular expression.')
	parser.add_argument('--file', nargs='+', dest='file', action='store', help='Gets torrent file, which decompose and start monitoring from DHT nodes in this file or from tracker (swarm).')
	parser.add_argument('--magnet', nargs='+', dest='magnet', action='store', help='Given magnet-link or file with magnet-link would be parsed and its output filled to proper class variables and starts crawling from magnet-link (Some DHT node).')
	parser.add_argument('--output', type=str, dest="output", action='store', help='Specifies output file name, if not given output is written to standard output (terminal).')
	parser.add_argument('--duration', type=int, dest='duration', action='store', help='Set for how long should program monitor continuously')
	parser.add_argument('--result', type=str, dest="result_file", action='store', help='opens result file as json and dumps it\'s content.')
	## settings for dht

	parser.add_argument('--counter', type=int, dest='counter', action='store', help='Counter specifies how long to wait after a queue with nodes is empty')
	parser.add_argument('--max-peers', type=int, dest='max_peers', action='store', help='Specifies maximum number of peers in queue. This is set by default on value of 200.')
	parser.add_argument('--block-timeout', type=int ,action='store', help='Timeout for how long should be our connection blocked.')
	parser.add_argument('--test', action='store_true', help='Tests connection to remote(local) server.')
	# TODO add --additional for additional information: connect with TCP socket on node to extract more information
	return parser

# Parse it from class methods to monitor class where we want to exchange this information. Start monitoring and initialize all necessary things at first

class Monitor:
	def __init__(self, arguments, torrent):
		self.counter = 1
		self.torrent = torrent
		self.infohash = self.torrent.random_infohash()
		self.test = False
		self.duration = 600
		# Set when arguments are given
		self.regex = arguments.regex 						 # regular expression which should parse output/input
		self.file = arguments.file 							 # file which should be parsed !!
		self.magnet = arguments.magnet 						 # magnet-link given
		self.output = arguments.output
		self.result = arguments.result_file

		if arguments.hash is not None:
			self.infohash = sha1(arguments.hash.encode('utf-8')) # infohash of some file on internet, if not specified randomly generate infohash
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

	# Debug info of class variables , print(Monitor_obj)
	def __str__(self):
		return "Hash: {},\nRegex: {},\nFile: {},\nMagnet-link: {},\nDuration of crawl: {},\nCounter: {}".format(self.infohash, self.regex, self.file, self.magnet, self.duration, self.counter)

	def vprint(self, msg):
		if self.torrent.verbosity:
			print(msg)

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
			# print(key.decode('utf-8'))
			# print(value)
			if str(key)[2] == "r":
				for lkey, lvalue in value.items():
					nodes = self.decode_nodes(lvalue)

		return nodes

	def decode_nodes(self, nodes):
		n = []
		try:
			length = len(nodes)
		except:
			length = 0
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
			if self.counter is not None:
				time.sleep(self.counter)
			try:
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

				self.vprint("Last Thing\n{")
				for key,value in self.infoPool.items():
					for val in value:
						self.vprint("\"{}\": [\n\"{}\",{}\n],".format(key,val[0], val[1]))
				self.vprint("}")
			except Exception:
				print ("Exception in creating listener")

	def start_sender(self, test=False):
		if not test:
			while True:
				if self.counter is not None:
					time.sleep(self.counter)

				try:
					node = self.torrent.info.get(True)
					hexDig1 = int.from_bytes(self.infohash, byteorder='big')
					hexDig2 = int.from_bytes(node[0], byteorder='big')
					# TODO metrics
					if((hexDig1 ^ hexDig2)>>148) == 0:
						self.torrent.query_find_node(node)
						for i in range(1,5):
							tid = self.torrent.get_neighbor(self.infohash, node[0], i)
							self.query_find_node(tid, node)
					elif self.tn < 2000:
						self.torrent.query_find_node(node)
				except Exception:
					print ("Exception in creating sender")

		# if test is given perform single message send
		node = self.torrent.info.get(True)
		hexDig1 = int.from_bytes(self.infohash, byteorder='big')
		hexDig2 = int.from_bytes(node[0], byteorder='big')
		self.torrent.query_find_node(node)
		self.torrent.rejoin.cancel()

	def start_timer(self, thread1, thread2):
		self.vprint("Start of duration")
		# sleep for shorter time
		for i in range(self.duration):
			time.sleep(1)
		self.vprint("End of duration")
		# Clear all resources
		self.torrent.rejoin.cancel()
		identification = thread1.ident
		signal.pthread_kill(identification, 2)
		identification = thread2.ident
		signal.pthread_kill(identification, 2)

	def clear_resources(self):
		self.torrent.rejoin.cancel()

	def crawl_begin(self):
		send_thread = Thread(target=self.start_sender, args=())
		send_thread.daemon = True
		send_thread.start()
		listen_thread = Thread(target=self.start_listener, args=())
		listen_thread.daemon = True
		listen_thread.start()
		duration_thread = Thread(target=self.start_timer, args=(send_thread, listen_thread))
		duration_thread.daemon = True
		duration_thread.start()

		# TODO types of output
		# if country output set it to True
		output = ProcessOutput(self, True)
		while True:
			try:
				# self.counter = 10 if self.torrent.info.qsize() else self.counter - 1
				# self.info()
				output.get_locations()

				time.sleep(1)
			except KeyboardInterrupt:
				self.vprint("\nClearing threads, wait a second")
				self.clear_resources()
				break
			except Exception as err:
				print("Expcetion: Crawler start threads()", err.args)
		output.print_locations()


	def fill_locations(self):
		'''
		fill various information to dictionary
		'''
		pass

	def info(self):
		# [Dup]:%.2f%% ,  self.duplicates*100.0/self.total
		print ("[NodeSet]:%i\t\t[12-bit Zone]:%i [%i/s]\t\t[Response]:%.2f%%\t\t[Queue]:%i\t\t" % \
			  (len(self.nodePool), self.tn, self.tnspeed,
			   self.respondent*100.0/max(1,len(self.nodePool)),
			   self.torrent.info.qsize()))
		pass

	def parse_ips(self):
		iplist = []
		for key, value in self.monitor.infoPool.items():
			for val in value:
				# print(val[0])
				iplist.append((val[0]))
		self.ipPool["ip"] = iplist

	def parse_torrent_info(self, pieces, values):
		pieces = pieces.decode("utf-8")
		if pieces == "name":
			self.vprint("File name: {}".format(values.decode("utf-8")))
		if pieces == "pieces":
			return values

	def parse_torrent(self):
		if self.file is not None:
			self.torrent.clear_bootstrap()
			for file in self.file:
				file_r = open(file, "rb")
				content = file_r.read()
				info_hash = None
				self.vprint("Torrent file content")
				for key,value in self.torrent.decode_krpc(content).items():
					key = key.decode('utf-8')
					if key == "creation date":
						self.vprint("Creation of file: ")
						self.vprint(datetime.datetime.fromtimestamp(value).strftime("%Y-%m-%d %H:%M:%S"))
					if key == "info":
						for info_key, info_value in value.items():
							info_hash = self.parse_torrent_info(info_key, info_value)
							pass
					if key == "nodes":
						self.torrent.change_bootstrap(info_hash, value)
						pass
					# TODO url-list parse to join to swarm with torrent file
				file_r.close()
		else:
			# If no file given in self.file passing this function and continue without torrent file
			pass

	def parse_magnet(self):
		'''
		# FIXME
		parse magnet link
		'''
		pass


#################
# Start of main #
#################

# FIXME this should be used as process Output

def create_monitor(verbosity = False):
	args = argParse()
	args = args.parse_args()
	# This is variant with verbose output to track some lib imported staff
	dht_socket = torrentDHT(verbosity = verbosity)
	# dht_socket = torrentDHT(LogDHT())

	# Monitor class needs dht_socket, which is imported from torrentDHT.py
	monitor = Monitor(args, dht_socket)
	# This variant is only to test connection to BOOTSTRAP_NODES
	if monitor.test:
		monitor.start_sender(test=True)
		exit(2)
	elif monitor.result is not None:
		result = json.load(open(monitor.result))
		print(json.dumps(result,indent = 4))
		monitor.torrent.rejoin.cancel()
		exit(3)
	return monitor




