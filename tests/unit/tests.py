#!/usr/bin/env python3
'''
Created by Martin Vaško
'''
import time
import datetime
import os
import re
from unittest import TestCase, main
# user defined classes
from monitor import Monitor
from arg_parse import argument_parser
from torrent_dht import TorrentDHT, TorrentArguments, decode_peers


class TestCrawler(TestCase):
    '''
    Unit test class which is responsible to execute unit tests given below
    '''
    def test_connection(self):
        '''
        tests connection of dht_socket and Monitor.
        '''
        parser = argument_parser()
        result = parser.parse_args(['--test'])
        args = TorrentArguments()
        try:
            dht_socket = TorrentDHT(args)
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        self.assertEqual(monitor.start_sender(test=True), 1)
        monitor.crawl_begin(test=True)
        dht_socket.query_socket.close()


    def test_torrent_parser(self):
        '''
        this should take care of parser sha1 infohash.
        '''
        parser = argument_parser()
        cwd = os.getcwd()
        cwd = re.search(r"([^\/]+)$", cwd)
        cwd = cwd.group(0)
        file = './examples/dht_example.torrent'
        if cwd == "tests":
            file = "../examples/dht_example.torrent"
        # elif cwd == "monitoring":
            # file = './examples/dht_example.torrent'
        result = parser.parse_args(['--file',
                                    file])
        args = TorrentArguments()
        try:
            dht_socket = TorrentDHT(args)
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        monitor.parse_torrent()
        value = monitor.torrent.infohash_list[1][0]
        self.assertEqual(value, 'fb6e3624037cc9e4662a0698031659e6b4883b24')
        dht_socket.query_socket.close()


    def test_magnet_parser(self):
        '''
        This test should try magnet_parser.
        '''
        parser = argument_parser()
        cwd = os.getcwd()
        cwd = re.search(r"([^\/]+)$", cwd)
        cwd = cwd.group(0)
        file = './examples/magnet-link_fedora'
        if cwd == "tests":
            file = "../examples/magnet-link_fedora"
        result = parser.parse_args(['--magnet', file])
        args = TorrentArguments()
        try:
            dht_socket = TorrentDHT(args)
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        monitor.parse_magnet()
        value = monitor.torrent_name
        self.assertEqual(value, "Fedora-LXDE-Live-x86_64-27")
        dht_socket.query_socket.close()


    def test_query_for_connectivity(self):
        '''
        Test monitor method which should remove outdated peers.
        '''
        parser = argument_parser()
        result = parser.parse_args()
        args = TorrentArguments()
        try:
            dht_socket = TorrentDHT(args)
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        monitor.peers_pool = {"147.229.14.12:58431":
                              ["28.04.2018 07:27:14:606460",
                               ("token", "147.229.14.12", 58431)]}
        monitor.query_for_connectivity()
        self.assertIsInstance(monitor.peers_pool, dict)
        monitor.peers_pool = {"147.229.14.12:58431":
                              [datetime.datetime.now()
                               .strftime('%d.%m.%Y %H:%M:%S:%f'),
                               ("token", "147.229.14.12", 58431)]}
        monitor.query_for_connectivity()
        self.assertIsNotNone(monitor.peers_pool)


    def test_insert_to_peerpool(self):
        '''
        Test should change record when is same as already inserted
        '''
        info_pool = {}
        decode_peers('ba60a7a1ec51fc9a37ff410bbb243fcfe162d43f',
                     [b'v]\xb6\xd1\x1dO'], info_pool, 'token1')
        past_time = datetime.datetime.strptime(info_pool['118.93.182.209:7503'][0],
                                               "%d.%m.%Y %H:%M:%S:%f")
        time.sleep(5)
        decode_peers('ba60a7a1ec51fc9a37ff410bbb243fcfe162d43f',
                     [b'v]\xb6\xd1\x1dO'], info_pool, 'token2')
        current_time = datetime.datetime.strptime(info_pool['118.93.182.209:7503'][0],
                                                  "%d.%m.%Y %H:%M:%S:%f")
        delta_time = current_time - past_time
        total_seconds = delta_time.total_seconds()
        # 5 second delay should be displayed because of actualized entry
        self.assertEqual(int(total_seconds), 5)


    def test_get_geolocations(self):
        '''
        Tests getting geolocation of ip adress.
        '''
        parser = argument_parser()
        result = parser.parse_args(['--print_as_country'])
        args = TorrentArguments()
        try:
            dht_socket = TorrentDHT(args)
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        monitor.peers_pool = {"147.229.14.12:58431":
                              [datetime.datetime.now()
                               .strftime('%d.%m.%Y %H:%M:%S:%f'),
                               ("token", "147.229.14.12", 58431)]}
        monitor.output.get_geolocations()
        self.assertEqual(next(iter(monitor.output.country_city)), "Czechia:Brno")


if __name__ == '__main__':
    main()
