#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с универсальными и вспомогательными классами и функциями
"""

import logging

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
