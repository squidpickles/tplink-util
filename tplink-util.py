#!/usr/bin/env python3

"""
Copyright 2013 Kevin Rauwolf

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import netifaces
import socket
import threading
import collections
import struct
import time

kRemotePort = 28010 # TP-Link devices expect a query on this port
kLocalPort = 28011 # TP-Link devices require query be sent from this port, and will also send responses here
kBufferSize = 256 # Size of receive buffer
kListenTimeout = 1.5 # Listen for responses, timing out this often
kListenWait = 1.0 # How long to wait after sending responses before sending a shutdown to the listener
kStartRequest = b'\x01\x00' # Magic bytes that make up the start of a request
kStartRecord = b'\xff\x00' # Marks the beginning of an IP address record in the request
kEndRecord = b'\xff\xff' # Marks the end of an IP addresss record in the request
kRequestPacketSize = 164 # Request packets are padded with null bytes to this size
kResponseFormat = '>2x4s6s20s128s' # Format for the response
kMaximumLocalAddressCount = 16 # We only put up to this many local addresses in the request
kReportFormat = '{0:<15}   {1:<17}   {2:<12}   {3}' # Makes the columns line up nicely

class Listener(threading.Thread):
    """
    Listens for incoming requests on the UDP socket and adds them to a response
    dictionary
    """

    def __init__(self, sock):
        """ sock - a UDP socket ready to receive responses """
        super().__init__()
        self._socket = sock
        self._listening = False
        self.responses = dict()

    def run(self):
        """ Starts listening """
        self._listening = True
        while self._listening:
            try:
                response, addr = self._socket.recvfrom(kBufferSize)
                self.responses[addr] = response
            except socket.timeout:
                pass

    def stop(self):
        """
        Sends the stop listening signal. The listener may take up to
        kListenTimeout seconds to stop listening.
        """
        self._listening = False

def find_interfaces():
    """
    Gets a list of local interfaces capable of sending IPv4 broadcast messages
    """
    interfaces = collections.defaultdict(list)
    for interface in netifaces.interfaces():
        ifaddresses = netifaces.ifaddresses(interface)
        if netifaces.AF_INET in ifaddresses:
            for link in netifaces.ifaddresses(interface)[netifaces.AF_INET]:
                if 'broadcast' in link and 'addr' in link:
                    interfaces[link['broadcast']].append(link['addr'])
    return interfaces

if __name__ == '__main__':
    interfaces = find_interfaces()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    sock.bind(('', kLocalPort))
    sock.settimeout(kListenTimeout)
    listener = Listener(sock)
    listener.start()

    for broadcast in interfaces.keys():
        addresses = interfaces[broadcast]
        # Seems that if there is only 1 address, the response gets corrupted.
        # The broadcast address appears to be safe.
        if len(addresses) == 1:
            addresses.append(broadcast)
        data = kStartRequest + struct.pack('>Bx', min(len(addresses), kMaximumLocalAddressCount))
        first = True
        for address in addresses[:kMaximumLocalAddressCount]:
            if first:
                first = False
            else:
                data += kStartRecord
            data += socket.inet_aton(address) + kEndRecord
        data += b'\x00' * (kRequestPacketSize - len(data))
        sock.sendto(data, (broadcast, kRemotePort))
    time.sleep(kListenWait)
    listener.stop()
    header = kReportFormat.format('IP address', 'MAC address', 'Model No.', 'Description')
    print(header)
    print('=' * len(header))
    responses = listener.responses
    for addr in responses.keys():
        ip, mac, model, description = struct.unpack(kResponseFormat, responses[addr])
        ip = socket.inet_ntoa(ip)
        mac = ':'.join('{:02x}'.format(part) for part in mac)
        model = model.decode('utf-8', errors='replace')
        description = description.decode('utf-8', errors='replace')
        print(kReportFormat.format(ip, mac, model, description))
