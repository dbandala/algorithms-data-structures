# Montecarlo algorithm
# The Monte Carlo algorithm is a statistical technique that allows you to make numerical estimates using random sampling.
# It is often used in scenarios where it is difficult or impossible to compute an exact result.

# Example use cases include:
# 1. Estimating the value of π (pi) by randomly sampling points in a square and counting how many fall within a quarter circle.
# 2. Simulating complex systems, such as weather patterns or stock market fluctuations, to understand their behavior over time.
# 3. Solving optimization problems by exploring a large search space and identifying promising regions through random sampling.

from random import random


class MonteCarlo:
    def __init__(self, num_samples):
        self.num_samples = num_samples

    def estimate_pi(self):
        inside_circle = 0
        for _ in range(self.num_samples):
            x = random.uniform(-1, 1) # type: ignore
            y = random.uniform(-1, 1) # type: ignore
            if x**2 + y**2 <= 1:
                inside_circle += 1
        return (inside_circle / self.num_samples) * 4


# Monte Carlo integration

    def integrate(self, func, a, b):
        total = 0
        for _ in range(self.num_samples):
            x = random.uniform(a, b) # type: ignore
            total += func(x)
        return (b - a) * total / self.num_samples
    