a = 1,
b = 1,
d = (1, )
c = {1, 2, 3, 4},
e = ("abc")
f = ("abc", )
g = (1, ),

try:
    h = [[1], [2]][1, ]
except TypeError:
    pass


class A:
    b = 3,


print(A.b, type(A.b))
