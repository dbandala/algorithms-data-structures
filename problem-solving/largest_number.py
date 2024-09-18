# Leetcode 179. Largest Number
# Given a list of non-negative integers nums, arrange them such that they form the largest number and return it.
# Since the result may be very large, so you need to return a string instead of an integer.

# Example 1:
# Input: nums = [10,2]
# Output: "210"

# Example 2:
# Input: nums = [3,30,34,5,9]
# Output: "9534330"

# Constraints:
# 1 <= nums.length <= 100
# 0 <= nums[i] <= 109


class Solution(object):
    def largestNumber(self, nums):
        """
        :type nums: List[int]
        :rtype: str
        """
        # Convert each integer to a string
        num_strings = [str(num) for num in nums]

        print(num_strings)

        # Sort strings based on concatenated values
        num_strings.sort(key=lambda a: a * 10, reverse=True)

        num_strings_x10 = [num*10 for num in num_strings]

        print(num_strings)
        print(num_strings_x10)

        # Handle the case where the largest number is zero
        if num_strings[0] == "0":
            return "0"

        # Concatenate sorted strings to form the largest number
        return "".join(num_strings)
    

# test cases to validate the solution
s = Solution()
print(s.largestNumber([10,2])) # "210"
print(s.largestNumber([3,30,34,5,9])) # "9534330"
print(s.largestNumber([0,0])) # "0"
print(s.largestNumber([0,0,0])) # "0"
print(s.largestNumber([0,0,1])) # "100"

