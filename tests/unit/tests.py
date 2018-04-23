#!/usr/bin/env python3
'''
Created by Martin Vaško
'''
import sys
import time
import datetime
from unittest import TestCase, main
sys.path.append('../../src')
from monitor import Monitor, argument_parser
from torrent_dht import TorrentDHT, TorrentArguments, decode_peers


# result = parser.parse_args(sys.argv[2:])
# self.assertEqual(parse_input_args(), 'arg')


class TestCrawler(TestCase):

    def test_connection(self):
        parser = argument_parser()
        result = parser.parse_args(['--test'])
        args = TorrentArguments()
        try:
            dht_socket = TorrentDHT(args)
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        self.assertEqual(monitor.start_sender(test=True), 2)
        # monitor.crawl_begin(test=True)
        dht_socket.query_socket.close()

    def test_torrent_parser(self):
        parser = argument_parser()
        # TODO another file announce parse
        # file = './examples/Chasing Coral (2017) [WEBRip] [1080p] [YTS.AM].torrent'
        file = '../../examples/dht_example.torrent'
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
        value = monitor.torrent.target_pool[0]
        self.assertEqual(value, 'fb6e3624037cc9e4662a0698031659e6b4883b24')
        # monitor.crawl_begin(test=True)
        dht_socket.query_socket.close()

    def test_insert_to_peerpool(self):
        info_pool = {}
        decode_peers('ba60a7a1ec51fc9a37ff410bbb243fcfe162d43f',
                     [b'v]\xb6\xd1\x1dO'], info_pool)
        past_time = datetime.datetime.strptime(info_pool['118.93.182.209:7503'][0],
                                               "%d.%m.%Y %H:%M:%S:%f")
        time.sleep(5)
        decode_peers('ba60a7a1ec51fc9a37ff410bbb243fcfe162d43f',
                     [b'v]\xb6\xd1\x1dO'], info_pool)
        current_time = datetime.datetime.strptime(info_pool['118.93.182.209:7503'][0],
                                                  "%d.%m.%Y %H:%M:%S:%f")
        delta_time = current_time - past_time
        total_seconds = delta_time.total_seconds()
        # 5 second delay should be displayed
        self.assertEqual(int(total_seconds), 5)

    # def test_diverge_in_location(self):
    #     parser = argument_parser()
    #     result = parser.parse_args(['--duration', '5'])
    #     parser.country = "Czechia"
    #     try:
    #         dht_socket = TorrentDHT()
    #     except OSError:
    #         self.assertRaises(OSError)
    #         return
    #     monitor = Monitor(result, dht_socket)
    #     monitor.info_pool = {'abc': [('147.229.216.41', 6881)]}
    #     dict_pool = {'abc': [('147.229.216.41', 6881)]}
    #     self.assertEqual(monitor.diverge_in_location(dict_pool), {})
    #     monitor.crawl_begin(test=True)

if __name__ == '__main__':
    main()
