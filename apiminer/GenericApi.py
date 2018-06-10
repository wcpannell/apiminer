#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generic API Interface"""

import json


class MinerApi(object):
    """Generic API Class inherited by the protocol implementations

    Parameters
    ----------
    ip : str
        IP address of the api host
    port : int
        The port on which the api is listening

    Attributes
    ----------
    auto_update : bool
        Enable to update every time the response attribute is read.
    """
    def __init__(self, ip, port, auto_update=False):
        self.ip = str(ip).encode('utf-8')
        self.port = int(port)
        self.auto_update = auto_update
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
        """dict: Private storage of response.

        Read-only storage of formatted response. set by
        :meth:`MinerApi.update`.
        """

    @property
    def response(self):
        """Returns a dictionary of the response.

        Read-only storage of formatted response. set by
        :meth:`MinerApi.update`. If auto_update is enabled, accessing the
        attribute will call :meth:`MinerApi.update` and return the formatted
        response
        """
        if self.auto_update:
            self._raw_response, self._response = self.update("Update Please")

        return self._response

    def update(self, write_message):
        """Update the model with fresh data.

        This method automates calling the write, read, and formatter methods.

        Parameters
        ----------
            write_message : str
                Whatever message is required to get the desired response from
                your API

        Returns
        -------
        tuple
            + string
                The raw response from the API
            + dict
                The standardized response dict generated from the raw response
        """
        self.write(write_message)
        raw_response = self.read()
        formatted_response = self.format(raw_response)
        return (raw_response, formatted_response)

    def write(self, message):
        """This is just a dummy in the generic class.

        Overwrite this method with the implementation specific method.

        Parameters
        ----------
        message: str
            Your message
        """
        pass

    def read(self):
        """This is just a dummy in the generic class.

        Overwrite this method with the implementation specific method.

        Returns
        -------
        str
            This is just a serialized version of self._response
        """
        return json.dumps(self._response)

    def format(self, message):
        """This is just a dummy in the generic class.

        Overwrite this method with the implementation specific method.
        Formats the miner response into our standardized dictionary.

        Parameters
        ----------
        message : str
            Input message

        Attributes
        ----------
        dict
            Formatted version of message
        """
        json.loads(message)
