import grpc
import os
from aiogrpc.channel import Channel
from aioetcd3.kv import KV
from aioetcd3.lease import Lease
from aioetcd3.auth import Auth
# from aioetcd3.watch import Watch
from aioetcd3.utils import get_secure_creds


class Client(KV, Lease, Auth):
    def __init__(self, endpoint, ssl=False,
                 ca_cert=None, cert_key=None, cert_cert=None,
                 default_ca=False, timeout=None):
        self.channel, self.credentials = self._create_grpc_channel(endpoint=endpoint, ssl=ssl,
                                                                   ca_cert=ca_cert,
                                                                   cert_key=cert_key, cert_cert=cert_cert,
                                                                   default_ca=default_ca)
        self.timeout = timeout
        super().__init__(self.channel, self.timeout)

    def update_server_list(self, endpoints):

        if self.credentials:
            self.channel = Channel(grpc.secure_channel(endpoints, self.credentials))
        else:
            self.channel = Channel(grpc.insecure_channel(endpoints))
        self._update_channel(self.channel)

    def _create_grpc_channel(self, endpoint, ssl=False,
                             ca_cert=None, cert_key=None, cert_cert=None, default_ca=False):
        credentials = None
        if not ssl:
            channel = grpc.insecure_channel(endpoint)
        else:
            if default_ca:
                ca_cert = None
            else:
                if ca_cert is None:
                    ca_cert = ''

            # to ensure ssl connect , set grpc env
            os.environ['GRPC_SSL_CIPHER_SUITES'] = 'ECDHE-ECDSA-AES256-GCM-SHA384'

            credentials = grpc.ssl_channel_credentials(ca_cert, cert_key, cert_cert)
            channel = grpc.secure_channel(endpoint, credentials)

        # use aiogrpc to decorate channel
        channel = Channel(channel)

        return channel, credentials


def client(endpoint, timeout=None):

    # user `ip:port,ip:port` to user grpc balance
    return Client(endpoint, timeout=timeout)


def ssl_client(endpoint, ca_file=None, cert_file=None, key_file=None, default_ca=False, timeout=None):
    ca, key, cert = get_secure_creds(ca_cert=ca_file, cert_cert=cert_file, cert_key=key_file)
    return Client(endpoint, ssl=True, ca_cert=ca, cert_key=key, cert_cert=cert,
                  default_ca=default_ca, timeout=timeout)

