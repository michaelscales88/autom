from dateutil.parser import parse
from traceback import format_exc
from functools import wraps
from datetime import datetime
from json import JSONEncoder


def valid_dt(date_string):
    validated_dt = None
    try:
        validated_dt = parse(date_string, ignoretz=True)
    except ValueError:
        pass
    return validated_dt


def call_back_handler(fn, exceptions, handler, *args, **kwargs):
    try:
        return fn(*args, **kwargs)
    except exceptions:
        handler(fn)
        return fn(*args, **kwargs)
    except Exception:
        print(format_exc())


clasgit s DateTimeEncoder(JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        return super(DateTimeEncoder, self).default(o)

# class MyError(Exception):
#     pass
#
#
# class StackedTracebackDecorator(object):
#     def __init__(self, logger=None):
#         self._logger = logger
#
#     def __call__(self, fn):
#         @wraps(fn)
#         def decorated(*args, **kwargs):
#             try:
#                 fn(*args, **kwargs)
#             except Exception as e:
#                 et, ei, tb = sys.exc_info()
#                 if self._logger:
#                     self._logger.exception('Error Value: {e}\n'
#                                            'Error Type: {et}\n'
#                                            '{tb}'.format(e=e, et=et, tb=tb))
#                     # sleep(1)
#                 else:
#                     raise MyError(e).with_traceback(tb)
#         return decorated
