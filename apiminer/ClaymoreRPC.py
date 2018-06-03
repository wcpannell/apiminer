#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Implementation of ClaymoreRPC get_minerstats1 protocol

This is compatable with both Claymore and Ethminer
"""

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

    """
    def __init__(self, ip, port):
        self.ip = str(ip).encode('utf-8')

        self.port = int(port)

        #: bool: Set by :meth:`ClaymoreRPC._connect`
        self.connected = False

        #: str: Miner Version
        self.version = ''

        #: int: Miner Runtime
        self.runtime = 0

        #: int: Miner Total Hashrate
        self.total_hashrate = 0

        #: int: Number of accepted shares
        self.accepted_shares = 0

        #: int: Number of rejected shares
        self.rejected_shares = 0

        #: list of int: Hashrate per GPU
        self.percard_hashrate = [0, ]

        #: int: Total Decred Hashrate. Not used in Ethminer
        self.total_dcr_hashrate = 0

        #: int: Decred Accepted Shares. Not used in Ethminer
        self.dcr_accepted_shares = 0

        #: int: Decred Rejected Shares. Not used in Ethminer
        self.dcr_rejected_shares = 0

        #: list of int: Decred hashrate for each GPU. Not used in Ethminer
        self.percard_dcr_hashrate = [0, ]

        #: list of list of int: [[Temp1, Fan%1], ..., [TempN, Fan%N]]
        self.tempsfans = [[0, 0], ]

        #: str: Currently Connected Pool. ex. 'pool.pool.com:8080'
        self.pool = ''

        #: int: total invalid shares
        self.invalid_shares = 0

        #: int: Number of times the pool has switched
        self.pool_switches = 0

        #: Decred Invalid Shares. Not used in Ethminer
        self.dcr_invalid_shares = 0

        #: Decred Pool switches. Not used in Ethminer
        self.dcr_pool_switches = 0

        #: :class:`socket.socket` Object. This communicates with the API Host
        self.socket = None

        # Get Data right off the bat. Could be dangerous? I'm open to changing.
        self.update()

    def _connect(self):
        """Connects to our API Host"""
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.ip, self.port))
        self.connected = True

    def _disconnect(self):
        """Disconnects from our API Host"""
        self.socket.close()
        self.connected = False

    def update(self):
        """Update our model with fresh data. Connects if not connected"""
        if not self.connected:
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
            response = json.loads(received.decode('utf-8'))['result']

            self.version = response[0]

            self.runtime = int(response[1])

            [
                self.total_hashrate,
                self.accepted_shares,
                self.rejected_shares
            ] = [int(val) for val in response[2].split(';')]
            if self.total_hashrate > 0:
                self.total_hashrate /= 1000

            self.percard_hashrate = [
                (int(val) / 1000) for val in response[3].split(';')
            ]

            [
                self.total_dcr_hashrate,
                self.dcr_accepted_shares,
                self.dcr_rejected_shares,
            ] = [
                int(val) if val != 'off' else -1
                for val in response[4].split(';')
            ]
            if self.total_dcr_hashrate > 0:
                self.total_dcr_hashrate /= 1000

            self.percard_dcr_hashrate = [
                (float(val) / 1000) if val != 'off' else -1
                for val in response[5].split(';')
            ]

            tempsfans = response[6].split(';')
            self.tempsfans = [
                [int(value), int(tempsfans[index+1])]
                for index, value in enumerate(tempsfans)
                if not index % 2
            ]

            self.pool = response[7]

            [
                self.invalid_shares,
                self.pool_switches,
                self.dcr_invalid_shares,
                self.dcr_pool_switches
            ] = [
                int(val) if val != 'off' else -1
                for val in response[8].split(';')
            ]

        else:
            print('invalid JSON RPC response')

        # Close the socket when we're not using it.
        # Let me know if this isn't a good idea
        self._disconnect()

    def restart_miner(self):
        """Sends the miner (API Host) the restart command.
        The miner API must be set in write mode. No effort is made to check if
        the restart was successful. Also, note that if the miner is
        non-responsive, it is very unlikely that this command will be
        effective.
        """
        if not self.connected:
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

    def getdict(self, update=False):
        """Returns a dictionary of all the objects, in a nice format"""
        if update:
            self.update()

        ourdict = {
            'miner': {
                'version': self.version,
                'ip': self.ip,
                'port': self.port,
                'runtime': self.runtime
            },
            'eth_pool': {
                'pool': self.pool,
                'pool_switches': self.pool_switches,
                'accepted': self.accepted_shares,
                'rejected': self.rejected_shares,
                'invalid': self.invalid_shares,
                'total_hashrate': self.total_hashrate
            },
            'dcr_pool': {
                'pool': 'Not Implemented',
                'pool_switches': self.dcr_pool_switches,
                'accepted': self.dcr_accepted_shares,
                'rejected': self.dcr_rejected_shares,
                'invalid': self.dcr_invalid_shares,
                'total_hashrate': self.total_dcr_hashrate
            },
            'GPUs': {}
        }
        for gpu in range(len(self.percard_hashrate)):
            ourdict['GPUs']['GPU {}'.format(gpu)] = {
                'eth_hashrate': self.percard_hashrate[gpu],
                'total_dcr_hashrate': self.percard_dcr_hashrate[gpu],
                'temp': self.tempsfans[gpu][0],
                'fan': self.tempsfans[gpu][1]
            }
        return ourdict
