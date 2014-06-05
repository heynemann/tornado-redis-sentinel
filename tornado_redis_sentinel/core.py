import sys
import logging
import socket
import errno
import six

from toredis.client import Client

from tornado_redis_sentinel.stream import DownStream


logger = logging.getLogger(__name__)


class SentinelClient(Client):
    def __init__(self, io_loop=None, disconnect_callback=None):
        super(SentinelClient, self).__init__(io_loop=io_loop)
        self._disconnect_callback = disconnect_callback

    def on_disconnect(self):
        if self._disconnect_callback is not None:
            self._disconnect_callback()

    def _connect(self, sock, addr, callback):
        self._reset()

        self._stream = DownStream(sock, io_loop=self._io_loop)
        self._stream.connect(addr, callback=callback, timeout=self.timeout)
        self._stream.read_until_close(self._on_close, self._on_read)

    def connect(self, sentinels=['localhost:6379'], master_name=None, callback=None, timeout=0.05):
        if not sentinels or not isinstance(sentinels, (list, tuple)):
            raise ValueError("sentinels must be a list with valid host:port values")

        if master_name is None or not master_name or not isinstance(master_name, six.string_types):
            raise ValueError("master_name argument must be a valid name")

        self.next_sentinel = 0
        self.timeout = timeout

        self.sentinels = sentinels
        self.master_name = master_name
        self._connect_callback = callback

        self.connect_to_next_sentinel()

    def connect_to_next_sentinel(self):
        if self.next_sentinel < len(self.sentinels):
            host, port = self.sentinels[self.next_sentinel].split(':')
            self.next_sentinel += 1
        else:
            if self._connect_callback:
                self.connection_status = "FAILED_AFTER_ALL_SENTINELS"
                self._connect_callback()
            self._connect_callback = None
            return

        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
            self._connect(sock, (host, int(port)), callback=self.handle_connection_to_sentinel)
        except socket.error:
            err = sys.exc_info()[1]
            if err.errno == errno.ECONNREFUSED:
                logger.warn("Error connecting to %s:%d (%s)... Trying next sentinel." % (host, int(port), err))
                #self.connect_to_next_sentinel()
            else:
                raise

    def handle_connection_to_sentinel(self, *args, **kw):
        if not args[0]:
            self.connect_to_next_sentinel()
            return

        self.update_sentinels()

    def update_sentinels(self):
        self.send_message([
            'sentinel',
            'sentinels',
            self.master_name
        ], self.handle_get_all_sentinels)

    def handle_get_all_sentinels(self, *args, **kw):
        # each sentinel is a tuple with the values below
        # 'name', '10.10.10.10:26379', 'ip', '10.10.10.10', 'port', '26379', 'runid', '7ae5839dec4ce7685b7db89d365e01b0b1dba28f', 'flags', 'sentinel', 'pending-commands', '0', 'last-ping-sent', '0', 'last-ok-ping-reply', '341', 'last-ping-reply', '341', 'down-after-milliseconds', '5000', 'last-hello-message', '300', 'voted-leader', '?', 'voted-leader-epoch', '0'
        sentinels = args[0]

        if sentinels is not None:
            for sentinel in sentinels:
                name = sentinel[1]
                if name not in self.sentinels:
                    self.sentinels.append(name)
            self.next_sentinel = 0

        self.send_message([
            'sentinel',
            'get-master-addr-by-name',
            self.master_name
        ], self.handle_get_master_address)

    def handle_get_master_address(self, *args, **kw):
        if args[0] is None or args[0] == '-IDONTKNOW':
            self.connect_to_next_sentinel()
            return

        master_host, master_port = args[0]
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
        self._connect(sock, (master_host, int(master_port)), self.handle_connection_success)

    def handle_connection_success(self, *args, **kw):
        if self._connect_callback:
            self.connection_status = "CONNECTED"
            self._connect_callback()
        self._connect_callback = None
