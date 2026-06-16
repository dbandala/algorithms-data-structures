// Fibonacci using recursion + dynamic programming (memoization)
// Time complexity:  O(n)
// Space complexity: O(n)

#include <iostream>
#include <unordered_map>

std::unordered_map<int, long long> memo;

long long fibonacci(int n) {
    if (n == 0 || n == 1) return n;
    auto it = memo.find(n);
    if (it != memo.end()) return it->second;
    memo[n] = fibonacci(n - 1) + fibonacci(n - 2);
    return memo[n];
}

int main() {
    std::cout << fibonacci(10) << "\n";  // 55
    std::cout << fibonacci(20) << "\n";  // 6765

    std::cout << "\nUsing dynamic programming\n";
    std::cout << fibonacci(10) << "\n";  // 55
    std::cout << fibonacci(20) << "\n";  // 6765
    return 0;
}
