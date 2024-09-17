# Leetcode 1456. Maximum Number of Vowels in a Substring of Given Length
# Given a string s and an integer k, return the maximum number of vowel letters in any substring of s with length k.
# Vowel letters in English are 'a', 'e', 'i', 'o', and 'u'.

# Example 1:
# Input: s = "abciiidef", k = 3
# Output: 3
# Explanation: The substring "iii" contains 3 vowel letters.

# Example 2:
# Input: s = "aeiou", k = 2
# Output: 2
# Explanation: Any substring of length 2 contains 2 vowels.

# Example 3:
# Input: s = "leetcode", k = 3
# Output: 2
# Explanation: "lee", "eet" and "ode" contain 2 vowels.

# Constraints:
# 1 <= s.length <= 105
# s consists of lowercase English letters.
# 1 <= k <= s.length

class NaiveSolution(object):
    def maxVowels(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: int
        """
        # first approach: brute force
        # iterate through the string and check each substring of length k
        # count the number of vowels in each substring
        # return the maximum number of vowels found
        vowels = set('aeiou')

        max_vowels = 0
        for i in range(len(s) - k + 1):
            max_vowels = max(max_vowels, sum(1 for c in s[i:i+k] if c in vowels))

        return max_vowels

class Solution(object):
    def maxVowels(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: int
        """
        # approach: sliding window
        # initialize a window of size k
        # count the number of vowels in the window
        # slide the window to the right by 1
        # update the number of vowels in the window
        # return the maximum number of vowels found
        vowels = set('aeiou')

        max_vowels = 0
        window_vowels = sum(1 for c in s[:k] if c in vowels) # count the number of vowels in the first window

        max_vowels = window_vowels
        for i in range(k, len(s)):
            if s[i-k] in vowels:
                window_vowels -= 1
            if s[i] in vowels:
                window_vowels += 1
            max_vowels = max(max_vowels, window_vowels)

        return max_vowels


class CleverSolution(object):
    def maxVowels(self, s, k):
        """
        :type s: str
        :type k: int
        :rtype: int
        """
        currWindow, currLen, currVowelCount = [], 0, 0
        left = 0
        n = len(s)
        vowels = "AEIOUaeiou"
        ret = 0

        for right in range(n):
            letter = s[right]
            currWindow.append(letter)
            currLen += 1
            if letter in vowels:
                currVowelCount += 1
            
            while currLen > k:
                removedLetter = s[left]
                currWindow.remove(removedLetter)
                currLen -= 1
                if removedLetter in vowels:
                    currVowelCount -= 1
                left += 1
            
            # at this point satisfy the condition
            if currLen == k:
                ret = max(ret, currVowelCount)
        
        return ret


# Test cases
sol = Solution()
print(sol.maxVowels("abciiidef", 3)) # 3
print(sol.maxVowels("aeiou", 2)) # 2
print(sol.maxVowels("leetcode", 3)) # 2

