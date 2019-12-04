#!/usr/bin/env python3
# coding=utf-8

"""Модуль для функций обработки списка словарей"""

from copy import deepcopy
from collections import Iterable
from operator import itemgetter


def find_dict_in_list(list_of_dicts, values_dict=None, by_fields='',
                      default='$nodefaultvalue$', **kwargs):
    """
    Итератор, ищет словарь в списке словарей.
    :param list_of_dicts: Список словарей
    :param values_dict: Словарь, по которому нужно искать соответствие
    :param by_fields: По каким ключам словаря values_dict нужно искать соответствие.
    Если не задано, то по всем.
    :param default: Значение, которое возвращать, если совпадений не было
    :param kwargs: Именованные аргументы, которыми обновится словарь values_dict.
    Если values_dict не задан kwargs берутся в качестве values_dict.
    :return: Найденное совпадение (словарь или другой объект), либо default, если задано. Иначе ошибка итерации.
    """
    values_dict = deepcopy(values_dict)
    if not values_dict:
        values_dict = {}

    if kwargs and isinstance(values_dict, dict):
        values_dict.update(kwargs)
    elif kwargs:
        for field, value in kwargs.items():
            values_dict[field] = value

    if not by_fields:
        by_fields = values_dict.keys()

    by_fields = by_fields.split(',') \
        if isinstance(by_fields, str) else by_fields

    if not all(field in values_dict for field in by_fields): return

    any_matches = False
    for _dict in list_of_dicts:
        for field in by_fields:
            targer_field_name = field
            not_eq = field.endswith('__ne')
            if not_eq:
                field = field[:-4]
                # может отсутствовать, проверяем остальные поля
                if field not in _dict: continue
            # строгое существование, остальные поля можно не проверять
            elif field not in _dict: break

            # Сравниваемые значения
            targer_value = values_dict[targer_field_name] if isinstance(values_dict, dict) \
                else getattr(values_dict, targer_field_name)
            value = _dict[field] if isinstance(_dict, dict) else getattr(_dict, field)

            # Соответствие значению
            if not_eq:
                # Не должно быть равно
                if targer_value == value: break
            # Должно быть равно
            elif targer_value != value: break
        else:
            # совпадение - словарь
            yield _dict
            any_matches = True

    # Если нет совпадений и задано значение по умолчанию
    if not any_matches and default != '$nodefaultvalue$':
        yield default


def sort_list_of_dicts(lst, keys, reverse=False):
    """
    Сортирует список словарей по ключам словаря.
    В качестве ключей сортировки можно подавать несколько ключей словаря.
    :param lst: Список словарей
    :param keys: Ключи словаря
    :return: Отсортированный по правилу сортировки список словарей

    >>> some_list = [{'order': 3, 'value': 3}, {'order': 1, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(some_list, 'order,value')
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 1}, {'order': 3, 'value': 3}]
    >>> sort_list_of_dicts(some_list, ('order', 'value'))
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 1}, {'order': 3, 'value': 3}]
    >>> sort_list_of_dicts(some_list, 'order')
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(some_list, '-order,value')
    [{'order': 3, 'value': 1}, {'order': 3, 'value': 3}, {'order': 1, 'value': 3}]
    >>> sort_list_of_dicts(some_list, 'order,-value')
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(some_list, '-order,-value')
    [{'order': 3, 'value': 3}, {'order': 3, 'value': 1}, {'order': 1, 'value': 3}]
    >>> sort_list_of_dicts(some_list, '-value,-order')
    [{'order': 3, 'value': 3}, {'order': 1, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(some_list, '-value,-order', reverse=True)
    [{'order': 3, 'value': 1}, {'order': 1, 'value': 3}, {'order': 3, 'value': 3}]
    >>> sort_list_of_dicts(some_list, 'order', reverse=True)
    [{'order': 3, 'value': 3}, {'order': 3, 'value': 1}, {'order': 1, 'value': 3}]
    >>> sort_list_of_dicts(some_list, ('-order', 'value'))
    [{'order': 3, 'value': 1}, {'order': 3, 'value': 3}, {'order': 1, 'value': 3}]
    """
    keys = keys.split(',') if isinstance(keys, str) else keys
    keys_list = []
    for key in keys:
        field, direction = (key[1:], -1) if key.startswith('-') else (key, 1)
        keys_list.append(dict(direction=direction, field=field))

    return sorted(lst, key=lambda x: [k['direction'] * x[k['field']] for k in keys_list], reverse=reverse)


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
