#!/usr/bin/env python3
'''
Created by Martin Vasko
3BIT, Brno, Faculty of Information Technology.

Brief information:
This is implementation of monitoring BiTtorrent with Kademlia DHT.
Whole monitor class which will be presented next is going to be supported by
torrentDHT implementation, which was implemented by Martin Vasko.
'''
import signal
import time
import datetime
import hashlib
import select
import re
import socket
from threading import Thread, Semaphore
from bencoder import bencode
# from handshake import TorrentHandshake
from arg_parse import parse_input_args
from torrent_dht import TorrentDHT, TorrentArguments,\
                       random_infohash, decode_krpc, get_neighbor, \
                       get_myip
from process_output import ProcessOutput


def kill_sender_reciever(thread1, thread2=None):
    '''
    kill sender reciever and TorrentDHT socket when there is
    continuous bootstrap.
    '''
    identification = thread1.ident
    try:
        signal.pthread_kill(identification, 2)
    except ProcessLookupError:
        pass

    # take some time to kill reciever thread
    if thread2 is None:
        return

    identification = thread2.ident
    try:
        signal.pthread_kill(identification, 2)
    except ProcessLookupError:
        pass


def init_socket(port):
    '''
    Initialize empty socket to send announce peer messages
    '''
    sock = socket.socket(socket.AF_INET,
                         socket.SOCK_DGRAM,
                         socket.IPPROTO_UDP)
    sock.bind((get_myip(), port))
    return sock

class Monitor:
    """
     Parse it from class methods to monitor class where we want to exchange
     this information.
     Start monitoring and initialize all necessary things at first
    """

    def __init__(self, arguments, torrent):
        """
        Construct a new 'Foo' object.

        :param name: The name of foo
        :param age: The ageof foo
        :return: returns nothing
        """
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

        # print output in db format required for tarzan server
        self.db_format = arguments.db_format
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

        self.sock = self.torrent.query_socket
        self.n_nodes = 0             # Number of nodes in a specified n-bit zone
        self.no_recieve = 0      # timer that should point how many packets were timed out

        self.torrent_name = []
        self.info_pool = {}      # infohashes already found
        self.peers_pool = {}     # peers already found
        self.addr_pool = {}      # Addr recieved from
        self.peer_announce = {}  # pool of NODES announced peers
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

    def clear_monitor(self):
        '''
        clear monitor class before next crawl
        '''
        self.torrent.change_arguments(self.max_peers, self.queue_type)
        self.no_recieve = 0      # timer that should point how many packets were timed out
        self.info_pool = {}      # infohashes already found
        self.peers_pool = {}     # peers already found
        self.addr_pool = {}      # Addr recieved from
        self.peer_announce = {}  # pool of NODES announced peers
        self.respondent = 0     # Number of respondents


    #####################
    # START OF CRAWLING #
    #####################
    def query_for_connectivity(self):
        '''
        Query all found peers for connectivity.
        When respond, then connection is still there and peer is valid, else
        peer is deleted from dictionary.
        '''
        # try:
        #     self.torrent.query_socket.close()
        # except KeyboardInterrupt:
        #     pass
        present_time = datetime.datetime.now()
        peers_outdated = []

        peer_pool = self.peers_pool.values()
        # take all of incomming peers and check them
        for value in peer_pool:
            try:
                past_time = datetime.datetime.strptime(value[0], "%d.%m.%Y %H:%M:%S:%f")
            except KeyboardInterrupt:
                continue
            delta_time = present_time - past_time
            total_seconds = delta_time.total_seconds()
            if int(total_seconds) > 600:
                # outdated peer
                peers_outdated.append(value[1])

        # send announce peer to 'start' session
        # query queried node
        for value in peers_outdated:
            del self.peers_pool[value[1] + ":" + str(value[2])]

    def insert_to_queue(self, nodes):
        '''
        Inserts nodes to queue by given queue type.
        '''
        # Do not remove already asked
        last_node = None
        for node in nodes["Nodes"]:
            if node == last_node:
                continue
            self.torrent.nodes.put((node))
            last_node = node


    def process_and_update(self, ready, last_time):
        '''
        process packet and update all necesseties like info_pool, peers_pool.
        When decoding failed or not ready socket for recieving return back to
        listener thread.
        '''
        if ready[0]:
            try:
                msg, addr = self.sock.recvfrom(2048)
            except OSError:
                return last_time
        else:
            self.no_recieve = self.no_recieve + 0.1
            return last_time
        msg = decode_krpc(msg)
        if msg is None:
            return last_time
        self.addr_pool[addr] = {"timestamp": time.time()}

        pool = {}
        nodes = self.torrent.decode_message(msg, pool, self.peer_announce, addr)
        # update dictionary by given pool value
        try:
            if nodes["Nodes"]:
                self.info_pool.update(pool["Nodes"])
                self.respondent += 1
            if nodes["Peers"]:
                self.peers_pool.update(pool["Peers"])
        except KeyError:
            pass

        # Resolution without cleaning queue
        if self.torrent.nodes.qsize() <= self.max_peers * 0.9:
            try:
                if nodes["Nodes"]:
                    self.insert_to_queue(nodes)
            except KeyError:
                pass

        if not self.db_format:
            curr = time.time()
            if curr - last_time > 5:
                self.info()
                last_time = time.time()
            return last_time


    def start_listener(self):
        '''
        start listener thread. Recieve query packet and decode its body.
        There is shared queue between listener and sender thread.
        '''
        last_time = time.time()
        while True:
            if self.timeout is not None:
                time.sleep(self.timeout)

            # socket is closed no value returned
            try:
                ready = select.select([self.sock], [], [], 0.1)
            except (OSError, ValueError):
                continue

            # if self.torrent.nodes.qsize() > self.max_peers * 0.3:
                # for _ in range(1, 20):
                    # last_time = self.process_and_update(ready, last_time)
            # else:
            last_time = self.process_and_update(ready, last_time)


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
            self.torrent.query_get_peers(node, self.infohash, self.sock)
            return 1

        while True:
            if self.timeout is not None:
                time.sleep(self.timeout)
            node = self.torrent.nodes.get(True)

            hexdig_self = int(self.infohash, 16)
            hexdig_target = int(node[0], 16)
            if((hexdig_self ^ hexdig_target) >> 148) == 0:
                # we are close, we should send more packets but it is slow
                # on recieving thread because of decoding and composing
                # dictionaries
                try:
                    self.torrent.query_get_peers(node, self.infohash, self.sock)
                except OSError:
                    return 9
            # Speed is less than 2000 bps
            else:
                try:
                    self.torrent.query_get_peers(node, self.infohash, self.sock)
                except OSError:
                    return 9


    def start_timer(self, thread1, thread2):
        '''
        start thread timer for duration, when exhausted kill threads
        and exit program.
        '''
        self.vprint("Start of duration")
        # sleep for shorter time
        for _ in range(self.duration):
            time.sleep(1)
        self.vprint("End of duration")
        # Clear all resources
        kill_sender_reciever(thread1, thread2)


    def crawl_begin(self, torrent=None, test=False):
        '''
        Create all threads, duration to count how long program is executed.
        When Ctrl+C is pressed kill all threads

        Parameters
        ----------
        torrent : infohash
            20 bytes long infohash which should be used as part of monitoring.
        test : bool
            This paramter is for testing connection.

        '''
        self.clear_monitor()
        if torrent:
            self.torrent.infohash_list[2] = torrent

        send_thread = Thread(target=self.start_sender, args=())
        send_thread.daemon = True
        send_thread.start()
        listen_thread = Thread(target=self.start_listener,
                               args=())
        listen_thread.daemon = True
        listen_thread.start()
        duration_thread = Thread(target=self.start_timer,
                                 args=(send_thread, listen_thread))
        duration_thread.daemon = True
        duration_thread.start()
        while True:
            if test:
                break
            try:
                if self.country:
                    self.lock.acquire()
                    self.output.get_geolocations()
                    self.lock.release()
                time.sleep(1)
            except KeyboardInterrupt:
                self.vprint("\nClearing threads, wait a second")
                break
        self.query_for_connectivity()
        if self.db_format or self.output.print_country:
            self.output.get_geolocations()
            self.output.print_chosen_output()
        if not self.db_format:
            self.info()
            print("Time spend not recieving any UDP response: {}"
                  .format(self.no_recieve))

    def info(self):
        '''
        Print info for current state of crawling.
        '''
        bernouli = self.respondent*100.0 / max(1, len(self.info_pool))
        if bernouli > 100:
            bernouli = 100.00
        print("[NodeSet]:%i\t\t[PeerSet]:%i\t\t[Bernoulli process]:\
            %.2f%%\t\t[Queue]:%i\t\t" %
              (len(self.info_pool), len(self.peers_pool),
               bernouli, self.torrent.nodes.qsize()))

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


    def get_torrent_name(self, value):
        '''
        get name of torrent from torrent file

        Parameters
        ----------
        value : dict
            This should contain encoded name of torrent.

        Returns
        -------
        self.torrent_name
            Parsed torrent name from value dictionary.
        '''
        for name, name_val in value.items():
            name = name.decode('utf-8')
            if name == "name":
                self.torrent_name.append(name_val.decode("utf-8"))

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
                if not decode_krpc(content):
                    raise TypeError("WrongFileType")
                if not isinstance(decode_krpc(content), dict):
                    raise TypeError("WrongFileType")
                for key, value in decode_krpc(content).items():
                    key = key.decode('utf-8')
                    if key == "creation date":
                        self.vprint("Creation of file: ")
                        self.vprint(datetime.datetime
                                    .fromtimestamp(value)
                                    .strftime("%Y-%m-%d %H:%M:%S"))
                    if key == "info":
                        self.get_torrent_name(value)
                        info_hash = hashlib.sha1(bencode(value)).hexdigest()
                        # set torrent target
                        self.infohash = get_neighbor(info_hash, self.infohash)
                        self.torrent.infohash_list[1].append(info_hash)

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
                content = file_r.read().decode('utf-8')
                name = re.search(r"&dn.*&(xt|tr)", content)
                name = re.search(r"^((?!tr.*).)*", name.group(0))
                self.torrent_name.append(name.group(0)[4:-1])

                info_hash = re.search(r"urn:.*&(xl|dn)", content)
                # match last `:` and its content
                info_hash = re.search(r"(?:.(?!:))+$", info_hash.group(0))
                info_hash = info_hash.group(0)[1:-3]
                self.infohash = get_neighbor(info_hash, self.infohash)
                # set torrent target
                self.torrent.infohash_list[1].append(info_hash)
                file_r.close()

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

    Parameters
    ----------
    verbosity : bool
        Indicate verbose output

    Returns
    -------
    object
        Monitor object with initialized DHT socket and parsed arguments.
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
