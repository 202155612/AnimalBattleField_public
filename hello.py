import math

a = (1, 2, 0, 1)
b = (2, 4, 0, 2)

def multi(x: list[float], y: float[float]):
    return sum([a * b for a, b in zip(x, y)])

def abs_vec(x: list[float]):
    return math.sqrt(sum([a*a for a in x]))

def cos(x:list[float], y:float[float]):
    return multi(x, y) / abs_vec(x) / abs_vec(y)

print(cos(a, b))

