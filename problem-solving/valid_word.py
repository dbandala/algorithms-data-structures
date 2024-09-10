# Leetcode 3136. Valid Word
# A word is considered valid if:
# It contains a minimum of 3 characters.
# It contains only digits (0-9), and English letters (uppercase and lowercase).
# It includes at least one vowel.
# It includes at least one consonant.
# You are given a string word.
# Return true if word is valid, otherwise, return false.

# Notes:
# 'a', 'e', 'i', 'o', 'u', and their uppercases are vowels.
# A consonant is an English letter that is not a vowel.

# Example 1:
# Input: word = "234Adas"
# Output: true
# Explanation:
# This word satisfies the conditions.

# Example 2:
# Input: word = "b3"
# Output: false
# Explanation:
# The length of this word is fewer than 3, and does not have a vowel.

# Example 3:
# Input: word = "a3$e"
# Output: false
# Explanation:
# This word contains a '$' character and does not have a consonant.

 

# Constraints:
# 1 <= word.length <= 20
# word consists of English uppercase and lowercase letters, digits, '@', '#', and '$'.


class Solution(object):
    def isValid(self, word):
        """
        :type word: str
        :rtype: bool
        """
        # approach: create a set for vowels and consonants
        # create a counter for vowels and consonants
        # iterate through the word and check if the character is a vowel or consonant
        # increment the counter for vowels or consonants
        # if the counter for vowels and consonants is greater than 0, return True

        if len(word) < 3:
            return False
        
        vowels = set('aeiouAEIOU')
        consonants = set('bcdfghjklmnpqrstvwxyzBCDFGHJKLMNPQRSTVWXYZ')
        allowed = vowels.union(consonants).union(set('0123456789'))

        has_vowels = False
        has_consonants = False
        all_allowed = True

        for c in word:
            if c in vowels:
                has_vowels = True
            if c in consonants:
                has_consonants = True
            if c not in allowed:
                all_allowed = False
                break

        return has_vowels and has_consonants and all_allowed
    

# Test cases
sol = Solution()
print(sol.isValid("234Adas")) # True
print(sol.isValid("b3")) # False
print(sol.isValid("a3$e")) # False
print(sol.isValid("ae")) # False
print(sol.isValid("aei")) # False
print(sol.isValid("aeiou")) # False
print(sol.isValid("aeiouAEIOU")) # False
print(sol.isValid("aeiouAEIOU1")) # False
print(sol.isValid("aeiouAEIOU1$")) # False

