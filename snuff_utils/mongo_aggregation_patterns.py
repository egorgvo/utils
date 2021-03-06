#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Module is deprecated. Use https://github.com/egorgvo/mongo_aggregation instead.
"""

from copy import deepcopy


def field_is_specified(field):
    return {'$cond': [field, True, False]}


def project_set_value(expression):
    #TODO переделать на $literal если получится
    return {'$cond': [True, expression, '']}


def roundHalfUp(expression, signs_after_dot=0):
    abs_expression = {'$abs': expression}
    sign = {'$cond': [{'$gt': [expression, 0]}, 1, -1]}
    if signs_after_dot:
        rounded_abs = {'$divide': [
            {'$trunc': {'$add': [{'$multiply': [abs_expression, pow(10, signs_after_dot)]}, 0.5]}},
            pow(10, signs_after_dot)
        ]}
    else:
        rounded_abs = {'$trunc': {'$add': [abs_expression, 0.5]}}
    return {'$multiply': [rounded_abs, sign]}


def day_start(field):
    field = dollar_prefix(field)
    return {'$subtract': [
        field,
        {'$add': [
            {'$multiply': [{'$hour': field}, 3600000]},
            {'$multiply': [{'$minute': field}, 60000]},
            {'$multiply': [{'$second': field}, 1000]},
            {'$millisecond': field}
        ]}
    ]}


def month_start(field):
    field = dollar_prefix(field)
    return {'$subtract': [
        field,
        {'$add': [
            {'$multiply': [{'$subtract': [{'$dayOfMonth': field}, 1]}, 86400000]},
            {'$multiply': [{'$hour': field}, 3600000]},
            {'$multiply': [{'$minute': field}, 60000]},
            {'$multiply': [{'$second': field}, 1000]},
            {'$millisecond': field}
        ]}
    ]}


def lookup_unwind(collection, local_field='_id', as_field='', foreign_field='_id', preserveNullAndEmptyArrays=True):
    if not as_field:
        as_field = local_field
    pipeline = [
        lookup(collection, local_field, as_field, foreign_field),
        unwind(as_field, preserveNullAndEmptyArrays)
    ]
    return pipeline


def lookup(collection, local_field='_id', as_field='', foreign_field='_id'):
    if not as_field:
        as_field = local_field
    return {"$lookup": {
        'from': collection,
        'foreignField': foreign_field,
        'localField': local_field,
        'as': as_field,
    }}


def unwind(field, preserveNullAndEmptyArrays=False):
    field = dollar_prefix(field)
    if preserveNullAndEmptyArrays:
        return {'$unwind': {'path': field, 'preserveNullAndEmptyArrays': True}}
    else:
        return {'$unwind': field}


def dollar_prefix(field):
    return field if field.startswith('$') else '${}'.format(field)


def _list_dollar_prefix(*args):
    args = list(args)
    for i, arg in enumerate(args):
        if not isinstance(arg, str):
            continue
        args[i] = dollar_prefix(arg)
    return args


def pop_dollar_prefix(field):
    return field[1:] if field.startswith('$') else field


def date_to_string(field, date_format="%Y-%m-%d %H:%M:%S:%L"):
    field = dollar_prefix(field)
    return {'$dateToString': {'format': date_format, 'date': field}}


def set_value(expression):
    return {'$literal': expression}


def hide_fields(fields_to_hide, visible_fields, concealer_field='_id'):
    if isinstance(fields_to_hide, str):
        fields_to_hide = fields_to_hide.split(',')
    if isinstance(visible_fields, str):
        visible_fields = visible_fields.split(',')

    projection = {
        concealer_field: {field: dollar_prefix(field) for field in fields_to_hide},
    }
    projection[concealer_field][concealer_field] = dollar_prefix(concealer_field)
    projection.update({field: 1 for field in visible_fields})
    return {'$project': projection}


def unhide_fields(hided_fields, visible_fields, concealer_field='_id'):
    if isinstance(hided_fields, str):
        hided_fields = hided_fields.split(',')
    if isinstance(visible_fields, str):
        visible_fields = visible_fields.split(',')

    projection = {
        field: '{}.{}'.format(dollar_prefix(concealer_field), field)
        for field in hided_fields
    }
    projection.update({field: 1 for field in visible_fields})
    if concealer_field == '_id' and concealer_field not in hided_fields:
        projection[concealer_field] = 0
    return {'$project': projection}


def switch(cases_list, last_as_final=False, final_else=''):
    if not cases_list: return final_else
    cases = deepcopy(cases_list)
    case, value = cases.pop(0)
    if not cases and last_as_final: return {'$literal': value}
    else_expr = switch(cases, last_as_final, final_else)
    return {'$cond': [case, value, else_expr]}


def switch_compare(field, cases_list, compare_method='$eq', final_else=''):
    if not cases_list: return final_else
    cases = deepcopy(cases_list)
    case, value = cases.pop(0)
    else_expr = switch_compare(field, cases, compare_method, final_else)
    return {'$cond': [{compare_method: [field, case]}, value, else_expr]}


def ifNull(field, value):
    return {'$ifNull': [dollar_prefix(field), value]}


def cond(condition, then_value, else_value=0):
    if isinstance(condition, str):
        condition = dollar_prefix(condition)
    return {"$cond": [condition, then_value, else_value]}


def _and(*args):
    return {'$and': args}


def eq(first_expression, second_expression=True):
    return {'$eq': [first_expression, second_expression]}


def gt(first_expression, second_expression=None):
    if second_expression is None:
        return {'$gt': first_expression}
    return {'$gt': [first_expression, second_expression]}


def gte(first_expression, second_expression=None):
    if second_expression is None:
        return {'$gte': first_expression}
    return {'$gte': [first_expression, second_expression]}


def ne(first_expression, second_expression=True):
    if second_expression is True:
        return {'$not': [first_expression]}
    return {'$ne': [first_expression, second_expression]}


def field_in(field, values_list):
    field = dollar_prefix(field)
    return {'$or': [
        eq(field, value)
        for value in values_list
    ]}


def optimized_in(value, negative=False, operator_is_required=False):
    """
    Реализует оптимальный фильтр оператора $in. Если значение в списке единственное, то используется оператор $eq.
    Также возможно использование с отрицанием: $nin и $ne.
    Для оператора $eq по умолчанию возвращается только значение, потому что этого достаточно для обычного фильтра.
    Для возврата значения с оператором используйте operator_is_required в значении True.
    :param value: Список значений фильтра
    :param negative: Флаг, использовать ли $nin и $ne вместо $in и $eq
    :param operator_is_required: Флаг, обязательно ли возвращать оператор со значением
    :return: Значение или словарь {оператор: значение}
    >>> optimized_in(['1'])
    '1'
    >>> optimized_in(['1'], operator_is_required=True)
    {'$eq': '1'}
    >>> optimized_in(['1'], negative=True)
    {'$ne': '1'}
    >>> optimized_in(['1', '2'])
    {'$in': ['1', '2']}
    >>> optimized_in(['1', '2'], negative=True)
    {'$nin': ['1', '2']}
    """
    if len(value) == 1:
        value = value[0]
        operator = '$ne' if negative else '$eq' if operator_is_required else ''
    else:
        operator = '$nin' if negative else '$in'

    if operator:
        return {operator: value}
    return value


def field_exists(field):
    """
    >>> field_exists('field')
    {'$or': [{'$eq': ['$field', None]}, {'$gt': ['$field', None]}]}
    >>> field_exists('$field')
    {'$or': [{'$eq': ['$field', None]}, {'$gt': ['$field', None]}]}
    """
    field = dollar_prefix(field)
    return {'$or': [
        {'$eq': [field, None]},
        {'$gt': [field, None]},
    ]}


def concat(*args):
    return {'$concat': args}


def multiply(*args):
    return {'$multiply': _list_dollar_prefix(*args)}


def divide(first_expression, second_expression):
    return {'$divide': _list_dollar_prefix(first_expression, second_expression)}


def aggr_sum(*args):
    args = _list_dollar_prefix(*args)
    if len(args) == 1:
        return {'$sum': args[0]}
    return {'$sum': _list_dollar_prefix(*args)}


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
