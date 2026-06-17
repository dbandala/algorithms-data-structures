// Maximum subarray sum (Kadane's algorithm)
// Given an array of integers, finds the contiguous subarray with the largest sum.
// Time complexity:  O(n)
// Space complexity: O(1)

#include <iostream>
#include <vector>
#include <algorithm>

int max_subarray(const std::vector<int>& nums) {
    if (nums.empty()) return 0;
    if (nums.size() == 1) return nums[0];

    int max_sum = nums[0], current_sum = nums[0];

    for (int i = 1; i < static_cast<int>(nums.size()); ++i) {
        current_sum = std::max(nums[i], current_sum + nums[i]);
        max_sum = std::max(max_sum, current_sum);
    }

    return max_sum;
}

int main() {
    std::vector<int> input1 = {-2, 1, -3, 4, -1, 2, 1, -5, 4};
    std::cout << "Example 1: Result: " << max_subarray(input1) << "\n";  // 6

    std::vector<int> input2 = {1, 2, 3, -4, 5, 6};
    std::cout << "Example 2: Result: " << max_subarray(input2) << "\n";  // 13
    return 0;
}
