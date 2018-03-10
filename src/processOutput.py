#!/usr/bin/env python3
import urllib.request
import json

'''
Create by Martin Vasko
3BIT, Brno, Faculty of Information Technology.
'''


class ProcessOutput():
    '''
    Process output to process regex or to remove duplicities
    '''

    def __init__(self, monitor, country):
        self.monitor = monitor
        # class variables to save position and information about node
        self.ip = {}
        self.country_city = {}
        if country is not None:
            self.print_country = country
        else:
            self.print_country = False
        # TODO
        # self.latitude = {}
        # self.longitude = {}
        self.ipPool = {}

    def get_locations(self):
        '''
        get real locations of ip addresses
        '''
        if self.print_country:
            self.parse_ips()
            for key, value in self.ipPool.items():
                for ip_addr in value:
                    # FIXME when freegeoip is down we need another website to
                    # get this kind of information
                    urlFoLaction = "http://www.freegeoip.net/json/{0}".format(
                        ip_addr)
                    locationInfo = json.loads(urllib.request.urlopen(
                        urlFoLaction).read())
                    iplist = []
                    if locationInfo['country_name'] + ":" +
                    locationInfo['city'] in self.country_city:
                        iplist = self.fill_locations(locationInfo)
                    else:
                        iplist = [str(locationInfo['ip'])]
                    self.country_city[locationInfo['country_name'] + ":" +
                                      locationInfo['city']] = iplist
                    # FIXME
                    # print(self.country_city)
                    # print ('Latitude: ' + str(locationInfo['latitude']))
                    # print ('Longitude: ' + str(locationInfo['longitude']))
        pass

    def parse_ips(self):
        iplist = []
        for key, value in self.monitor.infoPool.items():
            for val in value:
                iplist.append((val[0]))
        self.ipPool["ip"] = iplist

    def fill_locations(self, locationInfo, iplist=[]):
        '''
        fill various information to dictionary
        '''
        iplist = self.country_city[locationInfo['country_name'] + ":" +
                                   locationInfo['city']]
        is_in_list = False
        for ip in iplist:
            if str(ip) == str(locationInfo['ip']):
                is_in_list = True
        if not is_in_list:
            iplist.append(str(locationInfo['ip']))
        return iplist

    def print_locations(self):
        if self.print_country:
            print(json.dumps(self.country_city, indent=4, sort_keys=True))
        else:
            print(json.dumps(self.monitor.infoPool, indent=4, sort_keys=True))
