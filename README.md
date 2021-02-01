# shuff-utils
General-purpose classes and functions.

## Installation

```bash
pip install -i shuff-utils
```

## DottedDict
`dict` that allows you to call its keys with the dot.

```python
d = DottedDict({'a': 'test'})
d.a
# 'test'
d = DottedDict(a='test')
d.a
# 'test'
```

## Timer
Class for measuring an execution time. 

```python    
# Init and set name of the whole period
timer = Timer('whole_period')
# Start custom measurement
timer.add_point('first block')
...
timer.add_point('second block')
...
# Stop custom measurement
timer.stop('first block')
timer.add_point('third block')
...
# Stop all the intervals and print summary details
timer.stop().print_summary()
# [2017-10-09 17:06:10 INFO] PROFILING: whole_period: 5000, first block: 3000, second block: 2000, third block: 2000
```

## Flask functions

### token_required - Bearer token decorator

Decorator that checks Bearer (static) Authorization token

Usage:
```python
import os

from dotenv import load_dotenv
from flask_restful import Resource
from snuff_utils.flask_decorators import token_required

# Get token from .env file
load_dotenv()
MY_TOKEN = os.getenv('MY_TOKEN', '')


class CallbackEvents(Resource):

    @token_required(MY_TOKEN)
    def post(self):
        # some code here
        return {}
```

## date and time

### localize

Converts naive time to local time.

```python
localize(some_date, new_timezone='UTC', force=False)
```
 
`force` param forces timezone replacement to new_timezone.

```python
from datetime import datetime
from pytz import UTC
date = datetime(2019, 12, 12, 2, 34)
localize(date)
# datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<UTC>)
localize(date, UTC)
# datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<UTC>)
localize(date, 'Europe/Samara')
# datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<DstTzInfo 'Europe/Samara' LMT+3:20:00 STD>)
date = localize(date, UTC)
localize(date, 'Europe/Samara')
# datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<UTC>)
localize(date, 'Europe/Samara', force=True)
# datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<DstTzInfo 'Europe/Samara' LMT+3:20:00 STD>)
```

### as_timezone

Returns the same UTC time as self, but in as_tz’s local time. Inherits `datetime.astimezone` behaviour.

```python
as_timezone(source_date, as_tz='UTC', source_tz_by_default='UTC')
```
    
```python
>>> from datetime import datetime
>>> from pytz import UTC
>>> date = datetime(2019, 12, 12, 2, 34)
>>> as_timezone(date, UTC)
datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<UTC>)
>>> as_timezone(date, 'Europe/Samara')
datetime.datetime(2019, 12, 12, 6, 34, tzinfo=<DstTzInfo 'Europe/Samara' +04+4:00:00 STD>)
>>> as_timezone(date, 'Europe/Samara', source_tz_by_default='Europe/Samara')
datetime.datetime(2019, 12, 12, 2, 34, tzinfo=<DstTzInfo 'Europe/Samara' +04+4:00:00 STD>)
```

## Input/output functions

### sv_import

Imports csv or other -sv files.

Let's say you have csv file with two columns and two rows of values, columns are separated by semicolon (;). Like this:
```
ID;Name
123;Jimmy
456;Andrew
```

```python
from snuff_utils.io_utils import sv_import
rows = sv_import('/path/to/sv_file.csv', sep=';')
for row in rows:
    print(row)
# {'ID': '123', 'Name': 'Jimmy'}
# {'ID': '456', 'Name': 'Andrew'}
```
Function returns a generator. To get list of dicts convert result to a list:
```python
rows = sv_import('/path/to/sv_file.csv', sep=';')
data = list(rows)
# [
#   {'first column': 'first row value', 'second column': 'first row value'},
#   {'first column': 'second row value', 'second column': 'second row value'}
# ]
```

## Sorting

### cmp_by_weight

Comparison by weight for `sorted`.

Allow sorting by dicts. If dicts are not in a weight sequence, their weights are equal. 
`partial` defines if a dictionary from a list must match for all keys (or only for comparison dict keys).

```python
>>> sorted('a,r,b,c,d,e'.split(','), key=cmp_by_weight('c,a,d,b'))
['c', 'a', 'd', 'b', 'e', 'r']

>>> sorted([1, 2, 3, 4, 5, 6, 7], key=cmp_by_weight(1, 5, 7))
[1, 5, 7, 2, 3, 4, 6]

>>> my_list = [{'a': 1}, {'b': 2}, {'c': 5, 'a': 2}]
>>> sorted(my_list, key=cmp_by_weight({'c': 5}, {'b': 2}))
[{'b': 2}, {'a': 1}, {'c': 5, 'a': 2}]

>>> sorted(my_list, key=cmp_by_weight({'c': 5}, {'b': 2}, partial=True))
[{'c': 5, 'a': 2}, {'b': 2}, {'a': 1}]
```

## Universal

### popattr

`popattr(obj, attr, default)`

Alias for sequential calls of `getattr` and `delattr`. Similar to dict.pop. Default value is `None`.

```python
>>> class A: pass
>>> a = A()
>>> setattr(a, 'some', 5)
>>> popattr(a, 'some')
5
>>> popattr(a, 'some')

>>> popattr(a, 'some', 'default')
'default'
```

## Other functions
Other functions is not described yet. You can see them in the corresponding modules. 
Some of them have descriptions in their docstrings.

## Changelog

### 1.0.9 (2021-02-01)

- Added `partial` sorting for list of dicts (`cmp_by_weight`).

### 1.0.8 (2020-12-09)

- Added `append_to_list` and `add_to_set` params to `group_list_of_dicts` function.

### 1.0.7

- Added `popattr` function.

### 1.0.6

- Added `sv_import` documentation.

### 1.0.5

- Fixed `date_and_time.localize` behaviour for non-pytz timezones. Added tests.

### 1.0.4

- Added `extended_filter` parameter to `marshmallow_extras.convert_to_instance`.

### 1.0.3

- `marshmallow_extras.convert` now can take many functions as arguments. 
- Added `marshmallow_extras.convert_items` function. 
- Added `marshmallow_extras.apply` function - with it `deserialize` parameter can apply many functions to value.

### 1.0.2

- Project directories included.

### 1.0.1

- Updated `token_required` decorator.

### 1.0.0

- Init version.

## Naming
The package is named after Slipknot's song. Thanks to the band, it helps a lot.