# Tenemos una función que recibe un entero y devuelve un entero
# Fib(0) -> 0 
# Fib(1) -> 1 
# Fib(n) -> Fib(n-1) + Fib(n-2)
# 0 1 2 3 4 5 6 7  8  9  10 11 // Entradas
# 0 1 1 2 3 5 8 13 21 34 55 89 // Salidas


fib_values = [0, 1]

def fib_recursive(n):
    # base cases
    if n<2:
        return n
    return fib_recursive(n-1)+fib_recursive(n-2)


def fib_iterative(n):
    if n<2:
        return fib_values[n]
    # iterative solution
    for i in range(2, n+1, 1):
        fib_values.append(fib_values[i-1] + fib_values[i-2])
    # return value
    return fib_values[n]


def fib_memoization(n):
    if n<2:
        return n
    # memoization
    if len(fib_values)>=n:
        return fib_values[n-1]
    else:
        fib_values.append(fib_memoization(n-1)+fib_memoization(n-2))
        return fib_values[n-1]


print(fib_recursive(10))
print(fib_memoization(10))