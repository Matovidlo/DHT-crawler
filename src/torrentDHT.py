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

BOOTSTRAP_NODES = [
    ("router.bittorrent.com", 6881),
    ("dht.transmissionbt.com", 6881),
    ("router.utorrent.com", 6881)
]


# TODO no IPv6 support
def get_myip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    name = sock.getsockname()[0]
    sock.close()
    return name


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

class TorrentDHT():

    def __init__(self, bind_port=6882, bootstrap_nodes=BOOTSTRAP_NODES,
                 infohash="", verbosity=False, max_node_qsize=200):
        self.query_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,
                                          socket.IPPROTO_UDP)

        self.query_socket.bind((get_myip(), bind_port))
        # Set verboisty
        self.verbosity = verbosity
        # Set log object
        self.bootstrap = True

        # create all necessary for transmission over network
        self.infohash = sha1(infohash.encode('utf-8'))
        if not infohash:
            self.infohash = random_infohash()

        # list of nodes
        self.max_node_qsize = max_node_qsize
        self.info = queue.Queue(self.max_node_qsize)
        # Append all bootstrap nodes
        for node in bootstrap_nodes:
            self.info.put((self.infohash, node[0], node[1]))
        self.rejoin = timer(3, self.rejoin_dht)
        self.rejoin.start()


    def clear_bootstrap(self):
        global BOOTSTRAP_NODES
        BOOTSTRAP_NODES = []

    def print_bootstrap(self):
        return BOOTSTRAP_NODES

    def change_bootstrap(self, infohash, node):
        self.info = queue.Queue(self.max_node_qsize)
        try:
            self.info.put((infohash, node[0][0].decode("utf-8"), node[0][1]))
        except AttributeError:
            self.info.put((infohash, node[0], node[1]))
        # Change bootstrap
        global BOOTSTRAP_NODES
        try:
            BOOTSTRAP_NODES.append((node[0][0].decode("utf-8"), node[0][1]))
        except AttributeError:
            BOOTSTRAP_NODES.append((node[0], node[1]))

    '''
    This is bootstrap mechanism, to get new nodes from well known ones.
    Joins DHT network from exact address
    '''

    def join_dht(self):
        if self.verbosity:
            print("Sending to bootstrap")
        for address in BOOTSTRAP_NODES:
            node = (random_infohash(), address[0], address[1])
            self.query_find_node(node)

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
        except IndexError:
            pass

    '''
    Query messages.
    '''

    def query_find_node(self, node, target=None, infohash=None):
        infohash = get_neighbor(infohash, self.infohash) if infohash \
            else self.infohash
        # By default transaction ID should be at least 2 bytes long
        if target is None:
            target = node[0]
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

    def query_get_peers(self, node, infohash, peer_id=None):
        peer_id = get_neighbor(peer_id, self.infohash) if peer_id \
            else self.infohash
        message = {
            "t": "gp",
            "y": "q",
            "q": "get_peers",
            "a": {
                "id": peer_id,
                "info_hash": infohash
            }
        }
        self.send_krpc(message, node)

    def query_announce_peer(self, node, infohash, token="", implied_port=1,
                            peer_id=None):
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
                "implied_port": implied_port,
                "info_hash": infohash,
                "port": port,
                "token": token
            }
        }
        self.send_krpc(message, node)

    '''
    Response message decode
    '''

    def response_get_peers(self, message, address):
        try:
            infohash = message["a"]["info_hash"]
            tid = message["t"]
            token = infohash[:2]
            msg = {
                "t": tid,
                "y": "r",
                "r": {
                    "id": get_neighbor(infohash, self.infohash),
                    "nodes": "",
                    "token": token
                }
            }
            self.send_krpc(msg, address)
        except KeyError:
            pass

    # Decode all types of messages, recieved and querry
    def decode_message(self, msg, info_pool):
        nodes = []
        for key, value in msg.items():
            # TODO responses and queries
            # print(key.decode('utf-8'))
            if str(key)[2] == "r":
                for lkey, lvalue in value.items():
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


'''
Class can possibly print nodes with this log class in format given
below in method log.
'''
''' class LogDHT(object):
    def log(self, infohash, address=None):
        print ("{} from {}:{}").format(infohash, address[0], address[1])
'''
