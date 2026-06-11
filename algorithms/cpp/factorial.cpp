// Recursive factorial
// Time complexity:  O(n)
// Space complexity: O(n) call stack

#include <iostream>

long long calculate_factorial(int n) {
    if (n == 0) return 1;
    return n * calculate_factorial(n - 1);
}

int main() {
    std::cout << calculate_factorial(5)  << "\n";  // 120
    std::cout << calculate_factorial(10) << "\n";  // 3628800
    return 0;
}
