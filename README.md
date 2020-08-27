# shuff-utils
General-purpose classes and functions.

## Installation

```bash
pip install -i shuff-utils
```

## DottedDict
`dict` that allows you to call its keys with the dot.

```python
d = {'a': 'test'}
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

## Other functions
Other functions is not described yet. You can see them in the corresponding modules. 
Some of them have descriptions in their docstrings.

## Naming
The package is named after Slipknot's song. Thanks to the band, it helps a lot.