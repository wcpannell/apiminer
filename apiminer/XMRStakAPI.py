#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
"""Reads data from the XMRStak JSON API"""

import requests


class XMRStakAPI(object):
    def __init__(self, ip, port):
        self.ip = ip

        self.port = port

        self.version = ""

        #: int: Uptime in minutes
        self.runtime = 0

        #: float: Current Total Hashrate. 10 second rolling average.
        self.total_hashrate = 0

        #: int: Total Accepted Shares
        self.accepted_shares = 0

        self.rejected_shares = 0

        #: list of float: Current Hashrate per card. 10s rolling average.
        self.percard_hashrate = [0]

        #: str: Pool with which the miner is currently connected
        self.pool = ""

        #: int: a copy of :attr:`XMRStak.rejected_shares`
        self.invalid_shares = 0

        self.update()

    def update(self):
        response = requests.get(
            "http://" + self.ip + ":" + str(self.port) + "/api.json"
        ).json()

        self.version = response["version"]

        self.runtime = int(response["connection"]["uptime"]) // 60

        self.total_hashrate = float(response["hashrate"]["total"][0])

        self.accepted_shares = int(response["results"]["shares_good"])

        self.rejected_shares = int(
            response["results"]["shares_total"]
            - response["results"]["shares_good"]
        )

        self.invalid_shares = self.rejected_shares

        self.percard_hashrate = [
            float(thread[0]) for thread in response["hashrate"]["threads"]
        ]

        self.pool = response["connection"]["pool"]

    def getdict(self, update=False):
        """Returns a dictionary of the class attributes, in a nice format"""
        if update:
            self.update()

        ourdict = {
            "miner": {
                "version": self.version,
                "ip": self.ip,
                "port": self.port,
                "runtime": self.runtime,
            },
            "cryptonight_pool": {
                "pool": self.pool,
                "accepted": self.accepted_shares,
                "rejected": self.rejected_shares,
                "invalid": self.invalid_shares,
                "total_hashrate": self.total_hashrate,
            },
            "GPUs": {},
        }
        for gpu in range(len(self.percard_hashrate)):
            ourdict["GPUs"]["GPU {}".format(gpu)] = {
                "hashrate": self.percard_hashrate[gpu]
            }
        return ourdict
