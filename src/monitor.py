#!/usr/bin/env python3
import argparse as arg
import signal
import time
import datetime
from threading import Thread, Semaphore
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
    parser.add_argument('--ipaddr', type=str, dest='ipaddr', action='store',
                        help='Specify ip addres to which should \
                         be bootstraped.')
    parser.add_argument('--port', type=int, dest='port', action='store',
                        help='Specify port to which should be connection \
                        binded.')
    parser.add_argument('--country', type=str, dest='country',
                        action='store', help='Store country name to \
                        converge only in this country and do not \
                        bootstrap away from it.')
    parser.add_argument('--regex', type=str, dest='regex', action='store',
                        help='Filters output by this regular expression.')
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
    parser.add_argument('--block-timeout', type=int, action='store',
                        help='Timeout for how long should be our connection \
                        blocked.')
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
        self.counter = 1
        self.torrent = torrent
        self.infohash = random_infohash()
        self.test = False
        self.duration = 600

        # regular expression which should parse output/input
        self.regex = arguments.regex
        # file which should be parsed !!
        self.file = arguments.file
        # magnet-link given
        self.magnet = arguments.magnet
        self.country = arguments.country

        self.ipaddr = arguments.ipaddr
        self.port = arguments.port
        if arguments.ipaddr and arguments.port is None:
            self.vprint("No addr and port set")

        if arguments.hash is not None:
            '''
            infohash of some file on internet,
            if not specified randomly generate infohash
            '''
            self.infohash = arguments.hash
        if arguments.counter is not None:
            # How long should wait after queue is empty
            self.counter = arguments.counter
        if arguments.test is not None:
            # Test of connection !
            self.test = arguments.test
        if arguments.duration is not None:
            # Duration of crawl
            self.duration = arguments.duration

        # local variables for class
        self.n_nodes = 0             # Number of nodes in a specified n-bit zone
        self.tnspeed = 0
        self.info_pool = {}      # infohashes already found
        self.addr_pool = {}      # Addr recieved from
        self.respondent = 0     # Number of respondents
        self.output = ProcessOutput(self, arguments.print_as_country,
                                    arguments.country)
        self.lock = Semaphore()

    def __str__(self):
        return "Hash: {},\nRegex: {},\nFile: {},\nMagnet-link: {},\
    \nDuration of crawl: {}, \nCounter: {}".format(self.infohash, self.regex,
                                                   self.file, self.magnet,
                                                   self.duration, self.counter)

    def vprint(self, msg):
        '''
        Print only when -v parameter is present
        '''
        if self.torrent.verbosity:
            print(msg)

    #####################
    # START OF CRAWLING #
    #####################

    def start_listener(self):
        while True:
            if self.counter is not None:
                time.sleep(self.counter)
            try:
                msg, addr = self.torrent.query_socket.recvfrom(1024)
            except OSError:
                # probably closed socket
                return 9
            try:
                msg = decode_krpc(msg)
            except Exception as instance:
                print("Malformed {}".format(instance.args))
                continue
            nodes = self.torrent.decode_message(msg, self.info_pool)
            # When --country is passed as argument, diverge it
            if self.country is not None:
                self.lock.acquire()
                nodes = self.diverge_in_location(nodes)
                self.lock.release()

            if self.torrent.info.qsize() <= 150:
                for node in nodes:
                    infohash = self.torrent.info.get(True)
                    if self.torrent.info.empty():
                        self.torrent.info.put((node))
                    elif node[0] != infohash[0]:
                        self.torrent.info.put((infohash))
                        self.torrent.info.put((node))

            self.addr_pool[addr] = {"timestamp": time.time()}
            if self.country is None:
                self.respondent += 1

    def start_sender(self, test=False):
        if not test:
            while True:
                if self.counter is not None:
                    time.sleep(self.counter)
                node = self.torrent.info.get(True)
                try:
                    hexdig_self = int.from_bytes(
                        self.infohash, byteorder='big')
                except ValueError:
                    hexdig_self = int(self.infohash, 16)
                try:
                    hexdig_target = int.from_bytes(node[0], byteorder='big')
                except ValueError:
                    hexdig_target = int(node[0], 16)

                # TODO metrics
                if((hexdig_self ^ hexdig_target) >> 148) == 0:
                    try:
                        self.torrent.query_find_node(node, infohash=self.infohash)
                    except OSError:
                        return 9
                    # for i in range(1, 5):
                    #     tid = get_neighbor(self.infohash,
                    #                        node[0], i)
                    #     self.torrent.query_find_node(node, tid)
                # Speed is less than 2000 bps
                elif self.n_nodes < 2000:
                    try:
                        self.torrent.query_find_node(node, infohash=self.infohash)
                    except OSError:
                        return 9

        # if test is given perform single message send
        node = self.torrent.info.get(True)
        hexdig_self = int.from_bytes(self.infohash, byteorder='big')
        hexdig_target = int.from_bytes(node[0], byteorder='big')
        self.torrent.query_find_node(node, infohash=self.infohash)
        self.torrent.rejoin.cancel()
        # return 2 to make test connection assertion
        return 2

    def start_timer(self, thread1, thread2):
        self.vprint("Start of duration")
        # sleep for shorter time
        for i in range(self.duration):
            time.sleep(1)
        self.vprint("End of duration")
        # Clear all resources
        self.kill_sender_reciever(thread1, thread2)

    def kill_sender_reciever(self, thread1, thread2):
        # TODO
        # self.torrent.rejoin.cancel()
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

    def clear_resources(self):
        # TODO
        # self.torrent.rejoin.cancel()
        self.torrent.query_socket.close()

    def crawl_begin(self, test=False):
        # Create all threads, duration to count how long program is executed
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
                '''
                    self.counter = 10 if self.torrent.info.qsize()
                    else self.counter - 1
                '''
                if self.country:
                    self.lock.acquire()
                    self.output.get_locations()
                    self.lock.release()
                else:
                    # self.info()
                    self.output.get_locations()
                time.sleep(1)
            except KeyboardInterrupt:
                self.vprint("\nClearing threads, wait a second")
                self.clear_resources()
                break
        self.info()
        self.output.print_locations()

    def info(self):
        print("[NodeSet]:%i\t\t[12-bit Zone]:%i [%i/s]\t\t[Response]:\
            %.2f%%\t\t[Queue]:%i\t\t" %
              (len(self.info_pool), self.n_nodes, self.tnspeed,
               self.respondent*100.0 / max(1, len(self.info_pool)),
               self.torrent.info.qsize()))

    def diverge_in_location(self, nodes):
        '''
        After climbing to another teritory, do not access it,
        return adjusted list of nodes.
        '''
        iplist = self.output.translate_node(self.info_pool)
        print(iplist)
        for ip_addr in iplist:
            num = 0
            for node_ip in nodes:
                if node_ip[1] == ip_addr[0]:
                    nodes.remove(nodes[num])
                num = num + 1
        return nodes

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
                for key, value in decode_krpc(content).items():
                    key = key.decode('utf-8')
                    if key == "creation date":
                        self.vprint("Creation of file: ")
                        self.vprint(datetime.datetime.
                                    fromtimestamp(value).
                                    strftime("%Y-%m-%d %H:%M:%S"))
                    if key == "info":
                        for info_key, info_value in value.items():
                            info_hash = self.parse_torrent_info(info_key,
                                                                info_value)
                    if key == "nodes":
                        self.torrent.change_bootstrap(info_hash, value)
                    # TODO url-list parse to join to swarm with torrent file
                    print(key)
                    # Try it with real torrent file
                file_r.close()
        '''
         If no file given in self.file passing this function and continue
         without torrent file
        '''

    def change_ip(self):
        if self.ipaddr is not None and self.port is not None:
            self.torrent.clear_bootstrap()
            self.torrent.change_bootstrap(self.infohash,
                                          (self.ipaddr, self.port))
        if self.ipaddr is not None:
            self.torrent.clear_bootstrap()
            self.torrent.change_bootstrap(self.infohash,
                                          (self.ipaddr, 6881))

    def parse_magnet(self):
        '''
        # FIXME
        parse magnet link
        '''
        pass


#################
# Start of main #
#################


def create_monitor(verbosity=False):
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
    dht_socket.change_hash(monitor.infohash)

    # This variant is only to test connection to BOOTSTRAP_NODES
    if monitor.test:
        result = monitor.start_sender(test=True)
        exit(result)
    monitor.parse_torrent()
    monitor.change_ip()
    return monitor
