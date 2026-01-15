# 402. Remove K Digits

# Given string num representing a non-negative integer num, and an integer k, return the smallest possible integer after removing k digits from num.

# Example 1:
# Input: num = "1432219", k = 3
# Output: "1219"
# Explanation: Remove the three digits 4, 3, and 2 to form the new number 1219 which is the smallest.

# Example 2:
# Input: num = "10200", k = 1
# Output: "200"
# Explanation: Remove the leading 1 and the number is 200. Note that the output must not contain leading zeroes.

# Example 3:
# Input: num = "10", k = 2
# Output: "0"
# Explanation: Remove all the digits from the number and it is left with nothing which is 0.

# Constraints:
# 1 <= k <= num.length <= 105
# num consists of only digits.
# num does not have any leading zeros except for the zero itself.

class Solution:
    def removeKdigits(self, num: str, k: int) -> str:
        stack = []
        for digit in num:
            while k > 0 and stack and stack[-1] > digit:
                stack.pop()
                k -= 1
            stack.append(digit)
        # If k is still greater than 0, remove from the end
        stack = stack[:-k] if k else stack
        # Remove leading zeros
        result = ''.join(stack).lstrip('0')
        return result if result else "0"
    
class NaiveSolution:
    def removeKdigits(self, num: str, k: int) -> str:
        num_list = list(num)
        for _ in range(k):
            i = 0
            while i < len(num_list) - 1 and num_list[i] <= num_list[i + 1]:
                i += 1
            num_list.pop(i)
        # Remove leading zeros
        result = ''.join(num_list).lstrip('0')
        return result if result else "0"
    

# Test cases
sol = Solution()
num = "1432219"
k = 3
print(sol.removeKdigits(num, k))  # Output: "1219"
num = "10200"
k = 1
print(sol.removeKdigits(num, k))  # Output: "200"
num = "99"
k = 2
print(sol.removeKdigits(num, k))  # Output: "0"
num = "14"
k = 1
print(sol.removeKdigits(num, k))  # Output: "1"
