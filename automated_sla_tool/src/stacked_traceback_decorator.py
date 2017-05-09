import sys
import functools
from time import sleep


class MyError(Exception):
    pass


class StackedTracebackDecorator(object):
    def __init__(self, logger=None):
        self._logger = logger

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            try:
                fn(*args, **kwargs)
            except Exception as e:
                et, ei, tb = sys.exc_info()
                if self._logger:
                    self._logger.exception('Error Value: {e}\n'
                                           'Error Type: {et}\n'
                                           '{tb}'.format(e=e, et=et, tb=tb))
                    sleep(1)
                else:
                    raise MyError(e).with_traceback(tb)
        return decorated
