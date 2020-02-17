#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с универсальными и вспомогательными классами и функциями
"""

import logging
from itertools import chain

import six

logger = logging.getLogger()


def default(value, default=None, empties=None):
    """
    Если значение не заполнено, возвращает значение по умолчанию.
    :param value: Исходное значение
    :param default: Значение по умолчанию
    :param empties: Список значений, которые необходимо воспринимать как пустые
    :type empties: list
    :return: Исходное значение, либо значение по умолчанию
    >>> default('2', '3')
    '2'
    >>> default('')

    >>> default('', '3')
    '3'
    >>> default('', '3', empties=[None])
    ''
    >>> default(None, '3', empties=[None])
    '3'
    """
    if empties and value in empties:
        return default
    elif not empties and not value:
        return default
    return value


def join_nonempty(iterable, binder=', '):
    """
    Работает аналогично join, но объединяет только непустые значения
    :param iterable: Итерируемый объект
    :param binder: Связующее звено
    :return: Строка
    """
    return binder.join(filter(None, iterable))


def str_to_list(variable, sep=','):
    return variable.split(sep) if isinstance(variable, six.string_types) else variable


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
