# Leetcode 525. Contiguous Array
# Given a binary array nums, return the maximum length of a contiguous subarray with an equal number of 0 and 1.

# Example 1:
# Input: nums = [0,1]
# Output: 2
# Explanation: [0, 1] is the longest contiguous subarray with an equal number of 0 and 1.

# Example 2:
# Input: nums = [0,1,0]
# Output: 2
# Explanation: [0, 1] (or [1, 0]) is a longest contiguous subarray with equal number of 0 and 1.

# Example 3:
# Input: nums = [0,1,1,1,1,1,0,0,0]
# Output: 6
# Explanation: [1,1,1,0,0,0] is the longest contiguous subarray with equal number of 0 and 1.
 
# Constraints:
# 1 <= nums.length <= 105
# nums[i] is either 0 or 1.



from collections import defaultdict


class Solution(object):
    def findMaxLength(self, nums):
        """
            nums: list[int]
        """
        # subarray_sum(j+1, i) = prefixSum[i] - prefixSum[j]
        first_seen = {0: -1}
        balance = 0
        max_len = 0

        for i, num in enumerate(nums):
            balance += 1 if num==1 else -1
            if balance in first_seen:
                max_len = max(max_len, i-first_seen[balance])
            else:
                first_seen[balance] = i

        return max_len


class OptimalSolution:
    def findMaxLength(self, nums: list[int]) -> int:
        if len(nums) == 1: return 0
        
        prefix_sums = [0]
        total = 0
        for num in nums:
            if num == 1:
                total += 1
            else:
                total -= 1
            prefix_sums.append(total)

        res = 0
        indices = defaultdict()

        for i, num in enumerate(prefix_sums):
            if num not in indices.keys():
                indices[num] = i             
            else:
                res = max(res, i - indices[num])

        return res

"""
- given binary array, return max length of subarray with equal 0s and 1s

- brute force: check every single length -> TLE O(n * n!)
  - optimization 1: skip check if start-end less than res -> still TLE
  - optimization 2: skip if difference bigger than number of remaining nums to check -> still TLE

- after looking at hints:
  - use hash table and prefix sum
  - idea -> TLE O(n^2) (n^2 checks for ranges)
    - change all 0s to -1
    - store precomputed array
    - check all ranges nums[r] - nums[l-1]
  - idea2:
    - check when first and last sums occur
    - return indices with largest gap
"""


# Validation
solution = Solution()
print(solution.findMaxLength([0,1]))  # Output: 2
print(solution.findMaxLength([0,1,0]))  # Output: 2
print(solution.findMaxLength([0,1,1,1,1,1,0,0,0]))  # Output: 6

            





