# Leetcode 3. Longest Substring Without Repeating Characters
# Given a string s, find the length of the longest substring without repeating characters.

# Example 1:

# Input: s = "abcabcbb"
# Output: 3
# Explanation: The answer is "abc", with the length of 3.
# Example 2:

# Input: s = "bbbbb"
# Output: 1
# Explanation: The answer is "b", with the length of 1.
# Example 3:

# Input: s = "pwwkew"
# Output: 3
# Explanation: The answer is "wke", with the length of 3.
# Notice that the answer must be a substring, "pwke" is a subsequence and not a substring.
 

# Constraints:
# 0 <= s.length <= 5 * 104
# s consists of English letters, digits, symbols and spaces.


class Solution(object):
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        n = len(s)
        maxLength = 0
        charMap = {}
        left = 0
        
        for right in range(n):
            if s[right] not in charMap or charMap[s[right]] < left:
                charMap[s[right]] = right
                maxLength = max(maxLength, right - left + 1)
            else:
                left = charMap[s[right]] + 1
                charMap[s[right]] = right
        
        print(charMap)
        return maxLength
    
class Solution2(object):
    def lengthOfLongestSubstring(self, s):
        """
        :type s: str
        :rtype: int
        """
        n = len(s)
        maxLength = 1
        substring = ''
        
        # edge case
        if len(s) == 0:
            return 0

        substring += s[0]
        for i in range(1, n):
            if s[i] not in substring:
                substring += s[i]
                maxLength = max(maxLength, len(substring))
            else:
                print(substring)
                substring = substring[substring.index(s[i])+1:] + s[i]
                print(substring)
                print("----")
            
        return maxLength

# Test cases
sol = Solution2()
s = "abcabcbb"
print(sol.lengthOfLongestSubstring(s)) # 3
# s = "bbbbb"
# print(sol.lengthOfLongestSubstring(s)) # 1
# s = "au"
# print(sol.lengthOfLongestSubstring(s)) # 2