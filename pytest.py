a = [1, 2, 3]
b = ["hey", "yo", "friend"]
f = [.1, .2, .3]
LL = [a, b, f]

LT = list(zip(*LL))

print(LT)