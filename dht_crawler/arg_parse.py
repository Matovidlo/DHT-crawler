#!/usr/bin/env python3
'''
Created by Martin Vaško
Argument parser
'''
import argparse as arg

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
    parser.add_argument('--db_format', dest='db_format', action='store_true',
                        help='Prints output in desired format for tarzan'\
                        ' server. It accepts only well formated output.'\
                        ' Cannot combine with --print_as_country.')
    return parser


def parse_input_args():
    '''
    Parse arguments from argParse class
    '''
    args = argument_parser()
    args = args.parse_args()
    return args
