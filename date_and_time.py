#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с универсальными и вспомогательными классами и функциями для работы с датами и временем
"""

import logging
from datetime import datetime, time, timedelta

from dateutil.relativedelta import relativedelta
from pytz import UTC, timezone

logger = logging.getLogger()


def utcnow():
    return UTC.localize(datetime.utcnow())


def _timezone(timezone_info):
    if timezone_info in ('msk', 'MSK', 'Moscow'):
        timezone_info = timezone('Europe/Moscow')
    elif isinstance(timezone_info, str):
        return timezone(timezone_info)
    return timezone_info


def as_timezone(source_date, as_tz='UTC', source_tz_by_default='UTC'):
    as_tz = _timezone(as_tz)
    if not source_date.tzinfo:
        source_date = source_date.replace(tzinfo=_timezone(source_tz_by_default))
    return source_date.astimezone(as_tz)


def localize(some_date, new_timezone='UTC', force=False):
    if some_date.tzinfo and (not force or not new_timezone):
        return some_date
    if not new_timezone:
        new_timezone = UTC
    new_timezone = _timezone(new_timezone)
    return new_timezone.localize(some_date.replace(tzinfo=None))


def duration(open_date, close_date=None, time_unit='seconds'):
    if not close_date:
        close_date = datetime.utcnow()
        if open_date.tzinfo:
            close_date = localize(close_date, open_date.tzinfo)
    if time_unit in ('d', 'day', 'days'):
        return (close_date - open_date).days
    elif time_unit in ('h', 'hour', 'hours'):
        return (close_date - open_date).days * 24 + (close_date - open_date).seconds // 360
    elif time_unit in ('m', 'minute', 'minutes'):
        return (close_date - open_date).days * 24 * 60 + (close_date - open_date).seconds // 60
    else:
        return (close_date - open_date).days * 24 * 60 * 60 + (close_date - open_date).seconds


def duration_format(duration, time_unit='second'):
    if isinstance(duration, timedelta):
        delta = timedelta
    elif time_unit in ('s', 'sec', 'second', 'seconds'):
        delta = timedelta(0, duration)
    elif time_unit in ('m', 'min', 'minute', 'minutes'):
        delta = timedelta(0, duration * 60)
    elif time_unit in ('h', 'hour', 'hours'):
        delta = timedelta(0, duration * 60 * 60)
    elif time_unit in ('d', 'day', 'days'):
        delta = timedelta(0, duration * 60 * 60 * 24)

    days = delta.days
    # Дни с 5 по 20 в каждой сотне
    if 4 < days % 100 < 21:
        days_format = 'дней'
    # Дни с 1 на конце
    elif days % 10 == 1:
        days_format = 'день'
    # Дни с 2, 3 или 4 на конце
    elif days % 10 in (2, 3, 4):
        days_format = 'дня'
    else:
        days_format = 'дней'
    return str(delta).replace('days', days_format).replace('day', 'день')


def day_start(day):
    """
    Возвращает дату и время начала дня указанной даты

    :param day: Дата
    :type day: date
    :rtype: datetime

    >>> day_start(datetime(2018, 1, 5, 23, 45))
    datetime.datetime(2018, 1, 5, 0, 0)
    >>> day_start(datetime(2018, 2, 24, 12, 22, 22, 908))
    datetime.datetime(2018, 2, 24, 0, 0)
    """
    if isinstance(day, datetime):
        return datetime.combine(day, time.min).replace(tzinfo=day.tzinfo)
    return datetime.combine(day, time.min)


def next_day(day):
    """
    Возвращает дату и время начала дня указанной даты

    :param day: Дата
    :type day: date
    :rtype: datetime

    >>> next_day(datetime(2018, 1, 5, 23, 45))
    datetime.datetime(2018, 1, 6, 0, 0)
    >>> next_day(datetime(2018, 2, 24, 12, 22, 22, 908))
    datetime.datetime(2018, 2, 25, 0, 0)
    """
    return day_start(day) + timedelta(days=1)


def week_start(some_date):
    """
    Возвращает дату и время начала недели для указанной даты

    :param some_date: Дата
    :type some_date: date
    :rtype: datetime

    >>> week_start(datetime(2018, 1, 1))
    datetime.datetime(2018, 1, 1, 0, 0)
    >>> week_start(datetime(2018, 2, 1))
    datetime.datetime(2018, 1, 29, 0, 0)
    """
    return day_start(some_date) - timedelta(days=some_date.weekday())


def next_week(some_date):
    """
    Возвращает дату и время начала недели для указанной даты

    :param some_date: Дата
    :type some_date: date
    :rtype: datetime

    >>> next_week(datetime(2018, 1, 1))
    datetime.datetime(2018, 1, 8, 0, 0)
    >>> next_week(datetime(2018, 2, 1))
    datetime.datetime(2018, 2, 5, 0, 0)
    """
    return week_start(some_date) + timedelta(weeks=1)


def month_start(some_date):
    """
    Возвращает дату и время начала месяца для указанной даты

    :param some_date: Дата
    :type some_date: date
    :rtype: datetime

    >>> month_start(datetime(2018, 1, 5))
    datetime.datetime(2018, 1, 1, 0, 0)
    >>> month_start(datetime(2018, 2, 28))
    datetime.datetime(2018, 2, 1, 0, 0)
    """
    return day_start(some_date.replace(day=1))


def next_month(some_date):
    """
    Возвращает дату и время начала месяца для указанной даты

    :param some_date: Дата
    :type some_date: date
    :rtype: datetime

    >>> next_month(datetime(2018, 1, 5))
    datetime.datetime(2018, 2, 1, 0, 0)
    >>> next_month(datetime(2018, 2, 28))
    datetime.datetime(2018, 3, 1, 0, 0)
    """
    return month_start(some_date) + relativedelta(months=1)


def tz_offset_in_ms(timezone):
    return timezone.utcoffset(datetime.utcnow()).seconds * 1000


if __name__ == '__main__':

    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
