# find-trailing-comma

find trailing comma like this in python

```python
a = 1, # not ok
b = 1, # not ok
d = (1, ) # ok
c = {1, 2,
     3, 4}, # not ok

```

I don't mean to make it a tuple, I just add a `,` by accident.