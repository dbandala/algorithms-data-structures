# Leetcode 5. Longest Palindromic Substring
# Given a string s, return the longest palindromic substring in s.
# Write a function in Python that takes a string as input and returns the longest palindromic substring within the string. For example, given the input "babad", the function should return "bab" or "aba". If there are multiple solutions, return any of them.

# The function signature is:
def longest_palindromic_substring(s: str) -> str:
    if len(s) == 0:
        return ""
    if len(s) == 1:
        return s
    for i in range(len(s)):
        for j in range(i+1, len(s)):
            if s[i:j+1] == s[i:j+1][::-1]:
                return s[i:j+1]
            

def longest_palindromic_substring(s: str) -> str:
    def expand_around_center(left, right):
        while left >= 0 and right < len(s) and s[left] == s[right]:
            left -= 1
            right += 1
        return s[left + 1:right]

    longest = ""
    for i in range(len(s)):
        odd_palindrome = expand_around_center(i, i)
        even_palindrome = expand_around_center(i, i + 1)
        longest = max(longest, odd_palindrome, even_palindrome, key=len)
    return longest

# For example, longest_palindromic_substring("babad") should return "bab" or "aba".
print(longest_palindromic_substring("babad")) # bab or aba
print(longest_palindromic_substring("cbbd")) # bb
print(longest_palindromic_substring("a")) # a


