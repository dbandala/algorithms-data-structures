# Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.
# You may assume that each input would have exactly one solution, and you may not use the same element twice.
# You can return the answer in any order.

class Solution(object):
    def twoSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        if len(nums)==0:
            return []
        if len(nums)==1:
            return [0] if nums[0]==target else []
        
        # create a dictionary to store the index of the numbers
        num_dict = {}
        for i, num in enumerate(nums):
            if num in num_dict:
                return [num_dict[num], i]
            num_dict[target-num] = i
        return []

# Test cases
sol = Solution()
print(sol.twoSum([2,7,11,15], 9)) # [0,1]
print(sol.twoSum([3,2,4], 6)) # [1,2]
