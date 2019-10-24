#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Модуль содержит паттерны для использования в валидации с помощью jsonschema
"""

from jsonschema import Draft4Validator, FormatChecker


def validate(data, scheme):
    validator = Draft4Validator(scheme, format_checker=FormatChecker())
    errors = sorted(validator.iter_errors(data), key=lambda e: e.path)
    result_errors = {}
    for error in iter(errors):
        error_path = '.'.join(str(path) for path in error.absolute_path)
        message = error.message.replace(r"u'", "'")
        if error_path:
            result_errors[error_path] = message
        else:
            result_errors.setdefault('_', [])
            result_errors['_'].append(message)
    return result_errors


nonempty_string = {
    "type": "string",
    'minLength': 1,
}

email_type = {
    'type': 'string',
    'minLength': 1,
    'pattern': '^.+@.+\..+$',
}

uuid4_pattern = {
    "type": "string",
    'minLength': 36,
    'maxLength': 36,
    "pattern": "^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$",
}

mongo_id_pattern = {
    'type': 'string',
    'minLength': 24,
    'maxLength': 24,
    'pattern': '^[a-z0-9]{24}$',
}

# Дата строкой формата "2017-02-25 13:54:45"
# date.format("%Y-%m-%d %H:%M:%S")
date_pattern = {"format": 'date-time'}

# Дата по ISO
date_ISO8601_Z_pattern = {
    'type': 'string',
    'minLength': 16,
    'maxLength': 27,
    'pattern': '^20[0-9]{2}-[0-1][0-9]-[0-3][0-9]T[0-2][0-9]:[0-6][0-9]:([0-6][0-9])?(.[0-9]{6})?Z?$',
}

int_as_string = {
    'type': 'string',
    'pattern': '^[0-9]+$',
}

float_as_string = {
    'type': 'string',
    'pattern': '^[0-9]+\.[0-9]+$',
}
