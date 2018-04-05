#!/usr/bin/env python3
import queue
import socket
import binascii
import re
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
BOOTSTRAP_NODES are well known nodes from which should begin torrent
peer detection.
'''
# TODO no IPv6 support

# set timer function for threading
def timer(time, function):
    '''
    create timer
    '''
    return Timer(time, function)


def entropy(length):
    '''
    entropy to generate infohash
    '''
    return "".join(chr(randint(0, 255)) for _ in range(length))


def random_infohash():
    '''
    generates random 20 bytes infohash
    '''
    i_hash = sha1(entropy(20).encode('utf-8'))
    # infohash should be 20 bytes long
    return i_hash.hexdigest()


def get_neighbor(target, infohash, end=10):
    '''
    mixture of infohashes
    '''
    return target[:end] + infohash[end:]

def has_node(id_node, host, port, info_pool):
    '''
    when node is in infopool clear duplicities.
    '''
    list_node = None
    for nodes in info_pool[id_node]:
        if nodes[0] == host and nodes[1] == port:
            list_node = nodes
            break
    return list_node


def decode_krpc(message):
    '''
    decode with bencoding. When exception is thrown, return None.
    '''
    try:
        return bdecode(message)
    except Exception:
        return None


def decode_nodes(value, info_pool):
    '''
    decode nodes from response message
    '''
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

        nid = binascii.hexlify(nid).decode("utf-8")
        nodes.append((nid, ip_addr, port))
        if nid not in info_pool:
            info_pool[nid] = [(ip_addr, port)]
        else:
            if not has_node(nid, ip_addr, port, info_pool):
                info_pool[nid].append((ip_addr, port))
            else:
                # duplicates
                pass
    return nodes


def decode_peers(value, info_pool):
    '''
    decode peers from response message
    '''
    pass


class TorrentArguments:
    '''
    bootstrap arguments for DHT class
    '''
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
        '''
        clear
        '''
        self.bootstrap_nodes = []

    def print_bootstrap(self):
        '''
        print
        '''
        return self.bootstrap_nodes


def get_myip():
    '''
    get my global ip_address, by connecting to google and get sockname
    '''
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.connect(("8.8.8.8", 80))
    name = sock.getsockname()[0]
    sock.close()
    return name


class TorrentDHT():
    '''
    Class which perform query and response of dht messages.
    '''

    def __init__(self, arguments, bind_port=6882, verbosity=False):
        self.query_socket = socket.socket(socket.AF_INET,
                                          socket.SOCK_DGRAM,
                                          socket.IPPROTO_UDP)
        self.query_socket.bind((get_myip(), bind_port))
        # Set verboisty
        self.verbosity = verbosity

        # create all necessary for transmission over network
        self.infohash = random_infohash()
        self.target = None
        # list of nodes
        self.bootstrap_nodes = arguments.bootstrap_nodes
        self.max_node_qsize = arguments.max_node_qsize
        self.nodes = queue.Queue(self.max_node_qsize)
        self.peers = queue.Queue(self.max_node_qsize)
        # Append all bootstrap nodes
        for node in arguments.bootstrap_nodes:
            self.nodes.put((self.infohash, node[0], node[1]))
        # self.rejoin = timer(3, self.rejoin_dht)
        # self.rejoin.start()

    def change_bootstrap(self, infohash, nodes):
        '''
        change bootstrap nodes when parsed magnet-link or .torrent file
        '''
        self.nodes = queue.Queue(self.max_node_qsize)
        # self.bootstrap_nodes = []
        for node_list in nodes:
            for node in node_list:
                compact_node = node.decode("utf-8")
                port = re.search(r":\d+", compact_node)
                port = port.group(0)[1::]

                compact_node = re.search(r".*:", compact_node)
                compact_node = compact_node.group(0)[6:-1]
                # self.nodes.put((infohash, compact_node, port))
                # self.bootstrap_nodes.append((compact_node, port))
        for bootstrap in self.bootstrap_nodes:
            self.nodes.put((infohash, bootstrap[0], bootstrap[1]))

    def change_info(self, infohash):
        '''
        change infohash in nodes queue
        '''
        self.nodes = queue.Queue(self.max_node_qsize)
        for bootstrap in self.bootstrap_nodes:
            self.nodes.put((infohash, bootstrap[0], bootstrap[1]))

    '''
    This is bootstrap mechanism, to get new nodes from well known ones.
    Joins DHT network from exact address
    '''

    # def join_dht(self):
    #     if self.verbosity:
    #         print("Sending to bootstrap")
    #     for address in self.bootstrap_nodes:
    #         node = (random_infohash(), address[0], address[1])
    #         self.query_get_peers(node, self.nodeshash, self.target)

    # def rejoin_dht(self):
    #     # print(self.nodes.qsize())
    #     # if self.nodes.qsize() == 0:
    #     self.join_dht()
    #     self.rejoin = timer(3, self.rejoin_dht)
    #     self.rejoin.start()
    '''
    This part is about query messages. Supports all 4 Kademlia messages sends
    over UDP with bencoding as torrent BEP05 refers.
    '''

    def send_krpc(self, message, node):
        '''
        sends bencoded krpc to node ip address and node port
        '''
        try:
            self.query_socket.sendto(bencode(message), (node[1], node[2]))
        except (IndexError, TypeError):
            pass

    '''
    Query messages.
    '''

    def query_find_node(self, node, infohash=None):
        '''
        send query find_node to node with our infohash
        '''
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
        '''
        send query ping to node
        '''
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

    def query_get_peers(self, node, infohash, target):
        '''
        send simple get_peers with our infohash to node
        '''
        print(target)
        infohash = get_neighbor(infohash, self.infohash) if infohash \
            else self.infohash
        message = {
            "t": "gp",
            "y": "q",
            "q": "get_peers",
            "a": {
                "id": binascii.unhexlify(infohash),
                "info_hash": binascii.unhexlify(target)
            }
        }
        self.send_krpc(message, node)

    def query_announce_peer(self, node, infohash, token="", peer_id=None):
        '''
        send announce_peer query
        '''
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
        '''
        decodes response message. When nodes decode nodes when peers
        decode peers and return them as result.
        '''
        nodes = []
        for key_type, message_content in msg.items():
            # response is detected
            if str(key_type)[2] == "r":
                for key, value in message_content.items():
                    if key.decode("utf-8") == "nodes":
                        nodes = decode_nodes(value, info_pool)
                        retval = "Nodes"
                    if key.decode("utf-8") == "values":
                        retval = "Peers"
                        nodes = decode_peers(value, info_pool)
                        print(value)
        return {retval: nodes}

