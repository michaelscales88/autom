import functools


class TypeDecorator(object):
    def __init__(self, argument, a_idx=0):
        self.arg_type = argument
        self.i_arg = a_idx

    def __call__(self, fn):
        @functools.wraps(fn)
        def decorated(*args, **kwargs):
            # TODO should be able to handle multiple types and multiple variables
            if isinstance(args[self.i_arg], self.arg_type):
                fn(*args, **kwargs)
            else:
                print('{0} is not a {1}.'.format(args[self.i_arg], self.arg_type))
            # if all(x in [args, kwargs] for x in self.arg_type):
            #     fn(*args, **kwargs)
            # else:
            #     print('{0} is not a {1}.'.format(args[self.i_arg], self.arg_type))
        return decorated

