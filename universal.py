#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с универсальными и вспомогательными классами и функциями
"""

import logging
from itertools import chain

logger = logging.getLogger()


def join_nonempty(iterable, binder=', '):
    """
    Работает аналогично join, но объединяет только непустые значения
    :param iterable: Итерируемый объект
    :param binder: Связующее звено
    :return: Строка
    """
    return binder.join(filter(None, iterable))


def str_to_list(variable, sep=','):
    return variable.split(sep) if isinstance(variable, str) else variable


def float_truncate(value, after_dot=0):
    """
    >>> v = -1.454645646400000000000000000000000000000000000001
    >>> [float_truncate(v, n) for n in range(5)]
    [-1.0, -1.4, -1.45, -1.454, -1.4546]
    """
    return float(int(value * 10 ** after_dot)) / 10 ** after_dot


def list_of_lists_unwind(some_list, iterator=False):
    """
    Unwind list of lists
    >>> a = [[1, 2], [3, 4], [5]]
    >>> list_of_lists_unwind(a)
    [1, 2, 3, 4, 5]
    >>> it = list_of_lists_unwind(a, iterator=True)
    >>> assert '<itertools.chain' in str(it)
    >>> list(it)
    [1, 2, 3, 4, 5]
    """
    result = chain(*some_list)
    if iterator:
        return result
    return list(result)


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
