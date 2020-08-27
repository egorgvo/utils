#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Module with file common functions
"""

import os.path


def file_exists(filename):
    return os.path.exists(filename) and os.path.isfile(filename)


def dir_exists(dirpath):
    return os.path.exists(dirpath) and os.path.isdir(dirpath)
