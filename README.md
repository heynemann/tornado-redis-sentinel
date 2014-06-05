tornado-redis-sentinel
======================

tornado-redis-sentinel is a library for connecting with redis asynchronously, while enjoying the benefits of the [toredis](https://github.com/mrjoes/toredis) library.

Implementing Sentinel Support
-----------------------------

tornado-redis-sentinel follows the guidelines in the [redis documentation](http://redis.io/topics/sentinel-clients) for implementing sentinel clients.

The only addition to that specification is that tornado-redis-sentinel will try to automatically discover other available sentinels for you.

Installing
----------

Installing tornado-redis-sentinel is as easy as:

    $ pip install tornado-redis-sentinel

Usage
-----

Using tornado-redis-sentinel is exactly the same as using toredis. The only difference is when connecting to it:

```python
from tornado_redis_sentinel import SentinelClient

# then when initializing tornado
# get ioloop from tornado
client = SentinelClient(io_loop=tornado_io_loop)
client.connect(
    sentinels=[
        "first-sentinel.myhost.com:7777",
        "second-sentinel.myhost.com:7778"
    ], master_name="my-master-name",
    callback=self.on_connected
)

def on_connected(self, status):
    # if connection was successful, status will be "CONNECTED"
    # otherwise it will be "FAILED_AFTER_ALL_SENTINELS"

    # do something with connection
```

Automatic Reconnection
----------------------

While tornado-redis-sentinel does not support automatic reconnection, it allows you to be notified when redis gets disconnected using the `disconnect_callback` argument to SentinelClient.

```python
from tornado_redis_sentinel import SentinelClient

# then when initializing tornado
# get ioloop from tornado
self.client = SentinelClient(io_loop=tornado_io_loop, disconnect_callback=self.on_disconnect)
self.client.connect(
    sentinels=[
        "first-sentinel.myhost.com:7777",
        "second-sentinel.myhost.com:7778"
    ], master_name="my-master-name",
    callback=self.on_connected
)

def on_disconnect(self, status):
    # reconnect?
    self.client.connect(
        sentinels=[
            "first-sentinel.myhost.com:7777",
            "second-sentinel.myhost.com:7778"
        ], master_name="my-master-name",
        callback=self.on_connected
    )
```

License
-------

tornado-redis-sentinel is MIT licensed:

    The MIT License (MIT)

    Copyright (c) 2014 Globo.com<timehome@corp.globo.com>

    Permission is hereby granted, free of charge, to any person obtaining a copy
    of this software and associated documentation files (the "Software"), to deal
    in the Software without restriction, including without limitation the rights
    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
    copies of the Software, and to permit persons to whom the Software is
    furnished to do so, subject to the following conditions:

    The above copyright notice and this permission notice shall be included in
    all copies or substantial portions of the Software.

    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
    THE SOFTWARE.

Contributing
------------

Fork, Code, Test, Pull-Request.

Rinse and repeat.
