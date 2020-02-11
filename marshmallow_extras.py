import six
from functools import partial
from marshmallow import ValidationError

from .iterators import safe_get
from .mongoengine_extras import get_model


def get_hierarchy(hierarchy, default=None, convert=None, where=None):
    def _get_hierarchy(obj, context, hierarchy, default=None, convert=None, where=None):
        if where:
            for k, v in where.items():
                if safe_get(obj, k) == v:
                    continue
                return default
        value = safe_get(obj, hierarchy, default)
        if value == default:
            return value
        elif convert:
            return convert(value)
        return value
    return partial(_get_hierarchy, hierarchy=hierarchy, default=default, convert=convert, where=where)


def convert_to_instance(model, field='id', many=False, error='', primary_key='id'):

    def to_instance(id, context, model, field='id', many=False, error='', primary_key='id'):
        if not error:
            error = 'Could not find document.'
        if isinstance(model, six.string_types):
            model = get_model(model)
        try:
            if many:
                id = list(set(id))
                # Search with filter is faster
                items = list(model.objects.filter(**{primary_key: {'$in': id}}))
                if len(items) == len(id):
                    return items
                # If something has not been found - we need to figure out the guilty
                # Get method will do this explicitly
                # It will be longer but it doesn't matter - there's an error anyway
                else:
                    return [model.objects.get(**{primary_key: _id}) for _id in id]
            else:
                return model.objects.get(**{primary_key: id})
        except Exception as exc:
            raise ValidationError(error, field_name=field)

    return partial(to_instance, model=model, field=field, many=many, error=error, primary_key=primary_key)


def split_str(sep=',', convert=None, validate=None, field='id', error=''):
    def _get_hierarchy(obj, context, sep=',', convert=None, validate=None, field='id', error=''):
        if not error:
            error = 'Unable to get value.'
        if isinstance(obj, list):
            return obj
        elif not isinstance(obj, str):
            return []
        value = [v.strip() for v in obj.split(sep)]
        if convert:
            try:
                value = [convert(v) for v in value]
            except Exception as exc:
                raise ValidationError(error, field_name=field)
        if validate:
            value = [validate(v) for v in value]
        return value
    return partial(_get_hierarchy, sep=sep, convert=convert, validate=validate, field=field, error=error)


def convert(convert, field='id', error=''):
    def _get_hierarchy(obj, context, convert, field='id', error=''):
        if not error:
            error = 'Unable to get value.'
        try:
            value = convert(obj)
        except Exception as exc:
            raise ValidationError(error, field_name=field)
        return value
    return partial(_get_hierarchy, convert=convert, field=field, error=error)
