# find-trailing-comma

find trailing comma like this in python

```python
a = 1, # not ok
b = 1, # not ok
d = (1, ) # ok
c = {1, 2,
     3, 4}, # not ok
h = ['element'][0, ] # not ok because it's a tuple in `[]`


```

I don't mean to make it a tuple, I just add a `,` by accident.

Just add this to your  `.pre-commit-config.yaml`

```yaml
  - repo: https://github.com/Trim21/find-trailing-comma
    rev: v0.0.1
    hooks:
      - id: find-trailing-comma
```