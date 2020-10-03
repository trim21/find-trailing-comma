# find-trailing-comma

deprecated, checkout https://github.com/Trim21/pre-commit-hooks

find trailing comma like this in python

```python
a = 1, # not ok
b = 1, # not ok
d = (1, ) # ok
c = {1, 2,
     3, 4}, # not ok
h = ['element'][0, ] # not ok because it's a tuple in `[]`
g = 1, 2, 3, # ok, not a single element

```

I don't mean to make it a tuple, I just add a `,` by accident.
