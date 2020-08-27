#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Module with dict common functions
"""

from copy import deepcopy


def dict_invert(some_dict):
    """
    >>> a = {'a': 1, 'b': 2, 'c': 3}
    >>> dict_invert(a)
    {1: 'a', 2: 'b', 3: 'c'}
    """
    return {v: k for k, v in some_dict.items()}


def dict_copy(some_dict, fields=None, deep=False, **kwargs):
    """
    >>> a = {'a': 1, 'b': 2, 'c': 3}
    >>> dict_copy(a, 'a')
    {'a': 1}
    >>> dict_copy(a, 'a,b')
    {'a': 1, 'b': 2}
    >>> dict_copy(a, ['a'])
    {'a': 1}
    >>> dict_copy(a, ['a', 'b'])
    {'a': 1, 'b': 2}
    >>> dict_copy(a)
    {'a': 1, 'b': 2, 'c': 3}
    >>> dict_copy(a, d='c')
    {'d': 3}
    >>> dict_copy(a, '*', d='c')
    {'a': 1, 'b': 2, 'd': 3}
    >>> dict_copy(a, 'b', d='c')
    {'b': 2, 'd': 3}
    """
    if deep:
        result_dict = deepcopy(some_dict)
    elif not fields and not kwargs:
        result_dict = some_dict.copy()
    else:
        result_dict = some_dict
    if not fields and not kwargs:
        return result_dict

    if not fields:
        fields = []
    elif fields == "*":
        fields = set(result_dict)
        fields -= set(kwargs)
    elif isinstance(fields, str):
        fields = fields.split(',')
    if kwargs:
        kwargs = dict_invert(kwargs)
        return {
            kwargs[field] if field in kwargs else field: value
            for field, value in result_dict.items()
            if field in fields or field in kwargs
        }
    else:
        return {field: value for field, value in result_dict.items() if field in fields}


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
