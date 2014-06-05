import time

from tornado import gen
from preggy import expect

from tests.base import TestCase
from tornado_redis_sentinel import SentinelClient


class TestSentinelClient(TestCase):
    """ Test the client """

    def setUp(self):
        super(TestSentinelClient, self).setUp()
        self.client = SentinelClient(io_loop=self.io_loop)

    def connect(self, callback=None, client=None, on_disconnect=None):
        if callback is None:
            callback = self.stop
        if client is None:
            client = self.client

        client._disconnect_callback = on_disconnect

        # use two invalid ports and one valid port
        client.connect(
            sentinels=['127.0.0.1:2222', '127.0.0.1:2223', '127.0.0.1:57574', '127.0.0.1:2224'],
            master_name="master",
            callback=callback
        )

    def test_connect(self):
        result = {}

        def callback():
            result["connected"] = True
            expect(self.client.connection_status).to_equal("CONNECTED")
            self.stop()

        self.connect(callback)
        self.wait()  # blocks

        expect(result).to_include("connected")
        expect(result["connected"]).to_be_true()

    def test_connect_updates_sentinels(self):
        result = {}

        def callback():
            result["connected"] = True
            expect(self.client.connection_status).to_equal("CONNECTED")
            self.stop()

        self.connect(callback)
        self.wait()  # blocks

        expect(result).to_include("connected")
        expect(self.client.sentinels).to_length(5)
        expect(self.client.sentinels).to_include("127.0.0.1:57573")


    def test_connect_fails_when_no_available_sentinels(self):
        result = {}

        def callback():
            result["called"] = True
            expect(self.client.connection_status).to_equal("FAILED_AFTER_ALL_SENTINELS")
            self.stop()

        self.client.connect(
            sentinels=['127.0.0.1:2222', '127.0.0.1:2223', '127.0.0.1:2224'],
            master_name="master",
            callback=callback
        )
        self.wait()  # blocks

        expect(result).to_include("called")
        expect(result['called']).to_be_true()

    def test_connect_timeout(self):
        result = {}

        def callback():
            result["timeout"] = True
            expect(self.client.connection_status).to_equal("FAILED_AFTER_ALL_SENTINELS")
            self.stop()

        self.client.connect(
            sentinels=['127.0.0.1:57574'],
            master_name="master",
            callback=callback,
            timeout=-1
        )

        self.wait()  # blocks

        expect(result).to_include("timeout")
        expect(result["timeout"]).to_be_true()

    @gen.engine
    def test_set_command(self):
        result = {}

        def set_callback(response):
            result["set"] = response
            self.stop()

        self.connect(self.stop)
        self.wait()

        self.client.set("foo", "bar", callback=set_callback)
        self.wait()
        #blocks
        expect(result).to_include("set")
        expect(result["set"]).to_equal(b"OK")

        value = yield gen.Task(self.client.get, "foo")
        expect(value).to_equal("bar")

    @gen.engine
    def test_get_command(self):
        result = {}

        def get_callback(response):
            result['response'] = response
            self.stop()

        time_string = "%s" % time.time()

        self.connect(self.stop)
        self.wait()

        yield gen.Task(self.client.set, "foo", time_string)

        self.client.get("foo", callback=get_callback)
        self.wait()
        #blocks

        expect(result['response']).not_to_be_null()
        expect(result['response']).to_equal(time_string)

    def test_sub_command(self):
        client = SentinelClient(io_loop=self.io_loop)
        result = {"message_count": 0}
        conn = SentinelClient(io_loop=self.io_loop)

        self.connect(self.stop, client)
        self.connect(self.stop, conn)

        response = yield gen.Task(client.subscribe, "foobar")
        if response[0] == "subscribe":
            result["sub"] = response
            yield gen.Task(conn.publish, "foobar", "new message!")
        elif response[0] == "message":
            result["message_count"] += 1
            if result["message_count"] < 100:
                count = result["message_count"]
                value = yield gen.Task(conn.publish,
                                       "foobar", "new message %s!" % count)
            result["message"] = response[2]

        expect(result).to_include("sub")
        expect(result).to_include("message")
        expect(result["message"]).to_equal("new message 99!")

    def test_pub_command(self):
        result = {}

        def pub_callback(response):
            result["pub"] = response
            self.stop()

        self.connect(self.stop)
        self.wait()
        self.client.publish("foobar", "message", callback=pub_callback)
        self.wait()
        # blocks
        expect(result).to_include("pub")
        expect(result["pub"]).to_equal(0)  # no subscribers yet

    def test_blpop(self):
        result = {}

        def rpush_callback(response):
            result["push"] = response

            def blpop_callback(response):
                result["pop"] = response
                self.stop()

            self.client.blpop("test", 0, blpop_callback)

        self.connect()
        self.wait()

        self.client.rpush("test", "dummy", rpush_callback)
        self.wait()

        expect(result["pop"]).to_be_like([b"test", b"dummy"])

    def test_disconnect(self):
        self.connect()
        self.wait()

        self.client.close()
        with self.assertRaises(IOError):
            self.client._stream.read_bytes(1024, lambda x: x)

    def test_on_disconnect(self):
        result = {}

        def on_disconnect(*args, **kw):
            result['disconnected'] = True

        self.connect(on_disconnect=on_disconnect)
        self.wait()

        expect(result).to_include('disconnected')
        expect(result['disconnected']).to_be_true()

    def test_invalid_sentinels(self):
        cli = SentinelClient(io_loop=self.io_loop)

        with self.assertRaises(ValueError):
            cli.connect(sentinels=None)

        with self.assertRaises(ValueError):
            cli.connect(sentinels="invalid")

        with self.assertRaises(ValueError):
            cli.connect(sentinels=[])

    def test_invalid_master_name(self):
        cli = SentinelClient(io_loop=self.io_loop)

        with self.assertRaises(ValueError):
            cli.connect(sentinels=["localhost:2345"])

        with self.assertRaises(ValueError):
            cli.connect(sentinels=["localhost:2345"], master_name="")

        with self.assertRaises(ValueError):
            cli.connect(sentinels=["localhost:2345"], master_name=10)
