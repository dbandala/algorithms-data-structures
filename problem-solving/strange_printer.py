# Leetcode 664. Strange Printer
# There is a strange printer with the following two special properties:
# The printer can only print a sequence of the same character each time.
# At each turn, the printer can print new characters starting from and ending at any place and will cover the original existing characters.
# Given a string s, return the minimum number of turns the printer needed to print it.

# Example 1:
# Input: s = "aaabbb"
# Output: 2
# Explanation: Print "aaa" first and then print "bbb".

# Example 2:
# Input: s = "aba"
# Output: 2
# Explanation: Print "aaa" first and then print "b" from the second place of the string, which will cover the existing character 'a'.
 
# Constraints:
# 1 <= s.length <= 100
# s consists of lowercase English letters.

class Solution(object):
    def strangePrinter(self, s):
        """
        :type s: str
        :rtype: int
        """
        # verify edge cases
        if len(s)==0:
            return 0
        if len(s)==1:
            return 1
        
        n = len(s)
        dp = [[0]*(n+1) for _ in range(n+1)]

        for l in range(n - 1, -1, -1):
            for r in range(l, n):
                res = 1 + dp[l + 1][r]
                for i in range(l + 1, r + 1):
                    if s[l] == s[i]:
                        res = min(res, dp[l][i - 1] + dp[i + 1][r])
                dp[l][r] = res
        
        print(dp)
        return dp[0][n - 1]
    

# Time complexity: O(n^3)
# Space complexity: O(n^2)

# Test cases
# s = "aaabbb"
# s = "aba"
s = "abac"
sol = Solution()
print(sol.strangePrinter(s))

        





