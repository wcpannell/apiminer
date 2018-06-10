#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
""""""
import pytest
import json
from apiminer.ClaymoreRPC import ClaymoreRPC


miner_response1 = """{\
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

miner_response2 = """{\
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

miner_response3 = """{\
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


@pytest.fixture
def response1_fixture(mocker):
    # mock has a bug in Python 2 causing failure when autospec is used on
    # socket.socket. https://github.com/testing-cabal/mock/issues/323
    m = mocker.patch("socket.socket").return_value
    m.recv.return_value = miner_response1
    m.connect.return_value = 'CONNECTED'
    RPC = ClaymoreRPC('10.255.255.1', 8080)
    return RPC


def test_raw_response1(response1_fixture):
    assert json.loads(miner_response1.decode('utf-8'))['result'] == \
        response1_fixture._raw_response


def test_version_response1(response1_fixture):
    assert json.loads(miner_response1.decode('utf-8'))['result'][0] == \
        response1_fixture.response['miner']['version']


def test_runtime_response1(response1_fixture):
    assert int(
        json.loads(
            miner_response1.decode('utf-8')
        )['result'][1]
    ) == response1_fixture.response['miner']['runtime']
#     def test_raw_response2(self):
#         #: bytestring: This JSONRPC response has DCR
#         miner_response = """{\
#             "id": 0,\
#             "jsonrpc": "2.0",\
#             "result": [\
#             "11.14.2",\
#             "200",\
#             "444142;172;2",\
#             "14572;15032;14802",\
#             "2000;200;2",\
#             "666;666;667",\
#             "52;32; 62;42; 72;42",\
#             "us2.ethermine.org:5552",\
#             "22;2;2;2"\
#         ]}""".encode('utf-8')
#
#         with patch('socket.socket') as mocked_socket:
#             mocked_socket.return_value.recv.return_value = \
#                 miner_response
#             RPC = ClaymoreRPC('example.com', 80)
#             RPC.update()
#             raw_response = RPC._raw_response
#             response = RPC.response
#
#             self.assertEqual(
#                 raw_response,
#                 json.loads(
#                     miner_response.decode('utf-8')
#                 )['result']
#             )
#
#     def test_raw_response3(self):
#         self.miner_response3 = """{\
#             "id": 0,\
#             "jsonrpc": "2.0",\
#             "result": [\
#             "11.14.3",\
#             "300",\
#             "444143;173;3",\
#             "14573;15033;14803",\
#             "3000;300;3",\
#             "1000;1000;1000",\
#             "53;33; 63;43; 73;53",\
#             "us3.ethermine.org:5553",\
#             "33;3;3;3"\
#         ]}""".encode('utf-8')
#
#         with patch('socket.socket') as mocked_socket:
#             mocked_socket.return_value.recv.return_value = \
#                 self.miner_response3
#             RPC = ClaymoreRPC('example.com', 80)
#             RPC.auto_update = True
#             self.response3 = RPC.response
#             self.raw_response3 = RPC._raw_response
#             self.assertEqual(
#                 self.raw_response3,
#                 json.loads(
#                     self.miner_response3.decode('utf-8')
#                 )['result']
#             )
