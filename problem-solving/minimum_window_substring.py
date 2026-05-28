# 76. Minimum Window Substring
# Given two strings s and t of lengths m and n respectively, return the minimum window substring of s such that every character in t (including duplicates) is included in the window. If there is no such substring, return the empty string "".

# The testcases will be generated such that the answer is unique.

# Example 1:
# Input: s = "ADOBECODEBANC", t = "ABC"
# Output: "BANC"
# Explanation: The minimum window substring "BANC" includes 'A', 'B', and 'C' from string t.

# Example 2:
# Input: s = "a", t = "a"
# Output: "a"
# Explanation: The entire string s is the minimum window.

# Example 3:
# Input: s = "a", t = "aa"
# Output: ""
# Explanation: Both 'a's from t must be included in the window.
# Since the largest window of s only has one 'a', return empty string.
 

# Constraints:
# m == s.length
# n == t.length
# 1 <= m, n <= 105
# s and t consist of uppercase and lowercase English letters.


# Follow up: Could you find an algorithm that runs in O(m + n) time?



class Solution(object):
    def minWindow(self, s: str, t: str)-> str:
        """
        type s: string
        type t: string
        rtype: string
        """
        
        # edge cases
        if len(s)==0 or len(t)==0:
            return ""

        if len(s)==len(t) and s==t:
            return s

        m, n = len(s), len(t)

        # what we are expecting in the window
        expected_chars = {}
        for char in t:
            expected_chars[char] = expected_chars.get(char, 0) + 1

        # what we currently have in the windows
        have = {}
        included = 0

        left = 0
        best_len = float('inf')
        best_left = 0

        for right in range(m):
            ch = s[right]
            have[ch] = have.get(ch, 0) + 1

            # did this char satisfy required frequency
            if ch in expected_chars and have[ch] == expected_chars[ch]:
                included +=1

            # if chars are satisfied try to shrink from left
            while included==len(expected_chars):
                # record this window as possible best one
                window = right - left + 1
                if window<best_len:
                    best_len = window
                    best_left = left
                
                # shrink
                left_ch = s[left]
                have[left_ch] -= 1
                # if remove char is needed and no longer satisfy frequency
                if left_ch in expected_chars and have[left_ch]<expected_chars[left_ch]:
                    included -= 1
                left += 1
        
        return "" if best_len==float('inf') else s[best_left:best_left+best_len]

        

sol = Solution()
s = "ADOBECODEBANC"
t = "ABC"
print(sol.minWindow(s, t)) # "BANC"

s = "bbaa"
t = "aba"
print(sol.minWindow(s, t)) # "baa"
