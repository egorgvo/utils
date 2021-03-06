#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Module is deprecated. Use https://github.com/egorgvo/mongo_aggregation instead.
"""

import logging
from copy import copy
from itertools import chain, combinations, product

from .mongo_aggregation_patterns import dollar_prefix, pop_dollar_prefix

logger = logging.getLogger(__name__)


class MongoAggregation(list):

    def __init__(self, pipeline='', collection='', allowDiskUse=False):
        self.collection = collection
        self.allowDiskUse = allowDiskUse
        self.actual_fields = set()
        self.pipeline = pipeline if pipeline else []

    def aggregate(self, collection='', allowDiskUse=False, as_list=False, collation=None):
        if collection:
            self.collection = collection
        if allowDiskUse:
            self.allowDiskUse = allowDiskUse
        if self.collection.__class__.__name__ != 'QuerySet' and not self.collection:
            logger.error('Агрегация невозможна: не указана коллекция')
            return
        if self.collection.__class__.__name__ == 'QuerySet':
            result = self.collection.aggregate(*self.pipeline, allowDiskUse=self.allowDiskUse, collation=collation)
        else:
            result = self.collection.aggregate(self.pipeline, allowDiskUse=self.allowDiskUse, collation=collation)
        return list(result) if as_list else result

    def append(self, object=None, *args):
        if not object: object = []
        if isinstance(object, list):
            self.pipeline.extend(object)
        else:
            self.pipeline.append(object)
        if args:
            for arg in args:
                self.pipeline.append(arg)
        return self

    def extend(self, object=None, *args):
        self.append(object, *args)

    def match(self, *args, **kwargs):
        if args:
            for arg in args:
                self.pipeline.append({
                    '$match': arg
                })
        self._convert_names_with_underlines_to_dots(kwargs, convert_operators=True)
        if args and kwargs:
            self.pipeline[-1]['$match'].update(kwargs)
        elif kwargs:
            self.pipeline.append({
                '$match': kwargs
            })
        self._add_to_actual_fields([
            x for x in self.last_stage.statement.keys()
            if not x.startswith('$')
        ])
        return self

    def lookup_unwind(self, collection, local_field='_id', as_field='', foreign_field='_id', preserveNullAndEmptyArrays=True):
        if not as_field:
            as_field = local_field
        self.lookup(collection, local_field, as_field, foreign_field),
        self.unwind(as_field, preserveNullAndEmptyArrays)
        return self

    def lookup(self, collection, local_field='_id', as_field='', foreign_field='_id'):
        if not as_field:
            as_field = local_field
        self.pipeline.append({"$lookup": {
            'from': collection,
            'foreignField': foreign_field,
            'localField': local_field,
            'as': as_field,
        }})
        self._add_to_actual_fields(local_field, ignore_if_theres_children=True)
        self._add_to_actual_fields(as_field, ignore_if_theres_children=True)
        return self

    def unwind(self, field, preserveNullAndEmptyArrays=False):
        field = dollar_prefix(field)
        if preserveNullAndEmptyArrays:
            self.pipeline.append({'$unwind': {'path': field, 'preserveNullAndEmptyArrays': True}})
        else:
            self.pipeline.append({'$unwind': field})
        self._add_to_actual_fields(field, ignore_if_theres_children=True)
        return self

    def sort(self, *args, **kwargs):
        self._convert_names_with_underlines_to_dots(kwargs)
        # Складываем все в args
        args = list(args)
        if kwargs:
            args.append(kwargs)

        if not args: return self
        # Делаем project
        for arg in args:
            self.pipeline.append({"$sort": arg})
            self._add_to_actual_fields(arg.keys())
        return self

    def skip(self, offset=0):
        if not offset: return self
        self.pipeline.append({"$skip": offset})
        return self

    def limit(self, limit=0):
        if not limit: return self
        self.pipeline.append({"$limit": limit})
        return self

    def project(self, *args, **kwargs):
        self._convert_names_with_underlines_to_dots(kwargs)
        # Складываем все в args
        if args and kwargs:
            args[-1].update(kwargs)
        elif kwargs:
            args = (kwargs,)
        if not args: return self

        # Делаем project
        for arg in args:
            self.pipeline.append({'$project': arg})
        # Заполняем актуальные поля
        self._set_actual_fields(arg.keys())
        return self

    def _get_fields_without_children(self, fields):
        parents = copy(fields)
        for one, another in combinations(fields, 2):
            is_children = another.startswith(f'{one}.')
            if is_children:
                parents.discard(another)
                continue
            is_children = one.startswith(f'{another}.')
            if is_children:
                parents.discard(one)
                continue
        return parents

    @staticmethod
    def _str_to_list(variable):
        return variable.split(',') if isinstance(variable, str) else variable

    def _set_actual_fields(self, *fields):
        """Устанавливает список актуальных полей"""
        self.actual_fields = set(chain(*fields))

    def _add_to_actual_fields(self, fields, ignore_if_theres_children=True):
        """Добавляет поля в список актуальных полей"""
        _fields = set(self._str_to_list(fields))
        if ignore_if_theres_children:
            _fields = [
                field
                for field in _fields
                if pop_dollar_prefix(field) not in self.get_parents(self.actual_fields, all_levels=True)
            ]
        for field in _fields:
            self.actual_fields.add(pop_dollar_prefix(field))

    @staticmethod
    def get_parents(fields, all_levels=False, upper_level=True):
        if isinstance(fields, str):
            fields = set(fields.split(','))

        # Самый нижний уровень
        if not all_levels and not upper_level:
            return {field.split('.')[0] for field in fields}

        # Все уровни и верхний
        parents = set()
        for field in fields:
            splitted = field.split('.')
            for i in range(len(splitted)):
                splitted.pop()
                if not splitted: break
                parents.add('.'.join(splitted))
                # Только верхний уровень
                if not all_levels: break
        return parents

    def smart_project(self, include_fields='', exclude_fields='', include_all_by_default=True, *args, **kwargs):
        if not include_all_by_default:
            self.actual_fields = set()

        exclude_id = False
        if exclude_fields:
            exclude_fields = set(exclude_fields.split(','))
            exclude_id = '_id' in exclude_fields
        if exclude_fields and not include_all_by_default:
            pass
        elif exclude_fields:
            for excl_field in exclude_fields:
                if excl_field in self.actual_fields:
                    self.actual_fields.discard(excl_field)
                    # continue
                # Убираем дочерние. К примеру:
                # actual_fields = {'menu.elements.option', 'menu.elements.count', 'count'}
                # exclude_field = 'menu.elements'
                # Дочерние: 'menu.elements.option', 'menu.elements.count'
                # Результат: actual_fields = {'count'}
                child_fields = {
                    act_field for act_field in self.actual_fields
                    if '{}.'.format(excl_field) in act_field
                }
                if child_fields:
                    self.actual_fields -= child_fields
                    continue
                # Обратная ситуация, когда
                # actual_fields = {'menu.elements', 'count'}
                # exclude_field = 'menu.elements.option'
                # Решение неочевидное, пока делаем так:
                # Отбрасываем последнее дочернее поле
                # ('option' для 'menu.elements.option', останется 'menu.elements')
                # Ищем соответствие; если находим, удаляем его, иначе идем дальше к родителю
                # Результат: actual_fields = {'count'}
                for parent in sorted(self.get_parents(excl_field, True), key=len, reverse=True):
                    if parent not in self.actual_fields: continue
                    self.actual_fields.discard(parent)
                    break

        if include_fields:
            include_fields = set(include_fields.split(','))
            parent_fields = self.get_parents(include_fields, True)
            self.actual_fields -= parent_fields
            self.actual_fields.update(include_fields)

        # Проверяем обращение к полям объекта с помощью __ в kwargs
        self._convert_names_with_underlines_to_dots(kwargs)

        # Складываем kwargs в args
        args = self._add_kwargs_to_args(args, kwargs)

        # def include_actual_fields_recursive(stage, field):
        #     hierarchy = field.split('.')
        #     for i in range(len(hierarchy)):
        #         parent_field = '.'.join(hierarchy[:i + 1])
        #         if i + 1 == len(hierarchy):
        #             theres_children = any([f.startswith(f"{field}.") for f in stage])
        #             if theres_children:
        #                 return
        #             break
        #         if parent_field not in stage:
        #             continue
        #         elif not stage[parent_field] or not isinstance(stage[parent_field], dict):
        #             return
        #         elif stage[parent_field].keys()[0].startswith('$'):
        #             return
        #         include_actual_fields_recursive(stage[parent_field], '.'.join(hierarchy[i+1:]))
        #         return
        #     stage.setdefault(field, 1)

        # for field in self._get_actual_fields_without_children():
        #     include_actual_fields_recursive(args[-1], field)

        paths = self._get_stage_hierarchy_fields(args[-1])
        if not paths and self.actual_fields:
            prolong_fields = self.actual_fields
        else:
            prolong_fields = set([actual_field
                                  for new_field, actual_field in product(paths, self.actual_fields)
                                  if actual_field != new_field
                                  and not actual_field.startswith(f'{new_field}.')
                                  and not new_field.startswith(f'{actual_field}.')])
        prolong_fields = self._get_fields_without_children(prolong_fields)
        for field in prolong_fields:
            args[-1].setdefault(field, 1)

        if exclude_id:
            args[-1]['_id'] = 0

        # Делаем project
        if args:
            for arg in args:
                self.pipeline.append({'$project': arg})
            # Заполняем актуальные поля
            actual_fields = self._get_stage_hierarchy_fields(arg)
            if exclude_id:
                actual_fields.remove('_id')
            self._set_actual_fields(actual_fields)
        return self

    def _get_stage_hierarchy_fields(self, stage, prefix=''):
        def get_fields_for_dict_value(value, prefix=''):
            if not isinstance(value, dict):
                return []
            if list(value.keys())[0].startswith('$'):
                literal = value.get('$literal')
                if literal and isinstance(literal, dict):
                    return self._get_stage_hierarchy_fields(literal, prefix)

                return [prefix]
            return self._get_stage_hierarchy_fields(value, prefix)

        paths = []
        for field, value in stage.items():
            new_prefix = f'{prefix}.{field}' if prefix else field
            if isinstance(value, list):
                for obj in value:
                    if isinstance(obj, dict):
                        paths.extend(get_fields_for_dict_value(obj, prefix=new_prefix))
                        break
                continue
            elif isinstance(value, dict):
                paths.extend(get_fields_for_dict_value(value, prefix=new_prefix))
                continue
            paths.append(new_prefix)
            continue
        return paths

    @staticmethod
    def _add_kwargs_to_args(args, kwargs):
        # Складываем kwargs в args
        if args and kwargs:
            args[-1].update(kwargs)
        elif kwargs:
            args = (kwargs,)
        elif not args:
            args = ({},)
        return args

    def group(self, *args, **kwargs):
        """
        Стадия группировки

        :param group_by: Поля группировки. Можно подавать строкой через запятую, либо списком, либо словарем
        :param first_fields: Список полей для оператора $first. Строка либо список.
        :param min_fields: Список полей для оператора $min. Строка либо список.
        :param max_fields: Список полей для оператора $max. Строка либо список.
        :param sum_fields: Список полей для оператора $sum. Строка либо список.
        :param counter_fields: Список полей для оператора $sum, количество просуммированных строк. Строка либо список.
        :param avg_fields: Список полей для оператора $avg. Строка либо список.
        :param push_fields: Список полей для оператора $push. Строка либо список.
        :param addToSet_fields: Список полей для оператора $addToSet. Строка либо список.
        :param operator_by_default: Используемый оператор для остальных полей actual_fields. По умолчанию не добавляет остальные поля в результат.
        :param exclude_fields: Использовать operator_by_default для всех, кроме перечисленных. Строка через запятую, либо список.
        :param args: Описание остальных полей группировки словарем, либо несколькими словарями.
        :param kwargs: Описание остальных полей группировки именованными аргументами.
        :return:
        """
        group_by = kwargs.pop('group_by', None)
        first_fields = kwargs.pop('first_fields', None)
        min_fields = kwargs.pop('min_fields', None)
        max_fields = kwargs.pop('max_fields', None)
        sum_fields = kwargs.pop('sum_fields', None)
        counter_fields = kwargs.pop('counter_fields', None)
        avg_fields = kwargs.pop('avg_fields', None)
        push_fields = kwargs.pop('push_fields', None)
        add_to_set_fields = kwargs.pop('addToSet_fields', None)
        operator_by_default = kwargs.pop('operator_by_default', None)
        exclude_fields = kwargs.pop('exclude_fields', False)
        if exclude_fields:
            exclude_fields = exclude_fields.split(',')

        # Инициализируем stage группировки
        stage = {}

        # Добавляем kwargs и args в stage
        args = self._add_kwargs_to_args(args, kwargs)
        for arg in args:
            if not isinstance(arg, dict): continue
            if not arg: continue
            stage.update(arg)

        # Подготовка и обработка операторов группировки
        operators = {
            '$first': first_fields,
            '$min': min_fields,
            '$max': max_fields,
            '$sum': sum_fields,
            '$avg': avg_fields,
            '$push': push_fields,
            '$addToSet': add_to_set_fields,
        }
        for operator, fields in operators.items():
            if not fields: continue
            self._group_set_operator(stage, fields, operator)
        if counter_fields:
            self._counter_set_operator(stage, counter_fields)

        # Указываем поле группировки
        stage['_id'] = self._group_get_id(group_by)

        # Устанавливаем по дефолту $first для остальных полей
        if operator_by_default:
            parent_fields = self.get_parents(self.actual_fields, True)
            if isinstance(stage['_id'], str):
                _id_fields = pop_dollar_prefix(stage['_id'])
            else:
                _id_fields = stage['_id'].keys()
            for field in parent_fields:
                if field in chain(stage, _id_fields): continue
                elif field in exclude_fields: continue
                stage[field] = {operator_by_default: dollar_prefix(field)}

        # Формируем actual_fields
        if not stage['_id']:
            _id_fields = []
        elif isinstance(stage['_id'], str):
            _id_fields = ['_id']
        else:
            _id_fields = ['_id.{}'.format(key) for key in stage['_id'].keys()]

        def get_prolonged_actual_fields_for(*fields_lists):
            prolong_fields = []
            new_fields = [self._str_to_list(fields) for fields in fields_lists if fields]
            for actual_field, new_field in product(self.actual_fields, chain(*new_fields)):
                if not actual_field.startswith(new_field):
                    continue
                prolong_fields.append(actual_field)
            return prolong_fields

        prolonged_actual_fields = get_prolonged_actual_fields_for(first_fields, push_fields, add_to_set_fields)
        self._set_actual_fields(stage, _id_fields, prolonged_actual_fields)

        self.pipeline.append({'$group': stage})
        return self

    def _group_set_operator(self, stage, fields, operator):
        if not fields: return
        if isinstance(fields, str):
            fields = fields.split(',')
        fields = self._convert_names_with_underlines_to_dots(fields)
        if isinstance(fields, dict):
            fields = fields.keys()
        for field in fields:
            stage[pop_dollar_prefix(field)] = {operator: dollar_prefix(field)}

    def _counter_set_operator(self, stage, fields):
        if not fields: return
        if isinstance(fields, str):
            fields = fields.split(',')
        fields = self._convert_names_with_underlines_to_dots(fields)
        if isinstance(fields, dict):
            fields = fields.keys()
        for field in fields:
            stage[pop_dollar_prefix(field)] = {'$sum': 1}

    def _group_get_id(self, group_by=None):
        # Допустимая ситуация: группировка всех строк в одну
        if not group_by: return None

        # Преобразуем к списку, если строка
        if isinstance(group_by, str):
            group_by = group_by.split(',')

        # Преобразуем имена вида item__name к item.name
        group_by = self._convert_names_with_underlines_to_dots(group_by)

        # Если group_by - словарь, считаем его сформированным корректно
        if isinstance(group_by, dict):
            return group_by

        # Если список, формируем словарь или одно соответсвие
        if isinstance(group_by, list):
            if len(group_by) == 1:
                return dollar_prefix(group_by[0])

            return {pop_dollar_prefix(field): dollar_prefix(field) for field in group_by}

        # Опасная ситуация, но иначе никак - пусть группирует по всем строкам
        return None

    @staticmethod
    def _convert_names_with_underlines_to_dots(args, convert_operators=False):
        """Проверяем обращение к полям объекта с помощью __ в словаре"""
        for i, arg in enumerate(copy(args)):
            if '__' not in arg:
                continue
            elif arg.startswith('__') or arg.endswith('__'):
                continue
            replacement = arg.replace('__', '.')
            if isinstance(args, list):
                args.pop(i)
                args.insert(i, replacement)
            else:
                if convert_operators:
                    potential_operator = replacement[replacement.rfind('.')+1:]
                    if potential_operator in ['eq', 'ne', 'gt', 'gte', 'lt', 'lte', 'in', 'nin']:
                        args[replacement[:replacement.rfind('.')]] = {dollar_prefix(potential_operator): args.pop(arg)}
                        continue
                args[replacement] = args.pop(arg)
        return args

    @property
    def last_stage(self):
        if not self.pipeline:
            return None
        return LastStage(self.pipeline)


class LastStage():

    def __init__(self, pipeline):
        if not pipeline:
            raise Exception("Последнего этапа в этой агрегации не существует.")
        self.__data = pipeline[-1]

    @property
    def name(self):
        return list(self.__data.keys())[0]

    @name.setter
    def name(self, value):
        self.__data[value] = self.__data.pop(self.name)

    @property
    def statement(self):
        return self.__data[self.name]

    @statement.setter
    def statement(self, value):
        self.__data[self.name] = value

    def __repr__(self):
        return str(self.__data)


if __name__ == "__main__":
    import logging
    from config.database import mongo_connection
    import pymongo
    from datetime import datetime
    from dateutil.relativedelta import relativedelta
    logger = logging.getLogger()
    client = pymongo.MongoClient(mongo_connection)
    db = client.get_default_database()
    today = datetime.now()
    yesterday = today - relativedelta(days=1)

    pipeline = MongoAggregation(collection=db.action)
    pipeline.match(
        {'date': {'$gte': yesterday, '$lt': today}},
        completed=True,
        _cls={'$in': [
            'Action.Order', 'Action.StorageIncome', 'Action.StorageCancellation', 'Action.StorageMovementOutcome'
        ]},
    ).smart_project(
        'transactions.amount,_cls', '_id'
    ).append([
        {'$project': {
            '_cls': 1,
            'date': 1,
            'transactions.amount': 1,
            'transactions.cashbox': 1,
        }},
    ]).project(
        {'transactions.amount':1, 'transactions.cashbox': 1}, _cls=1, date=1
    ).project(
        transactions=1, _cls=1, date=1
    )
    cursor = pipeline.aggregate()

    for doc in cursor:
        print(doc)
        break