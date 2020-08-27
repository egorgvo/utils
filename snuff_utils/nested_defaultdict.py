#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Nested defaultdict implementation
"""

from collections import defaultdict


class NestedDefaultDict(defaultdict):

    def __init__(self, *args, **kwargs):
        super(NestedDefaultDict, self).__init__(NestedDefaultDict, *args, **kwargs)

    def __repr__(self):
        return repr(dict(self))
