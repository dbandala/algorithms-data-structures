// Standard binary search on a sorted array
// Iterative two-pointer approach
// Time complexity:  O(log n)
// Space complexity: O(1)

#include <iostream>
#include <vector>

int binary_search(const std::vector<int>& nums, int target) {
    int left = 0, right = static_cast<int>(nums.size()) - 1;

    while (left <= right) {
        int mid = left + (right - left) / 2;  // avoids integer overflow

        if (nums[mid] == target)
            return mid;
        else if (nums[mid] < target)
            left = mid + 1;   // target must be in right half
        else
            right = mid - 1;  // target must be in left half
    }

    return -1;  // not found
}

int main() {
    std::vector<int> nums = {1, 3, 5, 7, 9, 11, 13, 15};

    std::cout << binary_search(nums, 7)  << "\n";  // 3
    std::cout << binary_search(nums, 1)  << "\n";  // 0
    std::cout << binary_search(nums, 15) << "\n";  // 7
    std::cout << binary_search(nums, 6)  << "\n";  // -1
    return 0;
}
