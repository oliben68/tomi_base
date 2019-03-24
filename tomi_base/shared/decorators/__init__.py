import functools


def before(*methods):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for method in methods:
                method(*args, **kwargs)
            return func(*args, **kwargs)

        return wrapper

    return decorator


def after(*methods):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return_value = func(*args, **kwargs)
            for method in methods:
                method(*args, **kwargs)
            return return_value

        return wrapper

    return decorator
