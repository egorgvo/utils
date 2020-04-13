from functools import wraps


def iterate_over(arg_name):
    """
    Decorator, run function for elements of iterable argument
    Декоратор, применяющий функцию к элементам итерируемого аргумента.
    :param arg_name: name of the function argument
    :type arg_name: str
    """
    def iterate_this(func):
        func.gw_method = func.__name__

        @wraps(func)
        def wrapper(*args, **kwargs):
            if arg_name in kwargs:
                iterable_arg = kwargs[arg_name]
                for item in iterable_arg:
                    kwargs[arg_name] = item
                    func(*args, **kwargs)
            else:
                index = func.__code__.co_varnames.index(arg_name)
                iterable_arg = args[index]
                for item in iterable_arg:
                    new_args = tuple([item if i == index else arg for i, arg in enumerate(args)])
                    func(*new_args, **kwargs)
        return wrapper
    return iterate_this


def try_again(exception, retry_attempts=1, raise_exc=True):
    """
    Use as decorator to exit process if
    function takes longer than s seconds
    """
    def outer(fn):
        fn.gw_method = fn.__name__

        @wraps(fn)
        def wrapper(*args, **kwargs):
            for i in range(retry_attempts + 1):
                try:
                    return fn(*args, **kwargs)
                except exception as exc:
                    if raise_exc and i == retry_attempts:
                        raise exc
                    continue
        return wrapper
    return outer
