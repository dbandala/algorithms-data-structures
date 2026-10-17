# Leetcode 930. Binary Subarrays With Sum
# Given a binary array nums and an integer goal, return the number of non-empty subarrays with a sum goal.

# A subarray is a contiguous part of the array.

# Example 1:
# Input: nums = [1,0,1,0,1], goal = 2
# Output: 4
# Explanation: The 4 subarrays are bolded and underlined below:
# [1,0,1,0,1]
# [1,0,1,0,1]
# [1,0,1,0,1]
# [1,0,1,0,1]

# Example 2:
# Input: nums = [0,0,0,0,0], goal = 0
# Output: 15
 
# Constraints:
# 1 <= nums.length <= 3 * 104
# nums[i] is either 0 or 1.
# 0 <= goal <= nums.length


class Solution:
    def numSubarraysWithSum(self, nums: list[int], goal: int) -> int:
        """
        nums: list[list]
        goal: int
        rtype: int
        """
        # Initialize a dictionary to store the frequency of prefix sums
        prefix_sums = {0: 1}
        current_sum = 0
        result = 0

        for num in nums:
            current_sum += num
            if current_sum - goal in prefix_sums:
                result += prefix_sums[current_sum - goal]
            prefix_sums[current_sum] = prefix_sums.get(current_sum, 0) + 1

        # Return the total count of subarrays with the given sum
        return result


# Validation
solution = Solution()
# Test case 1
nums = [1,0,1,0,1]
goal = 2
print(solution.numSubarraysWithSum(nums, goal))  # Output: 4

# Test case 2
nums = [0,0,0,0,0]
goal = 0
print(solution.numSubarraysWithSum(nums, goal))  # Output: 15
