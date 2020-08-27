#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с вспомогательными функциями-итераторами
"""

from collections.abc import Iterable

from itertools import chain, islice


def is_iterable(obj):
    return isinstance(obj, Iterable)


def iterable(obj):
    if is_iterable(obj):
        return obj
    return [obj]


def iterate_over_hierarchy(value, hierarchy, hierarchy_separator='.', ignore_nonexistent=True):
    """
    Функция позволяет получать значения дочерних элементов объекта, используя условное обозначение иерархии.
    Если среди дочерних объектов попадется список и в hierarchy указан индекс для этого списка,
    то будет выбран соответствующий элемент списка.
    Если среди дочерних объектов попадаются списки и индекс не указан, то итератор проходит по всем элементам списка.

    :param value: Объект с дочерними элементами
    :param hierarchy: Иерархия полей объекта
    :type hierarchy: Список или строка
    :param hierarchy_separator: Разделитель строки
    :param ignore_nonexistent: Флаг, игнорировать отсутствие полей (ничего не возвращать)
    :return: Итератор по значениям нижнего уровня иерархии
    >>> a = {'a': {'f': [{'f': [{'g': {'s': 3}}, {'g': [{'s': 5}, {'b': 3, 's': 89}]}]}]}}
    >>> list(iterate_over_hierarchy(a, 'a.f.f.0.g.s'))
    [3]
    >>> a = {'a': {'f': [{'f': [{'g': {'s': 3}}, {'g': [{'s': 5}, {'b': 3, 's': 89}]}]}]}}
    >>> list(iterate_over_hierarchy(a, 'a.f.f.g.s'))
    [3, 5, 89]
    """
    def has_attr(obj, attr):
        if not obj:
            return False
        try:
            return attr in obj
        except:
            return hasattr(obj, attr)

    # Предварительное преобразование списка полей иерархии в список
    if not isinstance(hierarchy, list):
        hierarchy = hierarchy.split(hierarchy_separator)

    for i, field in enumerate(hierarchy):
        # Получение элемента списка по индексу
        if isinstance(value, list) and field.isdigit():
            field = int(field)
            # Если индекс больше длины списка
            if field >= len(value):
                if ignore_nonexistent: break
                yield None
                break

        # Цикл по списку
        elif isinstance(value, list):
            for item in value:
                for result in iterate_over_hierarchy(item, hierarchy[i:], hierarchy_separator, ignore_nonexistent):
                    yield result
            break

        # Если поле отсутствует
        elif not has_attr(value, field):
            if ignore_nonexistent: break
            yield None
            break

        # Ступаем на уровень ниже
        try:
            value = value[field]
        except:
            value = getattr(value, field)

        # Обработка последнего уровня иерерахии
        if i + 1 == len(hierarchy):
            yield value
            break


def safe_get(obj, hierarchy, default=None, hierarchy_separator='.'):
    return next(iterate_over_hierarchy(obj, hierarchy, hierarchy_separator=hierarchy_separator), default)


def chunks(iterable, n):
    """Yield n-sized iterators from iterable.
    Use map(list, chunks(...)) for list chunks."""
    iterator = iter(iterable)
    while True:
        yield chain((next(iterator),), islice(iterator, n-1))


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
