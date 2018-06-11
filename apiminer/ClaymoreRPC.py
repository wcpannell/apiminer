#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Implementation of ClaymoreRPC get_minerstats1 protocol

This is compatable with both Claymore and Ethminer
"""
from __future__ import (absolute_import, division, print_function,
                        unicode_literals)
from builtins import * # noqa 401,403
import socket
import json


class ClaymoreRPC(object):
    """Class that interacts with a ClaymoreRPC protocol listener

    Parameters
    ----------
    ip : str
        IP address of the api host
    port : int
        The port on which the api is listening

    Attributes
    ----------
    response : dict
        Private storage of formatted response. set by
        :meth:`ClaymoreRPC.update`
    """
    def __init__(self, ip, port):
        self.ip = str(ip).encode('utf-8')

        self.port = int(port)

        #: bool: Set by :meth:`ClaymoreRPC._connect`
        self._connected = False

        #: :obj:`socket.socket` Object. This communicates with the API Host
        self.socket = None

        #: bool: Enable to update every time the response attribute is read.
        self.auto_update = False

        self._response = {
            'miner': {
                'version': '',
                'ip': '',
                'port': 0,
                'runtime': 0
            },
            'eth_pool': {
                'pool': '',
                'pool_switches': 0,
                'accepted': 0,
                'rejected': 0,
                'invalid': 0,
                'total_hashrate': 0
            },
            'dcr_pool': {
                'pool': 'Not Implemented',
                'pool_switches': 0,
                'accepted': 0,
                'rejected': 0,
                'invalid': 0,
                'total_hashrate': 0
            },
            'GPUs': {
                'GPU 0': {
                    'eth_hashrate': 0,
                    'total_dcr_hashrate': 0,
                    'temp': 0,
                    'fan': 0
                }
            }
        }
        """dict: Private storage of formatted response. set by
        :meth:`ClaymoreRPC.update`"""

        # Get Data right off the bat. Could be dangerous? I'm open to changing.
        self.update()

    def _connect(self):
        """Connects to our API Host"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self._connected = True

    def _disconnect(self):
        """Disconnects from our API Host"""
        self.socket.close()
        self._connected = False

    def update(self):
        """Update our model with fresh data. Connects if not connected"""
        if not self._connected:
            self._connect()
        self.socket.sendall(
            (
                json.dumps(
                    {
                        "id": 0,
                        "jsonrpc": "2.0",
                        "method": "miner_getstat1"
                    }
                )
                + '\n'
            ).encode('utf-8')
        )
        try:
            received = self.socket.recv(1024)
        except ConnectionResetError:
            received = None
            self._disconnect()
            pass

        if received:
            self._raw_response = json.loads(received.decode('utf-8'))['result']
        else:
            print('invalid JSON RPC response')

        # Close the socket when we're not using it.
        # Let me know if this isn't a good idea
        self._disconnect()
        return self._raw_response

    def restart_miner(self):
        """Sends the miner (API Host) the restart command.
        The miner API must be set in write mode. No effort is made to check if
        the restart was successful. Also, note that if the miner is
        non-responsive, it is very unlikely that this command will be
        effective.
        """
        if not self._connected:
            self._connect()
        self.socket.sendall(
            (
                json.dumps(
                    {
                        "id": 0,
                        "jsonrpc": "2.0",
                        "method": "miner_restart"
                    }
                )
                + '\n'
            ).encode('utf-8')
        )
        self._disconnect()

    def _format_response(self):
        self._response['miner']['version'] = \
                self._raw_response[0]
        self._response['miner']['runtime'] = \
            int(self._raw_response[1])

        [
            self._response['eth_pool']['total_hashrate'],
            self._response['eth_pool']['accepted'],
            self._response['eth_pool']['rejected']
        ] = [int(val) for val in self._raw_response[2].split(';')]
        if self._response['eth_pool']['total_hashrate'] > 0:
            self._response['eth_pool']['total_hashrate'] /= 1000

        [
            self._response['dcr_pool']['total_hashrate'],
            self._response['dcr_pool']['accepted'],
            self._response['dcr_pool']['rejected'],
        ] = [
            int(val) if val != 'off' else -1
            for val in self._raw_response[4].split(';')
        ]
        if self._response['dcr_pool']['total_hashrate'] > 0:
            self._response['dcr_pool']['total_hashrate'] /= 1000

        self._response['eth_pool']['pool'] = self._raw_response[7]

        [
            self._response['eth_pool']['invalid'],
            self._response['eth_pool']['pool_switches'],
            self._response['dcr_pool']['invalid'],
            self._response['dcr_pool']['pool_switches']
        ] = [
            int(val) if val != 'off' else -1
            for val in self._raw_response[8].split(';')
        ]

        percard_eth_hashrate = [
            (int(val) / 1000) for val in self._raw_response[3].split(';')
        ]

        percard_dcr_hashrate = [
            (float(val) / 1000) if val != 'off' else -1
            for val in self._raw_response[5].split(';')
        ]

        tempsfans = self._raw_response[6].split(';')
        tempsfans = [
            [int(value), int(tempsfans[index+1])]
            for index, value in enumerate(tempsfans)
            if not index % 2
        ]

        for gpu in range(len(percard_eth_hashrate)):
            self._response['GPUs']['GPU {}'.format(gpu)] = {
                'eth_hashrate': percard_eth_hashrate[gpu],
                'dcr_hashrate': percard_dcr_hashrate[gpu],
                'temp': tempsfans[gpu][0],
                'fan': tempsfans[gpu][1]
            }
        self._response['miner']['ip'] = self.ip
        self._response['miner']['port'] = self.port

    @property
    def response(self):
        """Returns a dictionary of the response, in a nice format"""
        if self.auto_update:
            self.update()

        self._format_response()
        return self._response
