# 1143. Longest Common Subsequence
# Given two strings text1 and text2, return the length of their longest common subsequence. If there is no common subsequence, return 0.

# A subsequence of a string is a new string generated from the original string with some characters (can be none) deleted without changing the relative order of the remaining characters.

# For example, "ace" is a subsequence of "abcde".
# A common subsequence of two strings is a subsequence that is common to both strings.

# Example 1:
# Input: text1 = "abcde", text2 = "ace" 
# Output: 3  
# Explanation: The longest common subsequence is "ace" and its length is 3.

# Example 2:
# Input: text1 = "abc", text2 = "abc"
# Output: 3
# Explanation: The longest common subsequence is "abc" and its length is 3.

# Example 3:
# Input: text1 = "abc", text2 = "def"
# Output: 0
# Explanation: There is no such common subsequence, so the result is 0.
 
# Constraints:
# 1 <= text1.length, text2.length <= 1000
# text1 and text2 consist of only lowercase English characters.



class Solution(object):
    def longestCommonSubsequence(self, text1, text2):
        """
        Return the length of the longest common subsequence of text1 and text2.

        Uses bottom-up dynamic programming: dp[i][j] is the LCS length for
        text1[:i] and text2[:j]. When characters match, extend the diagonal;
        otherwise take the best of skipping one character from either string.

        :type text1: str
        :type text2: str
        :rtype: int
        """
        if not text1 or not text2:
            return 0

        m, n = len(text1), len(text2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if text1[i - 1] == text2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1] + 1
                else:
                    dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

        return dp[m][n]

# test cases
sol = Solution()
print(sol.longestCommonSubsequence("abcde", "ace"))
print(sol.longestCommonSubsequence("abc", "abc"))
print(sol.longestCommonSubsequence("abc", "def"))


