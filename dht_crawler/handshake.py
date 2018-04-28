#!/usr/bin/env python3
'''
Created by Martin Vaško
part of BT library which should implement handshake methods.
'''
import socket
import time
import select
from random import randrange
from torrent_dht import get_myip

class TorrentHandshake:
    '''
    Torrent handshake class to process initial handshake with peer to prove
    its connectivity and filter it from peer pool if non respondend.
    '''
    def __init__(self, port):
        self.bt_socket = socket.socket(socket.AF_INET,
                                       socket.SOCK_DGRAM,
                                       socket.IPPROTO_UDP)
        self.micro_socket = socket.socket(socket.AF_INET,
                                          socket.SOCK_STREAM,
                                          socket.IPPROTO_TCP)
        self.bt_socket.bind(get_myip(), port)
    def send_handshake(self, peer):
        '''
        send handshake message for bitTorrent connection
        '''
        # FIXME split to create handshake message
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

        # just to establish connection to get result of this, but handshake
        # should be good to get positive or negative acknowledgment
        # TODO hole punch, those messages are mostly filtered because of firewall
        print("Connecting")
        try:
            self.bt_socket.sendto(message, (peer[1], peer[2]))
        except OSError:
            return True
        try:
            ready = select.select([self.bt_socket], [], [], 0.4)
        except (OSError, ValueError, KeyboardInterrupt):
            self.bt_socket.close()
            return False
        if ready[0]:
            msg = self.bt_socket.recvfrom(1024)
        else:
            try:
                self.micro_socket = socket.create_connection((peer[1],
                                                              peer[2]),
                                                             timeout=0.4)
            except socket.error:
                self.micro_socket.close()
                return False
            self.micro_socket.close()
            return True
        if msg:
            self.bt_socket.close()
            return True

        self.bt_socket.close()
        return False

        # Announce peers that we want to download torrent
        # query_sock = self.init_socket(port[1] + 3200)
        # for value in self.peer_announce.values():
        #     self.torrent.query_announce_peer(value[0], self.infohash,
        #                                      (port[1] + 3200), query_sock)
        #     try:
        #         ready = select.select([query_sock], [], [], 0.1)
        #     except (OSError, ValueError):
        #         continue
        #     msg = None
        #     if ready[0]:
        #         msg, _ = query_sock.recvfrom(2048)
        #     else:
        #         continue

        #     if not msg:
        #         continue
        #     msg = decode_krpc(msg)
        #     if msg is None:
        #         continue

