apiminer
--------

.. image:: https://travis-ci.org/wcpannell/apiminer.svg?branch=master
    :target: https://travis-ci.org/wcpannell/apiminer
    :alt: Travis.ci

.. image:: https://cloud.drone.io/api/badges/wcpannell/apiminer/status.svg
    :target: https://cloud.drone.io/wcpannell/apiminer
    :alt: Drone.io

.. image:: https://codecov.io/github/wcpannell/apiminer/branch/master/graph/badge.svg
   :target: https://codecov.io/github/python-attrs/attrs
   :alt: Test Coverage

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/ambv/black
   :alt: Code style: black

apiminer is a Python package that handles communications with your miner APIs so you don't have to. Apiminer formats the output into a dictionary object for use in your reporting script. It can, optionally, automatically grab the latest status every time it is called.

Apiminer supports:
 * ClaymoreRPC
     - `Claymore <https://bitcointalk.org/index.php?topic=1433925>`_
     - `Ethminer <https://github.com/ethereum-mining/ethminer>`_
     - `PhoenixMiner <https://bitcointalk.org/index.php?topic=2647654>`_
 * `XMRStak <https://github.com/fireice-uk/xmr-stak/>`_
 * `CGMinerRPC <https://github.com/ckolivas/cgminer/blob/master/API-README>`_
     - `Team Red Miner <https://bitcointalk.org/index.php?topic=5059817>`_
     - `SGMiner <https://github.com/genesismining/sgminer-gm>`_ (Untested)
     - `CGMiner <https://github.com/ckolivas/cgminer/>`_ (Untested)
 * Others Coming Soon

Documentation
-------------
Mediocre documentation is available at https://wcpannell.github.io/apiminer/

Usage
-----
A trivial example::

        >>> import apiminer

        >>> claymore_miner_1 = apiminer.ClaymoreRPC("192.168.0.2", 8080)
        >>> print(claymore_miner_1.unified_data())
        {"coin": "ethash",
        "total hashrate": 75965000,
        "shares": {"accepted": 1452, "rejected": 28, "invalid": 0},
        "uptime": "23:33",
        "version": "PM 4.2c - ETH",
        "GPUs": {"GPU 0": {"temp": 63, "fan": 66, "hashrate": 30026000},
         "GPU 1": {"temp": 55, "fan": 33, "hashrate": 15326000},
         "GPU 2": {"temp": 52, "fan": 32, "hashrate": 15304000},
         "GPU 3": {"temp": 51, "fan": 31, "hashrate": 15308000}}}

        >>> teamredminer_1 = apiminer.TeamRedMiner("192.168.0.3", 8080)
        >>> TeamRedMiner_1.coin = "Monero"
        >>> print(teamredminer_1.unified_data())
        {"coin": "Monero",
        "total hashrate": 2224.0,
        "shares": {"accepted": 16057, "rejected": 2, "invalid": 1},
        "uptime": "132:42",
        "version": "TeamRedMiner 0.4.5",
        "GPUs": {"GPU 0": {"hashrate": 2224, "temp": 53, "fan": 79}}}

