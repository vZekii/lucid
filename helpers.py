import functools


def debug(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = ["{0}={1!r}".format(k, v) for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print("Calling {0}({1})".format(func.__name__, signature))
        value = func(*args, **kwargs)
        print("{0!r} returned {1!r}".format(func.__name__, value))
        return value
    return wrapper
