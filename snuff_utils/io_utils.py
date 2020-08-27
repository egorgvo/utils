#!/usr/bin/env python3
# -*- encoding: utf-8 -*-

"""
Модуль с вспомогательными функциями ввода-вывода
"""

import codecs
from csv import DictReader

try:
    from .universal import str_to_list
except:
    from snuff_utils.universal import str_to_list


def yesno_question(question, example='y/n', retry=True, retry_message='',
                   yes_choices='y,yes,д,да', no_choices='n,no,н,нет'):
    """
    Реализует вопросы на "да/нет" в консоли

    :param question: Вопрос
    :type question: str
    :param example: Пример ответа
    :type example: str
    :param retry: Флаг, повторить вопрос при некорректном ответе
    :type retry: bool
    :param retry_message: Сообщение, для вывода в случае, если введен некорректный вопрос
    :type retry_message: str
    :param yes_choices: Варианты "да", через запятую
    :type yes_choices: str
    :param no_choices: Варианты "нет", через запятую
    :type no_choices: str
    :rtype: bool
    """
    answers = {
        True: map(str.strip, yes_choices.split(',')),
        False: map(str.strip, no_choices.split(','))
    }
    answers = {variation: boolean for boolean, variations in answers.items() for variation in variations}
    answer = input(f"{question} ({example})\n")
    while True:
        answer = answers.get(answer.lower())
        if not retry or answer is not None:
            return answer
        answer = input(retry_message)


def variants_question(question, answers=None, improved_answers=None, retry=True, retry_message='', **kwargs):
    """
    Реализует вопросы на "да/нет" в консоли

    :param question: Вопрос
    :type question: str
    :param answers: Варианты ответа, словарь с ключами типа строка
    (ключ будет использоваться как значение ввода пользователя)
    :type answers: dict
    :param improved_answers: Варианты ответа, которые будут возвращены пользователю (если указаны),
    ключи словаря соответствуют вводимым пользователем ответам.
    :type improved_answers: dict
    :param retry: Флаг, повторить вопрос при некорректном ответе
    :type retry: bool
    :param retry_message: Сообщение, для вывода в случае, если введен некорректный вопрос
    :type retry_message: str
    :param kwargs: Варианты ответа, которыми пополнится answers.
    Также, ключами с суффиксом _improved пополнится словарь improved_answers.
    :rtype: Вариант ответа - ключ словаря answers, либо значение словаря improved_answers,
    соответствующее ключу словаря answer, если таковое присутствует.
    """
    if not improved_answers:
        improved_answers = {}
    improved_answers.update({k[:-9]: v for k, v in kwargs.items() if k.endswith('_improved')})
    if not answers:
        answers = {}
    answers.update({k: v for k, v in kwargs.items() if not k.endswith('_improved')})
    answers_presentation = '\n'.join(f'{key} - {value}' for key, value in answers.items())
    answer = input(f"{question}\n{answers_presentation}\n")
    while True:
        answer = answer.lower()
        if answer not in answers and answer.isdigit() and int(answer) in answers:
            answer = int(answer)
        if answer in answers and answer in improved_answers:
            return improved_answers[answer]
        if answer in answers:
            return answer
        if not retry:
            return None
        answer = input(retry_message)


def sv_import(filename, field_names=None, fields_converters=None, comment_symbol='', sep=','):
    if not fields_converters:
        fields_converters = {}
    with open(filename, 'r') as svfile:
        read_rule = filter(lambda row: row and row[0] != comment_symbol, svfile) if comment_symbol else svfile
        csvreader = DictReader(read_rule, delimiter=sep, fieldnames=field_names)
        for row in csvreader:
            for field, converter in fields_converters.items():
                row[field] = converter(row.get(field, None))
            yield row


def sv_export(rows, filename, ordered_fields=None, ordered_fields_view=None, write_header=True, sep=',',
              encoding='utf-8', rw_mode='w'):
    if not filename:
        return None
    if ordered_fields:
        ordered_fields = str_to_list(ordered_fields)
    if not ordered_fields_view:
        ordered_fields_view = ordered_fields
    if ordered_fields_view:
        ordered_fields_view = str_to_list(ordered_fields_view)
    with codecs.open(filename, rw_mode, encoding=encoding) as sv_file:
        # Writing header
        if ordered_fields and write_header:
            sv_file.write(sep.join(ordered_fields_view) + "\n")
        # Writing rows
        if ordered_fields:
            for row in rows:
                line_str = '{}\n'.format(sep.join((str(row.get(key, '')) for key in ordered_fields)))
                sv_file.write(line_str)
        else:
            rows = (f'{row}\n' for row in rows)
            sv_file.writelines(rows)
    return filename
