#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Module with dict common functions
"""

from copy import deepcopy


def dict_copy(some_dict, fields=None, deep=False):
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
    """
    if deep:
        result_dict = deepcopy(some_dict)
    elif not fields:
        result_dict = some_dict.copy()
    else:
        result_dict = some_dict
    if not fields:
        return result_dict

    if isinstance(fields, str):
        fields = fields.split(',')
    return {field: value for field, value in result_dict.items() if not fields or field in fields}


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
