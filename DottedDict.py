#!/usr/bin/env python2.7
# -*- encoding: utf-8 -*-

"""
Модуль, описывающий класс DottedDict, позволяющий вызывать ключи словаря через точку
"""


class DottedDict(dict):
    """
    Use instances of this class for using dict with dot:
    >> d = {'a': 'test'}
    >> d.a
    'test'
    """
    def __getattr__(self, key):
        return self[key]

    def __setattr__(self, key, value):
        self[key] = value
