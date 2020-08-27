from copy import copy
from sqlalchemy.orm.query import Query, _entity_descriptor


class CustomQuery(Query):
    allowed_operators = ['icontains']

    @classmethod
    def _convert_names_with_underlines_to_dots(cls, **kwargs):
        """Проверяем обращение к полям объекта с помощью __ в словаре"""
        explicit = copy(kwargs)
        with_operator = {}
        for key, value in kwargs.items():
            if '__' not in key:
                continue
            elif key.startswith('__') or key.endswith('__'):
                continue
            replacement = key.replace('__', '.')
            potential_operator = replacement[replacement.rfind('.') + 1:]
            if potential_operator not in cls.allowed_operators:
                continue
            field = replacement[:replacement.rfind('.')]
            with_operator.setdefault(field, [])
            with_operator[field].append((potential_operator, explicit.pop(key)))
        return explicit, with_operator

    def filter_by(self, **kwargs):
        """
        Overload of standard function
        """
        implicit, with_operator = self._convert_names_with_underlines_to_dots(**kwargs)
        query = super().filter_by(**implicit)
        clauses = []
        for key, pairs in with_operator.items():
            for pair in pairs:
                operator, value = pair
                field = _entity_descriptor(self._joinpoint_zero(), key)
                if operator == 'icontains':
                    clause = field.ilike(f'%{value}%')
                clauses.append(clause)
        return query.filter(*clauses)
