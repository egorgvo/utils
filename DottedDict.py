#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Class DottedDict allows you to call dict keys with the dot.
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
