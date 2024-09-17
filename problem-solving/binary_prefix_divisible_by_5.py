# Leetcode 1018. Binary Prefix Divisible By 5
# You are given a binary array nums (0-indexed).
# We define xi as the number whose binary representation is the subarray nums[0..i] (from most-significant-bit to least-significant-bit).
# For example, if nums = [1,0,1], then x0 = 1, x1 = 2, and x2 = 5.
# Return an array of booleans answer where answer[i] is true if xi is divisible by 5.

# Example 1:
# Input: nums = [0,1,1]
# Output: [true,false,false]
# Explanation: The input numbers in binary are 0, 01, 011; which are 0, 1, and 3 in base-10.
# Only the first number is divisible by 5, so answer[0] is true.

# Example 2:
# Input: nums = [1,1,1]
# Output: [false,false,false]

# Constraints:
# 1 <= nums.length <= 105
# nums[i] is either 0 or 1.


class Solution(object):
    def prefixesDivBy5(self, nums):
        """
        :type nums: List[int]
        :rtype: List[bool]
        """
        # approach: keep track of the current number and check if it is divisible by 5
        result = []
        current_num = 0
        for num in nums:
            current_num = (current_num << 1) + num
            result.append(current_num % 5 == 0)

        return result
    
class CleverSolution(object):
    def prefixesDivBy5(self, nums):
        """
        :type nums: List[int]
        :rtype: List[bool]
        """
        j=[]
        b=""
        for i in nums:
            b+=str(i)
            if(int(b,2)%5==0):
                j.append(True)
            else:
                j.append(False)
        return j
    

# Test cases
sol = Solution()
print(sol.prefixesDivBy5([0,1,1])) # [True, False, False]
print(sol.prefixesDivBy5([1,1,1])) # [False, False, False]
print(sol.prefixesDivBy5([1,1,1,1,1])) # [False, False, False, False, False]


