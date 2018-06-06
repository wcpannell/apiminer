#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
""""""

import unittest
from unittest.mock import patch
import apiminer


class TestClaymoreRPC(unittest.TestCase):
    """"""
    def test(self):
        with patch('apiminer.ClaymoreRPC.socket') as mocked_socket:
            test_response = [
                '0.14.0',
                '306',
                '44414;174;2',
                '14573;15036;14805',
                '0;0;0',
                'off;off;off',
                '54;33; 58;35; 57;35',
                'us2.ethermine.org:5555',
                '0;0;0;0'
            ]
            mocked_socket.return_value.recv = test_response
            RPC = apiminer.ClaymoreRPC('example.com', 80)
            self.assertSetEqual(RPC._raw_response, test_response)


if __name__ == '__main__':
    unittest.main()
