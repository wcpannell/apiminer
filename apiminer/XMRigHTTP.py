import requests
import typing


class XMRig:
    """Interacts with the XMRig HTTP JSON API

    Parameters
    ----------
    ip : str
        can be in the format of "192.168.0.1" or "192.168.0.1:8080" to include
        the port.
    port : int or None
        The port on which the api is listening. If None, the IP will be
        checked for a port callout (IP:PORT). Defaults to 80 if no port is
        assigned.
    token : str
        Access token for methods which require authorization
    """

    def __init__(
        self, ip: str, port: typing.Optional[int] = None, token: str = ""
    ) -> None:
        if port is None:
            if ":" in ip:
                split_ip = ip.split(":")
                self.port = split_ip[1]
                self.ip = split_ip[0]
            else:
                self.port = 80
                self.ip = ip
        else:
            self.ip = ip
            self.port = port

        self.token = token
        self._config = None

    @property
    def base_url(self):
        base = "http://" + self.ip + ":" + str(self.port)
        return base

    @property
    def headers(self):
        header = {"Content-Type": "application/json"}
        if self.token:
            header["Authorization"] = "Bearer {}".format(self.token)
        return header

    def summary(self):
        response = requests.get(
            self.base_url + "/1/summary", headers=self.headers
        )
        if response.status_code != 200:
            raise requests.RequestException(
                "Error. Status Code {}".format(response.status_code)
            )
        return response.json()

    def threads(self):
        response = requests.get(
            self.base_url + "/1/threads", headers=self.headers
        )
        if response.status_code != 200:
            raise requests.RequestException(
                "Error. Status Code {}".format(response.status_code)
            )
        return response.json()

    @property
    def config(self):
        if self.token is None:
            raise ValueError("config property requires token authorization")
        response = requests.get(
            self.base_url + "/1/config", headers=self.headers
        )
        if response.status_code != 200:
            raise requests.RequestException(
                "Error. Status Code {}".format(response.status_code)
            )
        else:
            self._config = response.json()
        return self._config

    @config.setter
    def config(self, **kwargs):
        if self.token is None:
            raise ValueError("config property requires token authorization")
        else:
            self._config.update(kwargs)
        response = requests.put(
            self.base_url + "/1/config",
            headers=self.headers,
            json=self._config,
        )

        if response.status_code != 200:
            raise requests.RequestException(
                "Error. Status Code {}".format(response.status_code)
            )

    def unified_data(self, *args, **kwargs):
        response = self.summary()
        unified_response = {
            "coin": response["algo"],
            "total hashrate": response["hashrate"]["total"][0],
            "shares": {
                "accepted": response["results"]["shares_good"],
                "rejected": response["results"]["shares_total"],
                "invalid": -1,
            },
            "uptime": response["uptime"] // 60,
            "version": response["version"],
            "GPUs": {},
        }

        for index, thread in enumerate(response["hashrate"]["threads"]):
            unified_response["GPUs"]["GPU {}".format(index)] = thread[0]

        return unified_response
