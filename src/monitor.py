#!/usr/bin/env python3
import argparse as arg
import signal
import time
import datetime
import hashlib
import select
import re
from threading import Thread, Semaphore
from bencoder import bencode
try:
    from torrentDHT import TorrentDHT, TorrentArguments,\
                           random_infohash, decode_krpc
    from processOutput import ProcessOutput
except ImportError:
    from src.torrentDHT import TorrentDHT, TorrentArguments,\
                               random_infohash, decode_krpc
    from src.processOutput import ProcessOutput

'''
Created by Martin Vasko
3BIT, Brno, Faculty of Information Technology.

Brief information:
This is implementation of monitoring BiTtorrent with Kademlia DHT.
Whole monitor class which will be presented next is going to be supported by
torrentDHT implementation, which was implemented by Martin Vasko.
'''


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
    # parser.add_argument('--ipaddr', type=str, dest='ipaddr', action='store',
    #                     help='Specify ip addres to which should \
    #                      be bootstraped.')
    # parser.add_argument('--port', type=int, dest='port', action='store',
    #                     help='Specify port to which should be connection \
    #                     binded.')
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

    def insert_to_queue(self, nodes, queue_type):
        '''
        Inserts nodes to queue by given queue type.
        '''
        if queue_type == "Nodes":
            for node in nodes["Nodes"]:
                if self.torrent.nodes.empty():
                    self.torrent.nodes.put((node))
                    continue
                infohash = self.torrent.nodes.get(True)
                if node[0] != infohash[0]:
                    self.torrent.nodes.put((infohash))
                    self.torrent.nodes.put((node))
        # elif queue_type == "Peers":
        #     for node in nodes["Peers"]:
        #         self.torrent.peers.put((node))


    def start_listener(self):
        '''
        start listener thread. Recieve query packet and decode its body.
        There is shared queue between listener and sender thread.
        '''
        while True:
            if self.timeout is not None:
                time.sleep(self.timeout)

            # socket is closed no value returned
            try:
                ready = select.select([self.torrent.query_socket], [], [], 0.1)
            except (OSError, ValueError):
                # FIXME
                self.no_recieve = self.no_recieve + 0.1
                continue

            if ready[0]:
                msg, addr = self.torrent.query_socket.recvfrom(2048)
            else:
                continue

            msg = decode_krpc(msg)
            if msg is None:
                continue

            pool = {}
            nodes = self.torrent.decode_message(msg, pool)
            # update dictionary by given pool value
            for key in nodes.keys():
                if key is "Nodes":
                    self.info_pool.update(pool["Nodes"])
                elif key is "Peers":
                    self.peers_pool.update(pool["Peers"])
            # when 3/4 of queue is not resolved, do not resolve next
            # Resolution without cleaning queue
            if self.torrent.nodes.qsize() <= self.max_peers * 0.8:
                for key in nodes.keys():
                    self.insert_to_queue(nodes, key)

            # if len(self.peers_pool) != 0:
            #     for num in range(0, self.max_peers, 2):
            #         self.torrent.nodes.get(True)

            # Resolution with clean queue
            #     for key in nodes.keys():
            #         self.insert_to_queue(nodes, key)
            # else:
            #     # Clear half of queue
            #     for num in range(0, self.max_peers, 2):
            #         self.torrent.nodes.get(True)
            #     for key in nodes.keys():
            #         self.insert_to_queue(nodes, key)

            self.addr_pool[addr] = {"timestamp": time.time()}
            # if self.country is None:
            self.respondent += 1

    def start_sender(self, test=False):
        '''
        start sender thread. There is test parameter to test connection for
        unit testing. Otherwise continuous connection is performed till
        we dont get all nodes from k-zone or duration is exhausted.
        '''
        if not test:
            while True:
                if self.timeout is not None:
                    time.sleep(self.timeout)
                # if self.torrent.peers.empty():
                node = self.torrent.nodes.get(True)
                # else:
                    # node = self.torrent.peers.get(True)

                hexdig_self = int(self.infohash, 16)
                hexdig_target = int(node[0], 16)
                # DEBUG
                # print(hexdig_self, hexdig_target)

                if((hexdig_self ^ hexdig_target) >> 148) == 0:
                    try:
                        self.torrent.query_get_peers(node, self.infohash)
                    except OSError:
                        return 9
                    # FIXME
                    # for i in range(1, 5):
                    #     tid = get_neighbor(self.infohash,
                    #                        node[0], i)
                    #     self.torrent.query_find_node(node, tid)
                # Speed is less than 2000 bps
                elif self.n_nodes < 2000:
                    try:
                        self.torrent.query_get_peers(node, self.infohash)
                    except OSError:
                        return 9

        # if test is given perform single message send
        node = self.torrent.nodes.get(True)
        hexdig_self = int(self.infohash, 16)
        hexdig_target = int(node[0], 16)
        self.torrent.query_get_peers(node, self.infohash)
        self.torrent.rejoin.cancel()

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

    def kill_sender_reciever(self, thread1, thread2):
        '''
        kill sender reciever and TorrentDHT socket when there is
        continuous bootstrap.
        '''
        identification = thread1.ident
        try:
            signal.pthread_kill(identification, 2)
        except ProcessLookupError:
            pass
        identification = thread2.ident
        try:
            signal.pthread_kill(identification, 2)
        except ProcessLookupError:
            pass
        try:
            self.torrent.query_socket.close()
        except ProcessLookupError:
            return


    def crawl_begin(self, torrent, test=False):
        '''
        Create all threads, duration to count how long program is executed.
        When Ctrl+C is pressed kill all threads
        '''
        # TODO process thread probably
        self.torrent.target = torrent
        send_thread = Thread(target=self.start_sender, args=())
        send_thread.daemon = True
        send_thread.start()
        listen_thread = Thread(target=self.start_listener, args=())
        listen_thread.daemon = True
        listen_thread.start()
        duration_thread = Thread(target=self.start_timer,
                                 args=(send_thread, listen_thread))
        duration_thread.daemon = True
        duration_thread.start()

        while True:
            if test:
                self.kill_sender_reciever(send_thread, listen_thread)
            try:
                if self.country:
                    self.lock.acquire()
                    self.output.get_geolocations()
                    self.lock.release()
                else:
                    # self.info()
                    self.output.get_geolocations()
                time.sleep(1)
            except KeyboardInterrupt:
                self.vprint("\nClearing threads, wait a second")
                break
        self.info()
        self.output.print_geolocations()


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
                        self.torrent.target_pool.append(info_hash)

                    if key == "nodes":
                        pass
                    if key == "announce-list":
                        nodes = value
                self.torrent.change_bootstrap(info_hash, nodes)
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

                # set torrent target
                self.torrent.target_pool.append(info_hash.group(0)[1:-3])

#################
# Start of main #
#################

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
    monitor.torrent.change_arguments(monitor.max_peers)
    monitor.parse_torrent()
    monitor.parse_magnet()
    return monitor
