import functools


class FinishedDecorator(object):
    def __init__(self, finished):
        self.finished = finished

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            if self.finished:
                pass
            else:
                fn(*args, **kwargs)
        return decorated
