from string import Formatter

__all__ = ['f']


class FormatTuple(tuple):
    def __getitem__(self, key):
        if key + 1 > len(self):
            return "{}"
        return tuple.__getitem__(self, key)


class FormatDict(dict):
    def __missing__(self, key):
        return "{" + key + "}"


def f(string, *args, **kwargs):
    """
    String safe substitute format method.
    If you pass extra keys they will be ignored.
    If you pass incomplete substitute map, missing keys will be left unchanged.
    :param string:
    :param kwargs:
    :return:

    >>> f('{foo} {bar}', foo="FOO")
    'FOO {bar}'
    >>> f('{} {bar}', 1)
    '1 {bar}'
    >>> f('{foo} {}', 1)
    '{foo} 1'
    >>> f('{foo} {} {bar} {}', '|', bar='BAR')
    '{foo} | BAR {}'
    >>> f('{foo} {bar}', foo="FOO", bro="BRO")
    'FOO {bar}'
    """
    formatter = Formatter()
    args_mapping = FormatTuple(args)
    mapping = FormatDict(kwargs)
    return formatter.vformat(string, args_mapping, mapping)


if __name__ == "__main__":
    def _test_module():
        import doctest
        result = doctest.testmod()
        if not result.failed:
            print(f"{result.attempted} passed and {result.failed} failed.\nTest passed.")

    _test_module()
