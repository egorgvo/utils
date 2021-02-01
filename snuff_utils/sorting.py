#!/usr/bin/env python3
# coding=utf-8

from snuff_utils.iterators import safe_get


def default_cmp(one, other):
    """
    Default comparison function.
    Gives 1 if one > other, 0 if one == other, -1 if one < other.
    """
    if isinstance(one, dict) or isinstance(other, dict):
        return 0
    elif one > other:
        return 1
    elif one < other:
        return -1
    return 0


def compare_by_weight(*weight_sequence, partial=False):
    """
    Returns function that compares values by its index in weight sequence.
    Uses default compare if values are not in sequence.
    :param weight_sequence: weight sequence, list of values, allow comma-separated string
    """
    if len(weight_sequence) == 1:
        weight_sequence = weight_sequence[0]
    if isinstance(weight_sequence, str):
        weight_sequence = weight_sequence.split(',')

    def wrapped(one, other):
        cmp_map = {'one': False, 'other': False}
        weight_index_map = {'one': 0, 'other': 0}
        for variable, match_key in [(one, 'one'), (other, 'other')]:
            if not partial or not isinstance(variable, dict):
                cmp_map[match_key] = variable in weight_sequence
                if cmp_map[match_key]:
                    weight_index_map[match_key] = weight_sequence.index(variable)
                continue

            for cmp_dict in weight_sequence:
                if not isinstance(cmp_dict, dict):
                    continue
                if all([safe_get(variable, key) == value for key, value in cmp_dict.items()]):
                    cmp_map[match_key] = True
                    weight_index_map[match_key] = weight_sequence.index(cmp_dict)
                    break
            else:
                cmp_map[match_key] = False
        if all(cmp_map.values()):
            return weight_index_map['one'] - weight_index_map['other']
        elif cmp_map['one']:
            return -1
        elif cmp_map['other']:
            return 1
        return default_cmp(one, other)

    return wrapped


def cmp_for_sorted(compare):
    """
    Convert a 'compare' function into a 'key' param of 'sorted'
    :param compare: comparison function of format with params '(one, other)' that gives
    1 if one > other, 0 if one == other, -1 if one < other.
    :return: value for 'key' param of 'sorted'
    """

    class Comparison(object):
        def __init__(self, obj, *args):
            self.obj = obj

        def __lt__(self, other):
            return compare(self.obj, other.obj) < 0

        def __gt__(self, other):
            return compare(self.obj, other.obj) > 0

        def __eq__(self, other):
            return compare(self.obj, other.obj) == 0

        def __le__(self, other):
            return compare(self.obj, other.obj) <= 0

        def __ge__(self, other):
            return compare(self.obj, other.obj) >= 0

        def __ne__(self, other):
            return compare(self.obj, other.obj) != 0

    return Comparison


def cmp_by_weight(*weight_sequence, partial=False):
    """
    Returns value for 'key' param of 'sorted' that compares values by its index in weight sequence.
    Uses default compare if values are not in sequence.

    :param weight_sequence: weight sequence, list of values, allow comma-separated string

    >>> sorted('a,r,b,c,d,e'.split(','), key=cmp_by_weight('c,a,d,b'))
    ['c', 'a', 'd', 'b', 'e', 'r']
    >>> sorted([1, 2, 3, 4, 5, 6, 7], key=cmp_by_weight(1, 5, 7))
    [1, 5, 7, 2, 3, 4, 6]
    >>> sorted([{'a': 1}, {'b': 2}, {'c': 5, 'a': 2}], key=cmp_by_weight({'c': 5}, {'b': 2}))
    [{'b': 2}, {'a': 1}, {'c': 5, 'a': 2}]
    >>> sorted([{'a': 1}, {'b': 2}, {'c': 5, 'a': 2}], key=cmp_by_weight({'c': 5}, {'b': 2}, partial=True))
    [{'c': 5, 'a': 2}, {'b': 2}, {'a': 1}]
    """
    if len(weight_sequence) == 1:
        weight_sequence = weight_sequence[0]
    return cmp_for_sorted(compare_by_weight(weight_sequence, partial=partial))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
