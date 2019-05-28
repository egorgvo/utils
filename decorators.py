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
