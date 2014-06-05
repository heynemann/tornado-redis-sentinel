from datetime import timedelta

from tornado.iostream import IOStream
from tornado import concurrent


class DownStream(IOStream):
    '''
    Stream that errors when connection errors occur.
    Retrieved from https://groups.google.com/forum/#!topic/python-tornado/WUJtP31I36U
    '''

    @concurrent.return_future
    def connect(self, address, callback=None, server_hostname=None, timeout=None):
        """ Extended version of iostream.IOStream.connect handling timeouts and errors
        WARNING: this function overrides set_close_callback callback

        @param timeout:     connection timeout in seconds
        @return:            future
        """
        def handle_timeout():
            """ Connection timed out """
            self.set_close_callback(None)
            self.close()
            self.error = "timeout"
            callback(False)

        def handle_error():
            """ Connection error, stream is closed """
            if timeout:
                self.io_loop.remove_timeout(timeout_handle)
            callback(False)

        def handle_connected():
            """ Connection is established """
            self.set_close_callback(None)
            if timeout:
                self.io_loop.remove_timeout(timeout_handle)
            callback(True)

        if timeout:
            timeout_handle = self.io_loop.add_timeout(timedelta(seconds=timeout), handle_timeout)

        self.set_close_callback(handle_error)
        super(DownStream, self).connect(address, callback=handle_connected, server_hostname=server_hostname)
