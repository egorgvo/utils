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


def sort_list_of_dicts(lst, keys, reverse=False, default=None, **convert):
    """
    Sort list of dicts by fields names. Allowed multiple fields names.
    :param lst: list of dicts
    :param keys: fields names as sorting keys
    :param reverse: reverse sorting flag
    :param default: default value for non existent fields. May be specified as dict {'field': 'default_value'} format
    :param convert: dict of conversion (before comparison) rules
    :return: sorted list of dicts

    >>> lst = [{'order': 3, 'value': 3}, {'order': 1, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(lst, 'order,value')
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 1}, {'order': 3, 'value': 3}]
    >>> sort_list_of_dicts(lst, ('order', 'value'))
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 1}, {'order': 3, 'value': 3}]
    >>> sort_list_of_dicts(lst, 'order')
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(lst, '-order,value')
    [{'order': 3, 'value': 1}, {'order': 3, 'value': 3}, {'order': 1, 'value': 3}]
    >>> sort_list_of_dicts(lst, 'order,-value')
    [{'order': 1, 'value': 3}, {'order': 3, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(lst, '-order,-value')
    [{'order': 3, 'value': 3}, {'order': 3, 'value': 1}, {'order': 1, 'value': 3}]
    >>> sort_list_of_dicts(lst, '-value,-order')
    [{'order': 3, 'value': 3}, {'order': 1, 'value': 3}, {'order': 3, 'value': 1}]
    >>> sort_list_of_dicts(lst, '-value,-order', reverse=True)
    [{'order': 3, 'value': 1}, {'order': 1, 'value': 3}, {'order': 3, 'value': 3}]
    >>> sort_list_of_dicts(lst, 'order', reverse=True)
    [{'order': 3, 'value': 3}, {'order': 3, 'value': 1}, {'order': 1, 'value': 3}]
    >>> sort_list_of_dicts(lst, ('-order', 'value'))
    [{'order': 3, 'value': 1}, {'order': 3, 'value': 3}, {'order': 1, 'value': 3}]
    >>> lst = [{}, {'1': 'tpue'}, {'1': 'true'}]
    >>> sort_list_of_dicts(lst, '1', default={'1': 'z'})
    [{'1': 'tpue'}, {'1': 'true'}, {}]
    >>> sort_list_of_dicts(lst, '1', default='')
    [{}, {'1': 'tpue'}, {'1': 'true'}]
    >>> lst = [{'k1': 'weg'}, {'k1': 'lfe'}, {'k1': 'aqd'}, {'k1': 'Asd'}, {'k1': 'JKd'}, {'k1': 'Ukz'}]
    >>> sort_list_of_dicts(lst, 'k1')
    [{'k1': 'Asd'}, {'k1': 'JKd'}, {'k1': 'Ukz'}, {'k1': 'aqd'}, {'k1': 'lfe'}, {'k1': 'weg'}]
    >>> sort_list_of_dicts(lst, 'k1', k1=str.lower)
    [{'k1': 'aqd'}, {'k1': 'Asd'}, {'k1': 'JKd'}, {'k1': 'lfe'}, {'k1': 'Ukz'}, {'k1': 'weg'}]
    """
    keys = keys.split(',') if isinstance(keys, str) else keys
    keys_list = []
    for key in keys:
        field, direction = (key[1:], -1) if isinstance(key, str) and key.startswith('-') else (key, 1)
        keys_list.append(dict(direction=direction, field=field))

    def key(x):
        result = []
        for k in keys_list:
            field = k['field']
            k_default = default.get(field) if isinstance(default, dict) else default
            value = x.get(field, k_default)
            if field in convert:
                value = convert[field](value)
            result.append(k['direction'] * value)
        return result

    return sorted(lst, key=key, reverse=reverse)


def column_sum(data, column_name):
    """
    Получает сумму по индексу по всем строкам итерируемого объекта
    :param data: Итерируемый объект
    :param column_name: Индекс или наименование колонки
    :return: Сумма
    """
    return sum(row[column_name] if column_name in row else 0 for row in data)


def group_list_of_dicts(_source_list, by_fields='', sum_fields=''):
    """
    Группирует список словарей по полям выборки

    >>> source_list = [{'a': 1, 'b': 2, 'c': 5}, {'a': 1, 'b': 3, 'c': 5}, {'a': 1, 'b': 2, 'c': 6}, {'a': 1, 'b': 2, 'c': 5}]
    >>> group_list_of_dicts(source_list, 'a,b,c')
    [{'a': 1, 'c': 5, 'b': 2}, {'a': 1, 'c': 5, 'b': 3}, {'a': 1, 'c': 6, 'b': 2}]
    >>> group_list_of_dicts(source_list, 'a,b,c', 'c')
    [{'a': 1, 'c': 10, 'b': 2}, {'a': 1, 'c': 5, 'b': 3}, {'a': 1, 'c': 6, 'b': 2}]
    >>> group_list_of_dicts(source_list, 'a,b')
    [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}]
    >>> group_list_of_dicts(source_list, 'a,b', 'c')
    [{'a': 1, 'c': 16, 'b': 2}, {'a': 1, 'c': 5, 'b': 3}]
    >>> group_list_of_dicts(source_list, 'a', 'b,c')
    [{'a': 1, 'c': 21, 'b': 9}]
    >>> group_list_of_dicts(source_list, 'a,d', 'b,c')
    [{'a': 1, 'c': 21, 'b': 9}]
    >>> group_list_of_dicts(source_list, 'a,d,c', 'b,c')
    [{'a': 1, 'c': 15, 'b': 7}, {'a': 1, 'c': 6, 'b': 2}]
    >>> source_list[-1]['d'] = 1
    >>> group_list_of_dicts(source_list, 'a,d', 'b,c')
    [{'a': 1, 'c': 16, 'b': 7}, {'a': 1, 'c': 5, 'b': 2, 'd': 1}]

    :param _source_list: Исходный список словарей
    :param by_fields: Поля выборки
    :type by_fields: Список, либо строка ключей через запятые
    :param sum_fields: Поля, которые суммируются при группировке
    :type sum_fields: Список, либо строка ключей через запятые
    :return: Список словарей
    """
    if isinstance(by_fields, str):
        by_fields = by_fields.split(',')
        if '' in by_fields: by_fields.remove('')
    if not by_fields: return _source_list
    if isinstance(sum_fields, str):
        sum_fields = sum_fields.split(',')
        if '' in sum_fields: sum_fields.remove('')

    # Собираем словари в группы по полям выборки
    # В итоге получим список списков схоих по полям выборки словарей
    source_list = deepcopy(_source_list)
    assistive_list = []
    while source_list:
        base_dict = source_list[0]
        matches = [
            match_dict for match_dict in source_list
            if all([match_dict.get(key, None) == base_dict.get(key, None) for key in by_fields])
        ]
        assistive_list.append(matches)
        for match_dict in matches:
            if not match_dict in source_list: continue
            source_list.remove(match_dict)

    # Формируем итоговый список словарей
    result = []
    for group_list in assistive_list:
        # Берем все поля выборки как основу словаря
        cur_row = {
            field: group_list[0][field] for field in by_fields
            if field in group_list[0]
        }
        # Суммируем поля, указанные в sum_fields
        for field in sum_fields:
            cur_row[field] = column_sum(group_list, field)
        result.append(cur_row)
    return result


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
