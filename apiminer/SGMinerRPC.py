#!/usr/bin/env python3

# from __future__ import (
#     absolute_import,
#     division,
#     print_function,
#     unicode_literals,
# )
# from builtins import *
import socket
import json
import datetime


class _SGBase(object):
    """Class that interacts with SGMiner JSON-RPC compatible API"""

    def __init__(self, ip: str, port: int):
        self.ip = str(ip).encode("utf-8")
        self.port = int(port)

        self.socket = None
        self._connected = False
        self.VERBOSE = False
        self.coin = "Unknown"

    def _connect(self):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.settimeout(3)
        self.socket.connect((self.ip, self.port))
        self._connected = True

    def _disconnect(self):
        self.socket.close()
        self._connected = False

    def _write(self, method="summary", parameter=None):
        query = {"command": method}
        if parameter:
            query["parameter"] = parameter

        if not self._connected:
            self._connect()

        self.socket.sendall((json.dumps(query) + "\n").encode("utf-8"))

    def _read(self):
        """Read API response"""

        try:
            received = self.socket.recv(4096)
        except ConnectionResetError:
            received = None
            self._disconnect()
            pass

        self._disconnect()

        if received:
            message = json.loads(received.decode("utf-8"))
            status = self._decode_status(message)
            status_code = status["STATUS"]
            if (status_code is "E") or (status_code is "F"):
                raise ValueError(
                    status["Msg"] + ". Message Dump:\n" + str(message)
                )
            elif status_code is "S":
                if self.VERBOSE:
                    print(status)
                return message
            else:
                print("Unusual Status Flag Received.")
                print(status)
                return message
        else:
            print("invalid JSON RPC response")
            return {"results": "INVALID"}

    def _decode_status(self, message):
        status = message["STATUS"][0]
        status["When"] = datetime.datetime.fromtimestamp(
            status["When"]
        ).strftime("%c")
        return status

    def version(self):
        self._write("version")
        message = self._read()
        return message["VERSION"][0]

    def config(self):
        self._write("config")
        message = self._read()
        return message["CONFIG"][0]

    def summary(self):
        self._write("summary")
        message = self._read()
        return message["SUMMARY"][0]

    def devs(self):
        self._write("devs")
        message = self._read()
        return message["DEVS"]

    def gpu(self, number: int):
        self._write("gpu", parameter=number)
        message = self._read()
        return message["GPU"]

    def gpucount(self) -> int:
        self._write("gpucount")
        message = self._read()
        return message["GPUS"][0]["Count"]

    def unified_data(self, return_dual_mining=False):
        """@TODO: Fix GPUs"""
        message = self.summary()
        devs = self.devs()

        uptime_hours = message["Elapsed"] // 3600
        uptime_minutes = (message["Elapsed"] // 60) % 60

        unified_response = {
            "coin": self.coin,
            "total hashrate": message["KHS av"] * 1000,
            "shares": {
                "accepted": message["Accepted"],
                "rejected": message["Rejected"],
                "invalid": message["Discarded"] + message["Stale"],
            },
            "uptime": "{:02d}:{:02d}".format(uptime_hours, uptime_minutes),
            "version": self.version()["Miner"],
            "GPUs": self.devs(),
        }

        unified_response["GPUs"] = {}

        for dev in devs:
            unified_response["GPUs"]["GPU {}".format(dev["GPU"])] = {
                "hashrate": int(dev["KHS av"] * 1000),
                "temp": int(dev["Temperature"]),
                "fan": int(dev["Fan Percent"]),
            }

        return unified_response


class SGMiner(_SGBase):
    def __init__(self, ip: str, port: int):
        super().__init__(ip, port)

    def pgacount(self) -> int:
        self._write("pgacount")
        message = self._read()
        return message["PGAS"][0]["Count"]

    def pga(self, number: int):
        self._write("pga", parameter=number)
        message = self._read()
        return message["PGA"]


TeamRedMiner = _SGBase
