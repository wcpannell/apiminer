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
    "1000;100;1",\
    "333;333;334",\
    "41;11; 51;21; 61;31",\
    "us1.ethermine.org:5551",\
    "11;22;33;44"\
]}""".encode(
    "utf-8"
)

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
    "42;12; 52;22; 62;32",\
    "us2.ethermine.org:5552",\
    "22;2;2;2"\
]}""".encode(
    "utf-8"
)

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
    "43;13; 53;23; 63;33",\
    "us3.ethermine.org:5553",\
    "33;3;3;3"\
]}""".encode(
    "utf-8"
)


@pytest.fixture
def response1_fixture(mocker):
    # mock has a bug in Python 2 causing failure when autospec is used on
    # socket.socket. https://github.com/testing-cabal/mock/issues/323
    m = mocker.patch("socket.socket").return_value
    m.recv.return_value = miner_response1
    m.connect.return_value = "CONNECTED"
    RPC = ClaymoreRPC("10.255.255.1", 8080)
    return RPC


# Deprecated
def test_raw_response1(response1_fixture):
    response1_fixture.update()
    assert (
        json.loads(miner_response1.decode("utf-8"))["result"]
        == response1_fixture._raw_response
    )


def test_version_response1(response1_fixture):
    response = response1_fixture.format_getstat1()
    assert "0.14.0" == response["miner"]["version"]


def test_address_response1(response1_fixture):
    response = response1_fixture.format_getstat1()
    assert response1_fixture.ip == response["miner"]["ip"]
    assert response1_fixture.port == response["miner"]["port"]


def test_runtime_response1(response1_fixture):
    response = response1_fixture.format_getstat1()
    assert (
        # int(json.loads(miner_response1.decode("utf-8"))["result"][1])
        "05:06"
        == response["miner"]["runtime"]
    )


def test_eth_pool_response1(response1_fixture):
    response = response1_fixture.format_getstat1()
    assert "us1.ethermine.org:5551" == response["eth_pool"]["pool"]
    assert 22 == response["eth_pool"]["pool_switches"]
    assert 174 == response["eth_pool"]["accepted"]
    assert 2 == response["eth_pool"]["rejected"]
    assert 11 == response["eth_pool"]["invalid"]
    assert 44414000 == response["eth_pool"]["total_hashrate"]


def test_dcr_pool_response1(response1_fixture):
    response = response1_fixture.format_getstat1()
    assert 44 == response["dcr_pool"]["pool_switches"]
    assert 100 == response["dcr_pool"]["accepted"]
    assert 1 == response["dcr_pool"]["rejected"]
    assert 33 == response["dcr_pool"]["invalid"]
    assert 1000000 == response["dcr_pool"]["total_hashrate"]


def test_format_gpus_response1(response1_fixture):
    response = response1_fixture.format_getstat1()
    assert response["GPUs"]["GPU 0"] == {
        "eth_hashrate": 14573000,
        "dcr_hashrate": 333000,
        "temp": 41,
        "fan": 11,
    }
    assert response["GPUs"]["GPU 1"] == {
        "eth_hashrate": 15036000,
        "dcr_hashrate": 333000,
        "temp": 51,
        "fan": 21,
    }
    assert response["GPUs"]["GPU 2"] == {
        "eth_hashrate": 14805000,
        "dcr_hashrate": 334000,
        "temp": 61,
        "fan": 31,
    }


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
