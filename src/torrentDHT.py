#!/usr/bin/env python3
import queue
import socket
import binascii
from random import randint
from hashlib import sha1
from threading import Timer
from struct import unpack
from bencoder import bencode, bdecode

'''
Create by Martin Vasko
3BIT, Brno, Faculty of Information Technology.
'''


'''
This should be used as part of library, where you can create,
bind socket and send all torrent DHT messages over UDP.
BOOTSTRAP_NODES are well known nodes from which should crawl begin.
'''
# TODO no IPv6 support

# set timer function for threading
def timer(time, function):
    return Timer(time, function)


def entropy(length):
    return "".join(chr(randint(0, 255)) for _ in range(length))


def random_infohash():
    i_hash = sha1(entropy(20).encode('utf-8'))
    # infohash should be 20 bytes long
    return i_hash.digest()


def get_neighbor(target, infohash, end=10):
    # mix target and own infohash to get "neighbor"
    return target[:end] + infohash[end:]

def has_node(id_node, host, port, info_pool):
    list_node = None
    for nodes in info_pool[id_node]:
        if nodes[0] == host and nodes[1] == port:
            list_node = nodes
            break
    return list_node


def decode_krpc(message):
    try:
        return bdecode(message)
    except Exception:
        return None


class TorrentArguments:
    def __init__(self, bootstrap_nodes=None, max_node_qsize=200):
        if bootstrap_nodes is None:
            self.bootstrap_nodes = [
                ("router.bittorrent.com", 6881),
                ("dht.transmissionbt.com", 6881),
                ("router.utorrent.com", 6881)
            ]
        else:
            self.bootstrap_nodes = bootstrap_nodes
        self.max_node_qsize = max_node_qsize

    def clear_bootstrap(self):
        self.bootstrap_nodes = []

    def print_bootstrap(self):
        return self.bootstrap_nodes


def get_myip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    name = sock.getsockname()[0]
    sock.close()
    return name


class TorrentDHT():

    def __init__(self, arguments, bind_port=6882, infohash="",
                 verbosity=False):
        self.query_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                          socket.IPPROTO_UDP)

        self.query_socket.bind((get_myip(), bind_port))
        # Set verboisty
        self.verbosity = verbosity

        # create all necessary for transmission over network
        self.infohash = sha1(infohash.encode('utf-8'))
        if not infohash:
            self.infohash = random_infohash()

        # list of nodes
        self.bootstrap_nodes = arguments.bootstrap_nodes
        self.max_node_qsize = arguments.max_node_qsize
        self.info = queue.Queue(self.max_node_qsize)
        # Append all bootstrap nodes
        for node in arguments.bootstrap_nodes:
            self.info.put((self.infohash, node[0], node[1]))
        # self.rejoin = timer(3, self.rejoin_dht)
        # self.rejoin.start()

    def change_hash(self, input_hash):
        self.infohash = input_hash

    def change_bootstrap(self, infohash, node):
        self.info = queue.Queue(self.max_node_qsize)
        try:
            self.info.put((infohash, node[0][0].decode("utf-8"), node[0][1]))
        except AttributeError:
            self.info.put((infohash, node[0], node[1]))
        # Change bootstrap
        try:
            self.bootstrap_nodes.append((node[0][0].decode("utf-8"), node[0][1]))
        except AttributeError:
            self.bootstrap_nodes.append((node[0], node[1]))

    '''
    This is bootstrap mechanism, to get new nodes from well known ones.
    Joins DHT network from exact address
    '''

    def join_dht(self):
        if self.verbosity:
            print("Sending to bootstrap")
        for address in self.bootstrap_nodes:
            node = (random_infohash(), address[0], address[1])
            self.query_find_node(node, infohash=self.infohash)

    def rejoin_dht(self):
        # if self.info.qsize() == 0:
        self.join_dht()
        self.rejoin = timer(3, self.rejoin_dht)
        self.rejoin.start()
    '''
    This part is about query messages. Supports all 4 Kademlia messages sends
    over UDP with bencoding as torrent BEP05 refers.
    '''

    def send_krpc(self, message, node):
        # Get IP address and port touple
        try:
            self.query_socket.sendto(bencode(message), (node[1], node[2]))
        except (IndexError, TypeError):
            pass

    '''
    Query messages.
    '''

    def query_find_node(self, node, infohash=None):
        # target = get_neighbor(target, self.infohash) if target \
            # else self.infohash
        # By default transaction ID should be at least 2 bytes long
        # if infohash is None:
        #     infohash = node[0]
        message = {
            "t": "fn",
            "y": "q",
            "q": "find_node",
            "a": {
                "id": infohash,
                "target": node[0]
            }
        }
        self.send_krpc(message, node)

    def query_ping(self, node, infohash=None):
        infohash = get_neighbor(infohash, self.infohash) if infohash \
            else self.infohash
        # By default transaction ID should be at least 2 bytes long
        message = {
            "t": "pg",
            "y": "q",
            "q": "ping",
            "a": {
                "id": infohash
            }
        }
        self.send_krpc(message, node)

    def query_get_peers(self, node, infohash):
        message = {
            "t": "gp",
            "y": "q",
            "q": "get_peers",
            "a": {
                "id": node[0],
                "info_hash": infohash
            }
        }
        self.send_krpc(message, node)

    def query_announce_peer(self, node, infohash, token="", peer_id=None):
        # get port from node
        port = node[2]
        peer_id = get_neighbor(peer_id, self.infohash) if peer_id \
            else self.infohash
        message = {
            "t": "ap",
            "y": "q",
            "q": "announce_peer",
            "a": {
                "id": peer_id,
                "implied_port": 1, # could be 0 or 1
                "info_hash": infohash,
                "port": port,
                "token": token
            }
        }
        self.send_krpc(message, node)

    # Response message decode
    # Decode all types of messages, recieved and querry
    def decode_message(self, msg, info_pool):
        nodes = []
        for key, value in msg.items():
            # TODO responses and queries
            # print(key.decode('utf-8'))
            if str(key)[2] == "r":
                for lvalue in value.values():
                    nodes = self.decode_nodes(lvalue, info_pool)

        return nodes

    def decode_nodes(self, value, info_pool):
        nodes = []
        try:
            length = len(value)
        except TypeError:
            length = 0

        if (length % 26) != 0:
            return nodes
        # nodes in raw state
        for i in range(0, length, 26):
            nid = value[i:i+20]
            ip_addr = socket.inet_ntoa(value[i+20:i+24])
            port = unpack("!H", value[i+24:i+26])[0]
            nodes.append((nid, ip_addr, port))

            nid = binascii.hexlify(nid).decode("utf-8")
            if nid not in info_pool:
                info_pool[nid] = [(ip_addr, port)]
            else:
                if not has_node(nid, ip_addr, port, info_pool):
                    info_pool[nid].append((ip_addr, port))
                else:
                    # duplicates
                    pass
        return nodes
