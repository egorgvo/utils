#!/usr/bin/env python2.7
# coding=utf-8

"""
Модуль, описывающий класс Timer замера времени исполнения кода
"""

import logging
from collections import OrderedDict
from time import time as time_time

import six

logger = logging.getLogger()


class Timer(object):
    """
    Класс для замера времени

    Использование:
    # Инициализация таймера и установка общего интервала функции (опционально)
    timer = Timer('whole_func')
    # Запуск замеров блоками
    timer.add_point('first block')
    ...
    timer.add_point('second block')
    ...
    # Устанавливаем конец периода для конкретного интервала
    timer.stop('first block')
    timer.add_point('third block')
    ...
    # останавливает все интервалы и выводит суммарную информацию
    timer.stop().print_summary()
    # [2017-10-09 17:06:10 INFO] PROFILING: whole_func: 5000, first block: 3000, second block: 2000, third block: 2000
    """
    def __init__(self, timer_name=''):
        super(Timer, self).__init__()
        self.time_intervals = OrderedDict()

        self.timer_name = None
        if timer_name:
            self.add_point(timer_name)
            self.timer_name = timer_name

    def _unused_name(self, template='point_{}'):
        i = 0
        while True:
            i += 1
            if template.format(i) in self.time_intervals:
                continue
            return template.format(i)

    def start(self, name='', description='', prolong=True):
        return self.add_point(name, description, prolong)

    def stop(self, name=''):
        """
        Закрывает все незавершенные замеры
        """
        # Закрываем интервал по имени
        if name:
            self.time_intervals[name]['intervals'][-1]['end'] = time_time()
            return self

        # либо все незакрытые интервалы
        for intervals_info in self.time_intervals.values():
            for interval in intervals_info['intervals']:
                if 'end' in interval: continue
                interval['end'] = time_time()

        if self.timer_name:
            self.stop(self.timer_name)
        return self

    def add_point(self, name='', description='', prolong=True):
        """
        Добавление нового периода замера
        :param name: Наименование замера
        :param description: Описание замера
        """
        # закрываем все предыдущие замеры
        self.stop()

        # Назначаем имя новому замеру
        name = name if name else self._unused_name()

        # Стартуем замер
        if not name in self.time_intervals or not prolong:
            self.time_intervals[name] = {'intervals': [], 'description': description}
        self.time_intervals[name]['intervals'].append({'beginning': time_time()})
        return self

    def __str__(self):
        """
        Вывод результатов замера
        """
        string = "Наименование:\tДлительность\tОписание"
        for name, interval in self.time_intervals.items():
            string += "\n{:18}\t{:<10}\t{}".format(name, self.duration(interval['intervals']), interval['description'])
        return string

    def print_summary(self, prefix=''):
        logger.info('PROFILING: {}{}'.format(prefix, ', '.join((
            '{}: {}'.format(interval, self.duration(interval))
            for interval in self.time_intervals
        ))))

    def duration(self, interval):
        if isinstance(interval, six.string_types):
            interval = self.time_intervals[interval]['intervals']
        if isinstance(interval, list):
            return sum([int((i['end'] - i['beginning']) * 1000) for i in interval])
        else:
            return int((interval['end'] - interval['beginning']) * 1000)


if __name__ == "__main__":
    from time import sleep
    # Настройки логирования
    logging.basicConfig(
        format='[%(asctime)s %(levelname)s] %(message)s',
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)
    timer = Timer('main')
    timer.start('1')
    sleep(1)
    timer.stop('1')
    sleep(1)
    timer.stop().print_summary()
