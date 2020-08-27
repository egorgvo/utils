#!/usr/bin/env python3
# coding=utf-8

"""Модуль для функций обработки списка словарей"""

from copy import deepcopy
from operator import eq, ne, contains

try:
    from .universal import str_to_list
except:
    from snuff_utils.universal import str_to_list


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

    >>> next(find_dict_in_list([{'a': 1}], a=1), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], a__ne=0), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], a__ne=1), None)

    >>> next(find_dict_in_list([{'a': 1}], b__ne=1), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], b__eq=1), None)
    >>> next(find_dict_in_list([{'a': 1}], a__type=int), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], a__type=str), None)
    >>> next(find_dict_in_list([{'a': 1}], a__type=(str, int)), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], __type=dict), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], __type=list), None)
    >>> next(find_dict_in_list([1], __ne=1), None)
    >>> next(find_dict_in_list([{'a': 1}], __ne=1), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], a__in=[2, 4]), None)

    >>> next(find_dict_in_list([{'a': 1}], a__in=[2, 1, 4]), None)
    {'a': 1}
    >>> next(find_dict_in_list([{'a': 1}], a__nin=[2, 1, 4]), None)

    >>> next(find_dict_in_list([{'a': 1}], a__nin=[2, 4]), None)
    {'a': 1}
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
    by_fields = str_to_list(by_fields)

    if not all(field in values_dict for field in by_fields):
        return

    def field_exists(obj, field):
        exists = hasattr(obj, field)
        if exists:
            return True
        try:
            return field in obj
        except Exception as exc:
            return False

    def get_value(obj, field):
        return obj[field] if isinstance(obj, dict) else getattr(obj, field)

    operators_map = {
        '__eq': eq,
        '__ne': ne,
        '__type': isinstance,
        '__in': lambda x, y: contains(y, x),
        '__nin': lambda x, y: not contains(y, x),
    }
    operators_allow_nonexistence = [ne]

    any_matches = False
    for _dict in list_of_dicts:
        for field in by_fields:
            is_obj_check = False
            target_field = field
            for ending, operator in operators_map.items():
                if not field.endswith(ending):
                    continue
                field = field[:-len(ending)]
                is_obj_check = not bool(field)
                break
            else:
                operator = eq

            # Получаем сравниваемые значения
            target_value = get_value(values_dict, target_field)

            if is_obj_check:
                if operator(_dict, target_value):
                    continue
                break

            # Проверяем, что поле существует внутри объекта
            exists = field_exists(_dict, field)
            # для некоторых операторов допустимо отсутствие поля
            if not exists and operator in operators_allow_nonexistence:
                continue
            # строгое существование, остальные поля можно не проверять
            elif not exists:
                break

            value = get_value(_dict, field)
            # Сравниваем значения
            if operator(value, target_value):
                continue
            # Иначе объект не подходит фильтру
            break
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
    [{'a': 1, 'b': 2, 'c': 5}, {'a': 1, 'b': 3, 'c': 5}, {'a': 1, 'b': 2, 'c': 6}]
    >>> group_list_of_dicts(source_list, 'a,b,c', 'c')
    [{'a': 1, 'b': 2, 'c': 10}, {'a': 1, 'b': 3, 'c': 5}, {'a': 1, 'b': 2, 'c': 6}]
    >>> group_list_of_dicts(source_list, 'a,b')
    [{'a': 1, 'b': 2}, {'a': 1, 'b': 3}]
    >>> group_list_of_dicts(source_list, 'a,b', 'c')
    [{'a': 1, 'b': 2, 'c': 16}, {'a': 1, 'b': 3, 'c': 5}]
    >>> group_list_of_dicts(source_list, 'a', 'b,c')
    [{'a': 1, 'b': 9, 'c': 21}]
    >>> group_list_of_dicts(source_list, 'a,d', 'b,c')
    [{'a': 1, 'b': 9, 'c': 21}]
    >>> group_list_of_dicts(source_list, 'a,d,c', 'b,c')
    [{'a': 1, 'c': 15, 'b': 7}, {'a': 1, 'c': 6, 'b': 2}]
    >>> source_list[-1]['d'] = 1
    >>> group_list_of_dicts(source_list, 'a,d', 'b,c')
    [{'a': 1, 'b': 7, 'c': 16}, {'a': 1, 'd': 1, 'b': 2, 'c': 5}]

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
