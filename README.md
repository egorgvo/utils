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

## Other functions
Other functions is not described yet. You can see them in the corresponding modules. 
Some of them have descriptions in their docstrings.

## Changelog

### 1.0.3

- `marshmallow_extras.convert` now can take many functions as arguments. 
- Added `marshmallow_extras.convert_items` function. 
- Added `marshmallow_extras.apply` function - with it `deserialize` parameter can apply many functions to value.

## Naming
The package is named after Slipknot's song. Thanks to the band, it helps a lot.