#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
""""""

import unittest
# import socket
import json
from unittest.mock import patch
from apiminer.ClaymoreRPC import ClaymoreRPC


class TestClaymoreRPC(unittest.TestCase):
    """"""
    def setUp(self):
        print('Setting up')
    # def testlive(self):
        # print(self.ClaymoreRPC.response)

    def test_raw_response1(self):
        miner_response = """{\
            "id": 0,\
            "jsonrpc": "2.0",\
            "result": [\
            "0.14.0",\
            "306",\
            "44414;174;2",\
            "14573;15036;14805",\
            "0;0;0",\
            "off;off;off",\
            "54;33; 58;35; 57;35",\
            "us1.ethermine.org:5551",\
            "0;0;0;0"\
        ]}""".encode('utf-8')

        with patch('socket.socket') as mocked_socket:
            mocked_socket.return_value.recv.return_value = \
                miner_response
            RPC = ClaymoreRPC('example.com', 80)
            raw_response = RPC._raw_response
            response = RPC.response

            self.assertEqual(
                raw_response,
                json.loads(
                    miner_response.decode('utf-8')
                )['result']
            )

    def test_raw_response2(self):
        #: bytestring: This JSONRPC response has DCR
        miner_response = """{\
            "id": 0,\
            "jsonrpc": "2.0",\
            "result": [\
            "11.14.2",\
            "200",\
            "444142;172;2",\
            "14572;15032;14802",\
            "2000;200;2",\
            "666;666;667",\
            "52;32; 62;42; 72;42",\
            "us2.ethermine.org:5552",\
            "22;2;2;2"\
        ]}""".encode('utf-8')

        with patch('socket.socket') as mocked_socket:
            mocked_socket.return_value.recv.return_value = \
                miner_response
            RPC = ClaymoreRPC('example.com', 80)
            RPC.update()
            raw_response = RPC._raw_response
            response = RPC.response

            self.assertEqual(
                raw_response,
                json.loads(
                    miner_response.decode('utf-8')
                )['result']
            )

    def test_raw_response3(self):
        self.miner_response3 = """{\
            "id": 0,\
            "jsonrpc": "2.0",\
            "result": [\
            "11.14.3",\
            "300",\
            "444143;173;3",\
            "14573;15033;14803",\
            "3000;300;3",\
            "1000;1000;1000",\
            "53;33; 63;43; 73;53",\
            "us3.ethermine.org:5553",\
            "33;3;3;3"\
        ]}""".encode('utf-8')

        with patch('socket.socket') as mocked_socket:
            mocked_socket.return_value.recv.return_value = \
                self.miner_response3
            RPC = ClaymoreRPC('example.com', 80)
            RPC.auto_update = True
            self.response3 = RPC.response
            self.raw_response3 = RPC._raw_response
            self.assertEqual(
                self.raw_response3,
                json.loads(
                    self.miner_response3.decode('utf-8')
                )['result']
            )


if __name__ == '__main__':
    unittest.main()
