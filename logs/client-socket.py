#!/usr/bin/env python3
'''
Created
'''

import os
import sys
import subprocess
import socket
import fnmatch
import time
import re

PORT = 20183
READ = '-r'
SEND = '-s'
READNC = '-r-nc'
READSOC = '-r-soc'
SENDSOC = '-s-soc'
PACKET_SIZE = 2048

class Client(object):
    def __init__(self, port):
        self.host = "sec6net-mv15.fit.vutbr.cz"
        self.port = port
        self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)

    """Sending sync socket for server"""
    def sendSync(self, mode):
        try:
            self.sock.connect((self.host, self.port))
        except OSError:
            self.sock = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))

        print ('Sending sync socket')
        self.sock.send(mode.encode())
        if mode == READNC: #just for NetCat
            self.sock.close()
        time.sleep(0.2)

    """Sending file via IPv6 Socket"""
    def sendFile(self, fileName):
        #self.sock.connect((self.host, self.port))
        try:
            f = open(fileName,'rb')
        except Exception as err:
            print ("Can not open the file:", err)
            return
        print ('Sending via socket')
        l = f.read(PACKET_SIZE)
        while (l):
            self.sock.send(l)
            l = f.read(PACKET_SIZE)
        f.close()
        print ("Sending done")
        self.sock.shutdown(socket.SHUT_WR)
        resp = self.sock.recv(PACKET_SIZE)
        print ("Server responded: %s" % resp.decode())
        self.sock.close()
        pass

    """Sending file via Netcat"""
    def sendFileNC(self, fileName):
        
        command = "nc -6 " + self.host + " " + str(self.port) + " < " + fileName
        #print (command)
        print ('Sending file:\"%s\" via Netcat' % fileName)
        try:
            check = subprocess.call(command, shell=True) 
            if check != 0 :
                print ("Connection to the server wasnt established.")
            #else:
            #    print ("File was sended successfully." )
        except OSError as  err:
            print ("Exception:subprocess.call()", err )
            
        pass
        
    """Sending file via IPv6 Socket"""
    def recFile(self, fileName):
        print ( "Receiving data" )
        self.sock.settimeout(5)
        first = True
        with open(fileName, 'wb') as f:
            while 1:
                try:
                    data = self.sock.recv(PACKET_SIZE)
                    if not data:
                        print ( "No more data\n" )
                        response = "Data accepted\n"
                        self.sock.sendall(response.encode())
                        break
                    else:
                        if first:
                            first = False
                            if len(data.decode()) < 50:
                                if 'Unexpected name of file' in data.decode() or 'Unknown request' in data.decode():
                                    print ( "Error server response:", data.decode() )
                                    break
                        f.write(data)
                except KeyboardInterrupt:
                    print ("keyboardInterrupt")
                    break
                except socket.timeout:
                    print ("Timeout - No more data\n")
                    response = "Timeout - saving data as a file\n"
                    self.sock.sendall(response.encode())
                    break
            self.sock.close()
            f.close()
        pass


    
    def recFileNC(self, fileName):
        
        command = "nc -6 -l " + str(client.port+1) + " >> " + fileName
        print (command)
        print ('Receiving via Netcat')
        try:
            check = subprocess.call(command, shell=True) 
            if check != 0 :
                print ("Connection to the server wasnt established.")
            #else:
            #    print ("File was accepted successfully." )
        except KeyboardInterrupt:
            print ("KeyboardInterrupt")
            pass
        except OSError as err:
            print ("Exception:subprocess.call()", err)
        pass


if __name__=="__main__":
    usage = ("Usage for sending data:   client.py -s inputFile/prefixOfFiles\n"\
            + "Usage for receiving data: client.py -r [demanding_files]")
    if len(sys.argv) < 2:
        print ( usage )
        sys.exit(0)

    client = Client(PORT)
    if sys.argv[1] == SEND:
        try:
            files = sys.argv[2:]
        except:
            print ("You didnt choose any ipnut file")
            print (usage)
            sys.exit(0)

        # regex for files starting with prefix
        for file in files:
            # pomFile = files[0] + "*"
            # files = []
            # for file in os.listdir('.'):
            #     if fnmatch.fnmatch(file, pomFile):
            #         print ("Loading File:", file)
            #         files.append(file)
            # input is regular expression
            for list_file in os.listdir('.'):
                match = re.search(file, list_file)
                if match:
                    files.append(match.group(0))


        for fileName in files:
            print("Sending File:", fileName)
            client.sendSync(SENDSOC+"-"+fileName)
            client.sendFile(fileName)
            #client.sendFileNC(fileName) - not ready

    elif sys.argv[1] == READ:

        try:
            fileNames = sys.argv[2:]
            if not fileNames:
                fileNames = ['ipv4nodes.json', 'ipv6nodes.json', 'torrentsAndPeers.json'] 
        except:
            print ("You didnt choose any output file")
            print (usage)
            sys.exit(0)

        for fileName in fileNames:
            print ("Asking for file: ", fileName)
            try:
                #client.sendSync(READNC)
                #client.recFileNC(fileName)
                #sync = READSOC+"-"+"fileName
                client.sendSync(READSOC+"-"+fileName)
                client.recFile(fileName)
            except Exception as err:
                print ("Can not connect to the server:", err)

    else:
        print ("Unknown parameters")
        print (usage)
        sys.exit(0)
    pass
