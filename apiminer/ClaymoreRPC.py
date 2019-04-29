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

        self.authorized = None

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

    def write(self, method="miner_getstats1", password=None):
        """Send message to the miner. Connects if not connected

        Parameters
        ----------
        method: str
            Query the API for the data indicated. See [Ethminer
            Docs](https://github.com/ethereum-mining/ethminer/blob/master/docs/API_DOCUMENTATION.md)
            for more information on the methods that can be used
        password: str
            Password for APIs protected by --api-password. Note that this
            password is sent in cleartext. Blame ethminer.
        """
        query = {
            "id": 0,
            "jsonrpc": "2.0",
            "method": method
        }

        if password is not None:
            query['params'] = {"psw": password}

        if not self._connected:
            self._connect()
        self.socket.sendall(
            (
                json.dumps(query)
                + '\n'
            ).encode('utf-8')
        )

    def read(self):
        """Read data from API

        Returns
        -------
        dict
            deserialized JSON response.
        """
        try:
            received = self.socket.recv(1024)
        except ConnectionResetError:
            received = None
            self._disconnect()
            pass

        # Close the socket when we're not using it.
        # Let me know if this isn't a good idea
        self._disconnect()

        if received:
            return json.loads(received.decode('utf-8'))
        else:
            print('invalid JSON RPC response')

    def update(self):
        """DEPRECATION WARNING. This will be removed in the next release"""
        print("DEPRECATION WARNING. This will be removed in the next release")
        self.write("miner_getstat1")
        self._raw_response = self.read()['result']

    def authorize(self, password):
        """Authenticate connection. Used for APIs that have --api-password set.

        This will send the password in plaintext. Blame Ethminer

        Parameters
        ----------
        password: str
            The password. Again, cleartext.
        """
        self.write(method="api_authorize", password=password)
        response = self.read()
        if response['result']:
            self.authorized = True
        else:
            self.authorized = False

    def getstat1(self):
        """Implementation of the getstats1 method."""
        self.write("getstat1")
        raw_response = self.read()['result']
        response = dict()

        response['miner']['version'] = raw_response[0]
        response['miner']['runtime'] = int(raw_response[1])

        [
            response['eth_pool']['total_hashrate'],
            response['eth_pool']['accepted'],
            response['eth_pool']['rejected']
        ] = [int(val) for val in raw_response[2].split(';')]
        if response['eth_pool']['total_hashrate'] > 0:
            response['eth_pool']['total_hashrate'] /= 1000

        [
            response['dcr_pool']['total_hashrate'],
            response['dcr_pool']['accepted'],
            response['dcr_pool']['rejected'],
        ] = [
            int(val) if val != 'off' else -1
            for val in raw_response[4].split(';')
        ]
        if response['dcr_pool']['total_hashrate'] > 0:
            response['dcr_pool']['total_hashrate'] /= 1000

        response['eth_pool']['pool'] = raw_response[7]

        [
            response['eth_pool']['invalid'],
            response['eth_pool']['pool_switches'],
            response['dcr_pool']['invalid'],
            response['dcr_pool']['pool_switches']
        ] = [
            int(val) if val != 'off' else -1
            for val in raw_response[8].split(';')
        ]

        percard_eth_hashrate = [
            (int(val) / 1000) for val in raw_response[3].split(';')
        ]

        percard_dcr_hashrate = [
            (float(val) / 1000) if val != 'off' else -1
            for val in raw_response[5].split(';')
        ]

        tempsfans = raw_response[6].split(';')
        tempsfans = [
            [int(value), int(tempsfans[index+1])]
            for index, value in enumerate(tempsfans)
            if not index % 2
        ]

        for gpu in range(len(percard_eth_hashrate)):
            response['GPUs']['GPU {}'.format(gpu)] = {
                'eth_hashrate': percard_eth_hashrate[gpu],
                'dcr_hashrate': percard_dcr_hashrate[gpu],
                'temp': tempsfans[gpu][0],
                'fan': tempsfans[gpu][1]
            }
        response['miner']['ip'] = self.ip
        response['miner']['port'] = self.port

        return response

    def restart_miner(self):
        """Deprecated. Renamed to restart.

        This will be removed in the next version"""
        self.restart()

    def restart(self):
        """Sends the miner (API Host) the restart command.

        The miner API must be set in write mode. Also, note that if the miner
        is non-responsive, it is very unlikely that this command will be
        effective. If effective, this will cause the miner to stop mining,
        unload DAGs, reset GPUs, regenerate DAGs, and then start mining. The
        connection to the pool will be maintained.

        Returns
        -------
        bool
            Restart succesful.
        """
        self.write("miner_restart")
        response = self.read()

        if response:
            return True
        else:
            return False

    def reboot(self):
        """Runs a script named reboot.sh (Linux) or reboot.bat (Windows)

        This method will only work if the API is in write mode. There is no
        guarantee that script will succeed.

        Returns
        -------
        bool
            Returns True if script was found and the miner tried to start it.
        """
        self.write("miner_reboot")
        response = self.read()

        if response:
            return True
        else:
            return False

    def _format_response(self):
        """DEPRECATED WARNING. This will be removed in the next release"""
        print(
            "DEPRECATION WARNING. This will be removed in the next release\n",
            "Formatting will now be a part of each API method implementation"
        )

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
        """Deprecated.
Returns a dictionary of the response, in a nice format"""
        if self.auto_update:
            self.update()

        self._format_response()
        return self._response

class EthminerRPC(ClaymoreRPC):
    """Class that uses the Ethminer superset of ClaymoreRPC protocol listener
    to interact with an Ethminer client.

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
        super().__init__(ip, port):

    def getstatdetail(self):
        """Returns dict of detailed statistical data

        Returns
        -------
        dict
            API response
        """
        self.write("miner_getstatdetail")
        return self.read()

    def ping(self):
        """Check if the server is still alive
        Returns
        -------
        bool
            Response received.
        """
        self.write("miner_ping")
        response = self.read()
        if response:
            return True
        else:
            return False

    def getstathr(self):
        """Ethminer's noncompliant, but much better formatted extension to
        getstat1

        Returns
        -------
        dict
            Response
        """
        self.write("miner_getstathr")
        return self.read()
