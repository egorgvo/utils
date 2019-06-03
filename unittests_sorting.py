#!/usr/bin/env python

"""Сортировка unit-тестов"""

from unittest import TestLoader


def get_loader_sorting_by_methods_order(cls):
    """
    Возвращает loader unittest, в котором реализована сортировка тестов в порядке их описания внутри класса.
    Usage:
        unittest.main(testLoader=get_loader_sorting_by_methods_order(YourTestClass))
    :param cls: класс, которому принадлежат методы
    :return: лямбда-функция сортировки методов тестов
    """
    loader = TestLoader()
    method_line_number = lambda method: getattr(cls, method).__code__.co_firstlineno
    loader.sortTestMethodsUsing = lambda a, b: method_line_number(a) - method_line_number(b)
    return loader
