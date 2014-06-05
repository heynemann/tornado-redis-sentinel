import sys

__version__ = '0.1.0'

try:
    from tornado_redis_sentinel.core import SentinelClient  # NOQA
except ImportError:
    err = sys.exc_info()[1]
    print ("Import error, probably setup.py working its magic! %s" % err)
