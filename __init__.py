#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с универсальными классами и функциями
"""

from universal.universal import join_nonempty
from universal.date_and_time import duration, duration_format, localize, utcnow, \
    as_timezone, day_start, next_day, week_start, next_week, month_start, next_month, tz_offset_in_ms
from universal.list_of_dicts import find_dict_in_list, sort_list_of_dicts
from universal.yandex_mailer import YandexMailer
from universal.DottedDict import DottedDict
from universal.MongoAggregation import MongoAggregation
