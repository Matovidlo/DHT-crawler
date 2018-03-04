#!/usr/bin/env python3

import queue
import socket
import binascii
from random import randint
from hashlib import sha1
from threading import Timer, Thread
from struct import unpack

# from threading import Timer, Thread
from bencoder import bencode, bdecode
'''
This should be used as part of library, where you can create socket and send
all torrent DHT messages over UDP.
'''

BOOTSTRAP_NODES = [("router.bittorrent.com", 6881), ("dht.transmissionbt.com", 6881),("router.utorrent.com", 6881)]


# TODO no IPv6 support
# class to store node as object with necessary information
def get_myip():
	s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
	s.connect(("8.8.8.8", 80))
	name = s.getsockname()[0]
	s.close()
	return name

# set timer function for threading
def timer(t, f):
	return Timer(t, f)

# Main class
class torrentDHT():

	def __init__(self, log, bind_port = 6882, bootstrap_nodes = BOOTSTRAP_NODES, infohash = "", target = "", verbosity = False, max_node_qsize = 200):
		# Thread.__init__(self)
		# self.setDaemon(True)
		self.bind_ip = get_myip()
		self.bind_port = bind_port
		self.query_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
		self.query_socket.bind((self.bind_ip, self.bind_port))
		# Set verboisty
		self.verbosity = verbosity
		self.TID_LENGTH = 2
		# Set log object
		self.log_output = log

		# create all necessary for transmission over network
		self.infohash = sha1(infohash.encode('utf-8'))
		if not infohash:
			self.infohash = self.random_infohash()

		# list of nodes
		self.max_node_qsize = max_node_qsize
		self.info = queue.Queue(self.max_node_qsize)
		# Append all bootstrap nodes
		for node in bootstrap_nodes:
			self.info.put((self.infohash, node[0], node[1]))
		self.rejoin = timer(3, self.rejoin_DHT)
		self.rejoin.start()

	def __str__(self):
		return "IP {}, Port {}".format(self.bind_ip, self.bind_port)


	def entropy(self, length):
		return "".join(chr(randint(0, 255)) for _ in range(length))

	def change_TID_length(value):
		if isinstance(value, int):
			self.TID_LENGTH = value

	def random_infohash(self):
		i_hash = sha1(self.entropy(20).encode('utf-8'))
		# infohash should be 20 bytes long
		# line = self.entropy(20)
		# i_hash.update(line.encode('utf-8'))
		return i_hash.digest()

	def get_neighbor(self, target, infohash, end = 10):
		# mix target and own infohash to get "neighbor"
		return target[:end] + infohash[end:]

	def change_bootstrap(self, infohash, node):
		self.info = queue.Queue(self.max_node_qsize)
		self.info.put((infohash, node[0][0].decode("utf-8"), node[0][1]))

	'''
	This part is about query messages. Supports all 4 Kademlia messages sends over UDP with bencoding as torrent BEP05 refers.
	'''
	# Joins DHT network from exact address
	def join_DHT(self):
		for address in BOOTSTRAP_NODES:
			node = (self.random_infohash(), address[0], address[1])
			self.find_node(node)

	def rejoin_DHT(self):
		if self.info.qsize() == 0:
			self.join_DHT()
		self.rejoin = timer(3, self.rejoin_DHT)
		self.rejoin.start()

	def send_krpc(self, message, node):
		try:
			# Get IP address and port touple
			try:
				self.query_socket.sendto(bencode(message), (node[1],node[2]))
			except IndexError:
				pass
		except Exception as err:
			if self.verbosity:
				print("KRPC send error: {}".format(err.message))
			pass


	def decode_krpc(self, message):
		return bdecode(message)

	'''
	Query messages.
	'''

	def find_node(self, node, target = None, infohash = None):
		infohash = self.get_neighbor(infohash, self.infohash) if infohash else self.infohash
		# By default transaction ID should be at least 2 bytes long
		# transaction_id = self.entropy(self.TID_LENGTH)
		if target is None:
			target = node[0]
			# TODO set target
		message = {
			"t": "fn",
			"y": "q",
			"q": "find_node",
			"a": {
				"id": infohash,
				"target": target
			}
		}
		self.send_krpc(message, node)


	def ping(self, infohash = None):
		infohash = self.get_neighbor(infohash, self.infohash) if infohash else self.infohash
		# By default transaction ID should be at least 2 bytes long
		transaction_id = self.entropy(TID_LENGTH)
		message = {
			"t": transaction_id,
			"y": "q",
			"q": "ping",
			"a": {
				"id": infohash
			}
		}
		self.send_krpc(message)

	'''
	TODO Response messages.
	'''

	# TODO
	# decode_message, decode_nodes hasNodes as interface



# LogClass
class LogDHT(object):
	def log(self, infohash, address=None):
		print ("{} from {}:{}").format(infohash, address[0], address[1])


# FIXME
# if __name__ == "__main__":
	# dht_socket = BindSocket(get_myip(), 6882)
	# print(dht_socket)
	# dht = torrentDHT(Log(), dht_socket)
	# Start thread
	# dht.start()