#!/usr/bin/env python3
'''
Create by Martin Vasko
3BIT, Brno, Faculty of Information Technology.
'''
import urllib.request
import json


class ProcessOutput():
    '''
    Process output to process regex or to remove duplicities
    '''

    def __init__(self, monitor, country_print, country):
        self.monitor = monitor
        # class variables to save position and information about node
        self.country_city = {}
        if country_print is not None:
            self.print_country = country_print
        else:
            self.print_country = False
        self.db_format = self.monitor.db_format
        self.country_name = country
        # info_pool, ip_pool, port_pool
        self.pools = [{}, {}, {}]

    def translate_node(self, nodes):
        '''
        translates nodes ip address to equivalent country name, check wether
        they corelate with name given as parameter, returns adjusted ip
        addresses which should be deleted from `nodes` list.
        '''
        iplist = []
        infolist = []
        for info, node in nodes.items():
            url_of_location = "http://www.freegeoip.net/json/{}"\
                .format(node[0][0])
            location_info = json.loads(urllib.request.urlopen(url_of_location)
                                       .read())
            if location_info['country_name'] is None:
                iplist.append(node[0])
                infolist.append(info)
            else:
                if self.country_name != location_info['country_name']:
                    iplist.append(node[0])
                    infolist.append(info)
        for i in infolist:
            del nodes[i]

        return iplist


    def parse_ips(self):
        '''
        initiate pool of ip addresses port and infohashes for geolocation.
        '''
        iplist = []
        infolist = []
        portlist = []
        for value in self.monitor.peers_pool.values():
            infolist.append((value[0]))
            iplist.append((value[1][1]))
            portlist.append((value[1][2]))
        self.pools[0] = infolist
        self.pools[1] = iplist
        self.pools[2] = portlist


    def fill_locations(self, location_info, iplist=None):
        '''
        fill various information to dictionary
        '''
        iplist = self.country_city[location_info['country_name'] + ":" +
                                   location_info['city']]
        is_in_list = False
        for ip_addr in iplist:
            if str(ip_addr['ip']) == str(location_info['ip']):
                is_in_list = True
        if not is_in_list:
            iplist.append({"ip": str(location_info['ip']),
                           "latitude": str(location_info['latitude']),
                           "longitude": str(location_info["longitude"])})
        return iplist


    def get_geolocations(self):
        '''
        get real locations of ip addresses
        '''
        if self.print_country:
            self.parse_ips()
            for ip_addr in self.pools[1]:
                # FIXME when freegeoip is down we need another website to
                # get this kind of information
                url_of_location = "http://www.freegeoip.net/json/{0}".format(
                    ip_addr)
                try:
                    location_info = urllib.request.urlopen(
                        url_of_location).read()
                except urllib.error.HTTPError:
                    continue
                iplist = []
                location_info = json.loads(location_info.decode("utf-8"))
                if location_info['country_name'] + ":" + \
                        location_info['city'] in self.country_city:
                    iplist = self.fill_locations(location_info)
                else:
                    iplist = [{"ip": str(location_info['ip']),
                               "port": self.pools[2].pop(0),
                               "infohash": self.pools[0].pop(0),
                               "latitude": str(location_info['latitude']),
                               "longitude": str(location_info['longitude'])
                              }]
                self.country_city[location_info['country_name'] + ":" +
                                  location_info['city']] = iplist


    def print_chosen_output(self):
        '''
        print geolocation when argument --print_as_country is specified, else
        print as json object with no resolution.
        '''
        if self.print_country:
            print(json.dumps(self.country_city, indent=4, sort_keys=True))
            print(json.dumps(self.monitor.peer_announce, indent=4, sort_keys=True))
            print("Time spend not recieving any UDP response: {}"
                  .format(self.monitor.no_recieve))
        if self.db_format:
            print("{{\"{}\":".format(self.monitor.torrent.infohash_list[2]))

            print("{\"peers\": [")
            for peer in self.monitor.peers_pool.values():
                print("\t{{\"timestamp\":{}, \"addr\": [\"{}\", {}]}},"
                      .format(peer[0], str(peer[1][1]), peer[1][2]))
            print("]")
            print("\"nodes\": [")
            for key, node in self.monitor.peer_announce.items():
                print("\t{{\"timestamp\": {}, \"nodeID\": \"{}\", "\
                      "\"nodeAddr\": [\"{}\", {}]}},"
                      .format(node[1], key, node[0][1], node[0][2]))
            print("]")
            print("\"name\": \"{}\"".format(self.monitor.torrent_name.pop()))
            print("}")
            print("}")
