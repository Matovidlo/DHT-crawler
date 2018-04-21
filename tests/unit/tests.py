#!/usr/bin/env python3
import sys
from unittest import TestCase, main
from src.monitor import Monitor, argument_parser
from src.torrentDHT import TorrentDHT


# result = parser.parse_args(sys.argv[2:])
# self.assertEqual(parse_input_args(), 'arg')


class TestCrawler(TestCase):

    def test_connection(self):
        parser = argument_parser()
        result = parser.parse_args(['--test'])
        try:
            dht_socket = TorrentDHT()
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        self.assertEqual(monitor.start_sender(test=True), 2)
        monitor.crawl_begin(test=True)

    def test_torrent_parser(self):
        parser = argument_parser()
        # TODO another file announce parse
        # file = './examples/Chasing Coral (2017) [WEBRip] [1080p] [YTS.AM].torrent'
        file = './examples/dht_example.torrent'
        result = parser.parse_args(['--file',
                                    file])
        try:
            dht_socket = TorrentDHT()
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        monitor.parse_torrent()
        value = monitor.torrent.print_bootstrap()
        self.assertEqual(value, [('192.168.1.1', 6843)])
        monitor.crawl_begin(test=True)

    def test_diverge_in_location(self):
        parser = argument_parser()
        result = parser.parse_args(['--duration', '5'])
        parser.country = "Czechia"
        try:
            dht_socket = TorrentDHT()
        except OSError:
            self.assertRaises(OSError)
            return
        monitor = Monitor(result, dht_socket)
        monitor.info_pool = {'abc': [('147.229.216.41', 6881)]}
        dict_pool = {'abc': [('147.229.216.41', 6881)]}
        self.assertEqual(monitor.diverge_in_location(dict_pool), {})
        monitor.crawl_begin(test=True)

if __name__ == '__main__':
    main()
