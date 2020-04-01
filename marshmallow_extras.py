from functools import partial
from json import loads

import six
from marshmallow import ValidationError

from .iterators import safe_get, iterate_over_hierarchy
from .universal import str_to_list


def convert_to_embed(embed_model, many=False, default="%@#not_specified#@%"):

    def to_embed(obj, context, embed_model, many=False, default="%@#not_specified#@%"):
        if not obj:
            return ([] if many else None) if default == "%@#not_specified#@%" else default
        objs = obj if many else [obj]
        result = [embed_model(**_obj) for _obj in objs]
        return result if many else result[0]

    # Get model
    if isinstance(embed_model, six.string_types):
        from .mongoengine_extras import get_model
        embed_model = get_model(embed_model)
    # Return partial
    return partial(to_embed, embed_model=embed_model, many=many, default=default)


def get_hierarchy(hierarchy, many=False, default="%@#not_specified#@%", convert=None, convert_item=None):
    def _get_single(obj, context, hierarchy, default=None, convert=None):
        value = safe_get(obj, hierarchy, default)
        if value == default:
            return value
        elif convert:
            return convert(value)
        return value

    def _get_many(obj, context, hierarchy, default=[], convert=None, convert_item=None):
        result = list(iterate_over_hierarchy(obj, hierarchy))
        if not result:
            return default
        if convert_item:
            result = [convert_item(value) for value in result]
        if convert:
            result = convert(result)
        return result

    # default is different for single and many. If it is specified - pass it, otherwise use functions defaults.
    kwargs = {} if default == "%@#not_specified#@%" else {'default': default}
    if many:
        return partial(_get_many, hierarchy=hierarchy, convert=convert, convert_item=convert_item, **kwargs)
    else:
        return partial(_get_single, hierarchy=hierarchy, convert=convert, **kwargs)


def convert_to_instance(model, field='id', many=False, error='', primary_key='pk'):

    def to_instance(id, context, model, field='id', many=False, error='', primary_key='pk'):
        if not error:
            error = 'Could not find document.'
        try:
            if many:
                try:
                    if not (id.startswith('[') and id.endswith(']')):
                        raise Exception
                    id = loads(id)
                except:
                    id = str_to_list(id)
                id = list(set(id))
                # Search with filter is faster
                items = list(model.objects.filter(**{f'{primary_key}__in': id}))
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

    if isinstance(model, six.string_types):
        from .mongoengine_extras import get_model
        model = get_model(model)
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
