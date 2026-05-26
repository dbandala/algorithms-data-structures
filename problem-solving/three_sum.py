# Three sum problem
# Given an array of integers nums and an integer target, return indices of the three numbers such that they add up to target.
# You may assume that each input would have exactly one solution, and you may not use the same element twice.
# You can return the answer in any order.

class Solution(object):
    def threeSum(self, nums, target):
        """
        :type nums: List[int]
        :type target: int
        :rtype: List[int]
        """
        nums.sort()
        result = []
        for i in range(len(nums) - 2):
            if i > 0 and nums[i] == nums[i - 1]: # skip duplicate
                continue
            left, right = i + 1, len(nums) - 1
            while left < right:
                current_sum = nums[i] + nums[left] + nums[right]
                if current_sum < target:
                    left += 1
                elif current_sum > target:
                    right -= 1
                else:
                    result.append([nums[i], nums[left], nums[right]])
                    left += 1
                    right -= 1
                    while left<right and nums[left] == nums[left-1]:
                        left += 1 # skip duplicate
                    while left<right and nums[right] == nums[right+1]:
                        right -= 1 # skip duplicate

        return result

# Test cases
sol = Solution()
print(sol.threeSum([-1,0,1,2,-1,-4], 0)) # [[-1,-1,2],[-1,0,1]]
print(sol.threeSum([0,1,1], 0)) # []
print(sol.threeSum([0,0,0], 0)) # [[0,0,0]]