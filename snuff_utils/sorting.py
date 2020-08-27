#!/usr/bin/env python3
# coding=utf-8


def default_cmp(one, other):
    """
    Default comparison function.
    Gives 1 if one > other, 0 if one == other, -1 if one < other.
    """
    if one > other:
        return 1
    elif one < other:
        return -1
    return 0


def compare_by_weight(*weight_sequence):
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
        one_in = one in weight_sequence
        other_in = other in weight_sequence
        if one_in and other_in:
            return weight_sequence.index(one) - weight_sequence.index(other)
        elif one_in:
            return -1
        elif other_in:
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


def cmp_by_weight(*weight_sequence):
    """
    Returns value for 'key' param of 'sorted' that compares values by its index in weight sequence.
    Uses default compare if values are not in sequence.

    :param weight_sequence: weight sequence, list of values, allow comma-separated string

    >>> sorted('a,r,b,c,d,e'.split(','), key=cmp_by_weight('c,a,d,b'))
    ['c', 'a', 'd', 'b', 'e', 'r']
    >>> sorted([1, 2, 3, 4, 5, 6, 7], key=cmp_by_weight(1, 5, 7))
    [1, 5, 7, 2, 3, 4, 6]
    """
    if len(weight_sequence) == 1:
        weight_sequence = weight_sequence[0]
    return cmp_for_sorted(compare_by_weight(weight_sequence))


if __name__ == "__main__":
    import doctest
    doctest.testmod()
