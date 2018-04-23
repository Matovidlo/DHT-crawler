#!/usr/bin/env python3
'''
Created by Martin Vasko
3BIT, Brno, Faculty of Information Technology.

Brief information:
This is implementation of monitoring BiTtorrent with Kademlia DHT.
Whole monitor class which will be presented next is going to be supported by
torrentDHT implementation, which was implemented by Martin Vasko.
'''
import argparse as arg
import signal
import time
import datetime
import hashlib
import select
import re
import socket
import json
from random import randrange
from threading import Thread, Semaphore
from bencoder import bencode
try:
    from torrent_dht import TorrentDHT, TorrentArguments,\
                           random_infohash, decode_krpc, get_neighbor
    from process_output import ProcessOutput
except ImportError:
    from src.torrent_dht import TorrentDHT, TorrentArguments,\
                               random_infohash, decode_krpc, get_neighbor
    from src.process_output import ProcessOutput




def argument_parser():
    '''
    This part is about parsing input arguments. Using argparse for
    standardized use
    '''
    parser = arg.ArgumentParser()

    parser.add_argument('--hash', type=str, dest='hash', action='store',
                        help='Specifies info_hash of torrent file which can \
                        be get from magnet-link.')
    parser.add_argument('--bind_port', type=int, dest='bind_port', action='store',
                        help='Specify port to which should be connection \
                        binded.')
    parser.add_argument('--country', type=str, dest='country',
                        action='store', help='Store country name to \
                        converge only in this country and do not \
                        bootstrap away from it.')
    parser.add_argument('--file', nargs='+', dest='file', action='store',
                        help='Gets torrent file, which decompose and start \
                        monitoring from DHT nodes in this file or \
                        from tracker (swarm).')
    parser.add_argument('--magnet', nargs='+', dest='magnet', action='store',
                        help='Given magnet-link or file with magnet-link \
                        would be parsed and its output filled to proper \
                        class variables and starts crawling from magnet-link \
                        (Some DHT node).')
    parser.add_argument('--duration', type=int, dest='duration',
                        action='store', help='Set for how long should program \
                        monitor continuously.')
    parser.add_argument('--print_as_country', action='store_true',
                        help='Store ip addresses with coresponding \
                        dictionary in format country:city -> ip.addr.')
    parser.add_argument('--fifo', action='store_true', dest="queue_type",
                        help='Change shared queue between processes \
                        from default lifo to fifo')
    # settings for dht

    parser.add_argument('--counter', type=int, dest='counter', action='store',
                        help='Counter specifies how long to wait after \
                        a queue with nodes is empty.')
    parser.add_argument('--max-peers', type=int, dest='max_peers',
                        action='store', help='Specifies maximum number of \
                        peers in queue. This is set by default \
                        on value of 200.')
    parser.add_argument('--test', action='store_true',
                        help='Tests connection to remote(local) server.')
    return parser


def parse_input_args():
    '''
    Parse arguments from argParse class
    '''
    args = argument_parser()
    args = args.parse_args()
    return args


class Monitor:
    '''
     Parse it from class methods to monitor class where we want to exchange
     this information.
     Start monitoring and initialize all necessary things at first
    '''

    def __init__(self, arguments, torrent):
        self.timeout = 1
        self.torrent = torrent
        self.infohash = random_infohash()
        self.test = False
        self.duration = 600

        # file which should be parsed
        self.file = arguments.file
        # magnet-link given
        self.magnet = arguments.magnet
        self.country = arguments.country

        self.queue_type = arguments.queue_type
        self.max_peers = 600
        if arguments.max_peers is not None:
            self.max_peers = arguments.max_peers
        if arguments.hash is not None:
            # infohash of some file on internet,
            # if not specified randomly generate infohash
            self.torrent.change_info(arguments.hash)
        if arguments.counter is not None:
            # How long should wait after queue is empty
            self.timeout = arguments.counter
        if arguments.test is not None:
            # Test of connection !
            self.test = arguments.test
        if arguments.duration is not None:
            # Duration of crawl
            self.duration = arguments.duration
        # local variables for class
        self.n_nodes = 0             # Number of nodes in a specified n-bit zone
        self.tnspeed = 0
        self.no_recieve = 0      # timer that should point how many packets were timed out
        self.info_pool = {}      # infohashes already found
        self.peers_pool = {}     # peers already found
        self.addr_pool = {}      # Addr recieved from
        self.respondent = 0     # Number of respondents
        self.output = ProcessOutput(self, arguments.print_as_country,
                                    arguments.country)
        self.lock = Semaphore()

    def __str__(self):
        return "File: {},\nMagnet-link: {},\nDuration of crawl: {},\
                \nCounter: {}".format(self.file, self.magnet,
                                      self.duration, self.timeout)

    def vprint(self, msg):
        '''
        Print only when -v parameter is present
        '''
        if self.torrent.verbosity:
            print(msg)

    #####################
    # START OF CRAWLING #
    #####################

    def send_handshake(self, peer):
        '''
        send handshake message for bitTorrent connection
        '''
        def _int_to_bytes(data, bytes_len):
            return data.to_bytes(bytes_len, "big")
        message = bytes()
        value = 4
        ver = 1
        message += _int_to_bytes(value << 4 | ver, 1)
        message += _int_to_bytes(0, 1)
        message += _int_to_bytes(randrange(0xffff), 2)
        message += _int_to_bytes(int(time.time()), 4)
        message += _int_to_bytes(0, 4)
        message += _int_to_bytes(0xf000, 4)
        message += _int_to_bytes(randrange(0xffff), 2)
        message += _int_to_bytes(0, 2)

        bt_socket = socket.socket(socket.AF_INET,
                                  socket.SOCK_DGRAM,
                                  socket.IPPROTO_UDP)
        # just to establish connection to get result of this, but handshake
        # should be good to get positive or negative acknowledgment
        # TODO hole punch, those messages are mostly filtered because of firewall
        print("Connecting")
        try:
            bt_socket.sendto(message, (peer[1], peer[2]))
        except OSError:
            return True
        try:
            ready = select.select([bt_socket], [], [], 0.4)
        except (OSError, ValueError, KeyboardInterrupt):
            bt_socket.close()
            return False
        if ready[0]:
            msg = bt_socket.recvfrom(1024)
        else:
            bt_socket = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM,
                                      socket.IPPROTO_TCP)
            print("Connected")
            try:
                bt_socket = socket.create_connection((peer[1], peer[2]),
                                                     timeout=0.4)
            except socket.error:
                bt_socket.close()
                return False
            bt_socket.close()
            return True
        if msg:
            bt_socket.close()
            return True

        bt_socket.close()
        return False

    def query_for_connectivity(self):
        '''
        Query all found peers for connectivity.
        When respond, then connection is still there and peer is valid, else
        peer is deleted from dictionary.
        '''
        self.torrent.query_socket.close()
        present_time = datetime.datetime.now()
        peers_outdated = []
        for value in self.peers_pool.values():
            past_time = datetime.datetime.strptime(value[0], "%d.%m.%Y %H:%M:%S:%f")
            delta_time = present_time - past_time
            total_seconds = delta_time.total_seconds()
            if int(total_seconds) > 600:
                # TODO rework handshake
                # is_recieved = self.send_handshake(value[1])
                # # outdated peer
                # if not is_recieved:
                peers_outdated.append((value[1]))
        for value in peers_outdated:
            del self.peers_pool[value[1] + ":" + str(value[2])]

    def insert_to_queue(self, nodes):
        '''
        Inserts nodes to queue by given queue type.
        '''
        # remove already asked
        # tmp_set = set(self.addr_pool.keys())
        # node_set = []
        # save_info = []
        # for node in nodes["Nodes"]:
        #     node_set.append(node[1:])
        #     save_info.append(node[:1])

        # not_asked = set(node_set) - tmp_set
        # while not_asked:
        #     item = not_asked.pop()
        #     item = save_info[-1] + item
        #     self.torrent.nodes.put((item))

        # Do not remove already asked
        last_node = None
        for node in nodes["Nodes"]:
            if node == last_node:
                continue
            self.torrent.nodes.put((node))
            last_node = node


    def start_listener(self, thread1):
        '''
        start listener thread. Recieve query packet and decode its body.
        There is shared queue between listener and sender thread.
        '''
        # TODO
        last_time = time.time()
        while True:
            if self.timeout is not None:
                time.sleep(self.timeout)

            # socket is closed no value returned
            try:
                ready = select.select([self.torrent.query_socket], [], [], 0.1)
            except (OSError, ValueError):
                continue

            if ready[0]:
                msg, addr = self.torrent.query_socket.recvfrom(2048)
            else:
                self.no_recieve = self.no_recieve + 0.1
                continue
            msg = decode_krpc(msg)
            if msg is None:
                continue
            self.addr_pool[addr] = {"timestamp": time.time()}
            self.respondent += 1

            pool = {}
            nodes = self.torrent.decode_message(msg, pool)
            # update dictionary by given pool value
            try:
                if nodes["Nodes"]:
                    self.info_pool.update(pool["Nodes"])
                if nodes["Peers"]:
                    self.peers_pool.update(pool["Peers"])
            except KeyError:
                pass
            # when 3/4 of queue is not resolved, do not resolve next
            # Resolution without cleaning queue
            if self.torrent.nodes.qsize() <= self.max_peers * 0.8:
                try:
                    if nodes["Nodes"]:
                        self.insert_to_queue(nodes)
                except KeyError:
                    pass
            #  TODO
            curr = time.time()
            if curr - last_time > 5:
                self.info()
                last_time = time.time()

    def start_sender(self, test=False):
        '''
        start sender thread. There is test parameter to test connection for
        unit testing. Otherwise continuous connection is performed till
        we dont get all nodes from k-zone or duration is exhausted.
        '''
        if test:
            # if test is given perform single message send
            node = self.torrent.nodes.get(True)
            hexdig_self = int(self.infohash, 16)
            hexdig_target = int(node[0], 16)
            self.torrent.query_get_peers(node, self.infohash)
            return 2

        while True:
            if self.timeout is not None:
                time.sleep(self.timeout)
            node = self.torrent.nodes.get(True)

            hexdig_self = int(self.infohash, 16)
            hexdig_target = int(node[0], 16)
            if((hexdig_self ^ hexdig_target) >> 148) == 0:
                try:
                    self.torrent.query_get_peers(node, self.infohash)
                except OSError:
                    return 9
                for i in range(10, 20):
                    tid = get_neighbor(self.infohash, node[0], i)
                    self.torrent.query_get_peers(node, tid)
                    node = self.torrent.nodes.get(True)
            # Speed is less than 2000 bps
            elif self.n_nodes < 2000:
                if self.torrent.nodes.qsize() > self.max_peers * 0.8:
                    for i in range(1, 20):
                        try:
                            self.torrent.query_get_peers(node, self.infohash)
                        except OSError:
                            return 9
                        node = self.torrent.nodes.get(True)
                else:
                    try:
                        self.torrent.query_get_peers(node, self.infohash)
                    except OSError:
                        return 9


    def start_timer(self, thread1, thread2):
        '''
        start thread timer for duration, when exhausted kill threads
        and exit program.
        '''
        self.vprint("Start of duration")
        # sleep for shorter time
        for i in range(self.duration):
            time.sleep(1)
        self.vprint("End of duration")
        # Clear all resources
        self.kill_sender_reciever(thread1, thread2)

    def kill_sender_reciever(self, thread1, thread2=None):
        '''
        kill sender reciever and TorrentDHT socket when there is
        continuous bootstrap.
        '''
        identification = thread1.ident
        try:
            signal.pthread_kill(identification, 2)
        except ProcessLookupError:
            pass

        if thread2 is None:
            return

        identification = thread2.ident
        try:
            signal.pthread_kill(identification, 2)
        except ProcessLookupError:
            pass


    def crawl_begin(self, torrent=None, test=False):
        '''
        Create all threads, duration to count how long program is executed.
        When Ctrl+C is pressed kill all threads
        '''
        if torrent:
            self.torrent.target = torrent

        send_thread = Thread(target=self.start_sender, args=())
        send_thread.daemon = True
        send_thread.start()
        listen_thread = Thread(target=self.start_listener,
                               args=(send_thread,))
        listen_thread.daemon = True
        listen_thread.start()
        duration_thread = Thread(target=self.start_timer,
                                 args=(send_thread, listen_thread))
        duration_thread.daemon = True
        duration_thread.start()

        while True:
            if test:
                time.sleep(5)
                break
            try:
                if self.country:
                    self.lock.acquire()
                    self.output.get_geolocations()
                    self.lock.release()
                else:
                    self.output.get_geolocations()
                time.sleep(1)
            except KeyboardInterrupt:
                self.vprint("\nClearing threads, wait a second")
                break
        if test:
            self.kill_sender_reciever(send_thread, listen_thread)
        else:
            self.query_for_connectivity()
            # self.output.print_geolocations()
            self.info()


    def info(self):
        '''
        Print info for current state of crawling.
        '''
        print("[NodeSet]:%i\t\t[PeerSet]:%i\t\t[12-bit Zone]:%i [%i/s]\t\t[Response]:\
            %.2f%%\t\t[Queue]:%i\t\t" %
              (len(self.info_pool), len(self.peers_pool), self.n_nodes,
               self.tnspeed, self.respondent*100.0 / max(1, len(self.info_pool)),
               self.torrent.nodes.qsize()))

    def diverge_in_location(self, nodes):
        '''
        After climbing to another teritory, do not access it,
        return adjusted list of nodes.
        '''
        iplist = self.output.translate_node(self.info_pool)
        for ip_addr in iplist:
            num = 0
            for node_ip in nodes:
                if node_ip[1] == ip_addr[0]:
                    nodes.remove(nodes[num])
                num = num + 1
        return nodes


    def parse_torrent(self):
        '''
        parse torrent file to get infohash and announce list of nodes for
        better bootstrap.
        '''
        if self.file is not None:
            for file in self.file:
                file_r = open(file, "rb")
                content = file_r.read()
                info_hash = None
                nodes = []
                self.vprint("Torrent file content")
                for key, value in decode_krpc(content).items():
                    key = key.decode('utf-8')
                    if key == "creation date":
                        self.vprint("Creation of file: ")
                        self.vprint(datetime.datetime
                                    .fromtimestamp(value)
                                    .strftime("%Y-%m-%d %H:%M:%S"))
                    if key == "info":
                        info_hash = hashlib.sha1(bencode(value)).hexdigest()
                        # set torrent target
                        self.infohash = get_neighbor(info_hash, self.infohash)
                        self.torrent.target_pool.append(info_hash)

                    if key == "nodes":
                        pass
                    if key == "announce-list":
                        nodes = value
                self.torrent.change_bootstrap(info_hash, nodes, self.queue_type)
                file_r.close()


    def parse_magnet(self):
        '''
        parse magnet link
        '''
        if self.magnet is not None:
            for magnet in self.magnet:
                file_r = open(magnet, "rb")
                content = file_r.read()
                info_hash = re.search(r"urn:.*&(xl|dn)", content.decode('utf-8'))
                # match last `:` and its content
                info_hash = re.search(r"(?:.(?!:))+$", info_hash.group(0))
                self.infohash = get_neighbor(info_hash, self.infohash)
                # set torrent target
                self.torrent.target_pool.append(info_hash.group(0)[1:-3])

########################################
# This should be used in main function #
########################################

def create_monitor(verbosity=False):
    '''
    creates monitor class object. TorrentDHT creates udp socket which is
    binded on `bind_port`. Monitor needs this `dht_socket` and command line
    arguments to be created successfully. Then change of hash and parsing
    can change resolution of crawl. When they are not specified then
    global bootstrap nodes are used instead.
    '''
    args = parse_input_args()
    # This is variant with verbose output to track some lib imported staff
    if args.bind_port is not None:
        torrent_arguments = TorrentArguments()
        dht_socket = TorrentDHT(torrent_arguments, bind_port=args.bind_port,
                                verbosity=verbosity)
    else:
        torrent_arguments = TorrentArguments()
        dht_socket = TorrentDHT(torrent_arguments, verbosity=verbosity)

    # Monitor class needs dht_socket, which is imported from TorrentDHT.py
    monitor = Monitor(args, dht_socket)
    # This variant is only to test connection to BOOTSTRAP_NODES
    if monitor.test:
        result = monitor.start_sender(test=True)
        exit(result)
    monitor.torrent.change_arguments(monitor.max_peers, monitor.queue_type)
    monitor.parse_torrent()
    monitor.parse_magnet()
    return monitor
