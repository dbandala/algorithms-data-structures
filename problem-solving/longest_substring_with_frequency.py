# Given a string s and an integer k, return the length of the longest substring of s such that the frequency of each character in this substring is greater than or equal to k.
# If no such substring exists, return 0.
 
# Example 1:
 
# Input:  s = "aaabb", k = 3
# Output: 3
# Explanation: The longest substring is "aaa", as 'a' is repeated 3 times.
 
# Example 2:
 
# Input:  s = "ababbc", k = 2
# Output: 5
# Explanation: The longest substring is "ababb", as 'a' is repeated 2 times and 'b' is repeated 3 times.
 
# Constraints
 
# 1 <= s.length <= 10^4
# s consists of only lowercase English letters.
# 1 <= k <= 10^5


class Solution:
    def longestSubstring(self, s: str, k: int) -> int:
        def helper(start: int, end: int) -> int:
            if end - start < k:
                return 0
            
            count = {}
            for i in range(start, end):
                count[s[i]] = count.get(s[i], 0) + 1
            
            for mid in range(start, end):
                if count[s[mid]] < k:
                    mid_next = mid + 1
                    while mid_next < end and count[s[mid_next]] < k:
                        mid_next += 1
                    return max(helper(start, mid), helper(mid_next, end))
            
            return end - start
        
        return helper(0, len(s))
# Test cases
sol = Solution()
s = "aaabb"
k = 3
print(sol.longestSubstring(s, k))  # Output: 3
s = "ababbc"
k = 2
print(sol.longestSubstring(s, k))  # Output: 5
