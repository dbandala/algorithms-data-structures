# implementation of fibonacci series using recursion

def fibonacci(n):
    if n == 0 or n == 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# using dynamic programming
memo = [None] * 100
def fibonacci(n):
    if memo[n] is not None:
        return memo[n]
    if n == 0 or n == 1:
        return n
    memo[n] = fibonacci(n-1) + fibonacci(n-2)
    return memo[n]

# Test cases
print(fibonacci(10)) # 55
print(fibonacci(20)) # 6765

# Time complexity: O(n)
# Space complexity: O(n)
# where n is the number of elements in the fibonacci series
print("")
print("Using dynamic programming")
print(fibonacci(10)) # 55
print(fibonacci(20)) # 6765