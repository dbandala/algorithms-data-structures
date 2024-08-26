# Leetcode 169. Majority Element
# Given an array nums of size n, return the majority element.
# The majority element is the element that appears more than ⌊n / 2⌋ times. You may assume that the majority element always exists in the array.

# Example 1:
# Input: nums = [3,2,3]
# Output: 3

# Example 2:
# Input: nums = [2,2,1,1,1,2,2]
# Output: 2
 
# Constraints:
# n == nums.length
# 1 <= n <= 5 * 104
# -109 <= nums[i] <= 109
 
# Follow-up: Could you solve the problem in linear time and in O(1) space?

class Solution(object):
    def majorityElement(self, nums):
        """
        :type nums: List[int]
        :rtype: int
        """
        n = len(nums)
        majority_limit = n//2
        # edge scenarios
        if n==0:
            return None
        if n==1:
            return nums[0]
        
        # create a dictionary to store the count of each element
        count_dict = {}
        for num in nums:
            if num in count_dict:
                count_dict[num] += 1
            else:
                count_dict[num] = 1
            if count_dict[num] > majority_limit:
                return num
        return None
    
class Solution2:
    def majorityElement(self, nums):
        nums.sort()
        n = len(nums)
        return nums[n//2]
        

# The time complexity is O(n) where n is the number of elements in the array. The space complexity is O(n) because of the dictionary.

# Test cases
sol = Solution()
nums = [3,2,3]
print(sol.majorityElement(nums)) # 3





