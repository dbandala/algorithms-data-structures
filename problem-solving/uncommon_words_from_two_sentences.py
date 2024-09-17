# Leetcode 884. Uncommon Words from Two Sentences
# A sentence is a string of single-space separated words where each word consists only of lowercase letters.
# A word is uncommon if it appears exactly once in one of the sentences, and does not appear in the other sentence.
# Given two sentences s1 and s2, return a list of all the uncommon words. You may return the answer in any order.

# Example 1:
# Input: s1 = "this apple is sweet", s2 = "this apple is sour"
# Output: ["sweet","sour"]
# Explanation:
# The word "sweet" appears only in s1, while the word "sour" appears only in s2.

# Example 2:
# Input: s1 = "apple apple", s2 = "banana"
# Output: ["banana"]

# Constraints:
# 1 <= s1.length, s2.length <= 200
# s1 and s2 consist of lowercase English letters and spaces.
# s1 and s2 do not have leading or trailing spaces.
# All the words in s1 and s2 are separated by a single space.


class Solution(object):
    def uncommonFromSentences(self, s1, s2):
        """
        :type s1: str
        :type s2: str
        :rtype: List[str]
        """
        # approach: count repeated words in each sentence

        s1_words = []
        s2_words = []

        for word in s1.split():
            s1_words.append(word)

        for word in s2.split():
            s2_words.append(word)

        s1_words_dict = {}
        s2_words_dict = {}

        for word in s1_words:
            if word in s1_words_dict:
                s1_words_dict[word] += 1
            else:
                s1_words_dict[word] = 1
        
        for word in s2_words:
            if word in s2_words_dict:
                s2_words_dict[word] += 1
            else:
                s2_words_dict[word] = 1

        uncommon_words = []
        for word in s1_words_dict:
            if s1_words_dict[word] == 1 and word not in s2_words_dict:
                uncommon_words.append(word)

        for word in s2_words_dict:
            if s2_words_dict[word] == 1 and word not in s1_words_dict:
                uncommon_words.append(word)
        
        return uncommon_words
    
class SolutionWithCounter(object):
    def uncommonFromSentences(self, s1, s2):
        """
        :type s1: str
        :type s2: str
        :rtype: List[str]
        """
        from collections import Counter

        words1 = s1.split()
        words2 = s2.split()

        freq = Counter(words1 + words2)
        
        uncommon_words = [word for word in freq if freq[word] == 1 and (word in words1) ^ (word in words2)]
        
        return uncommon_words
    

# Test cases
sol = Solution()
print(sol.uncommonFromSentences("this apple is sweet", "this apple is sour")) # ["sweet","sour"]
print(sol.uncommonFromSentences("apple apple", "banana")) # ["banana"]

# Time complexity: O(n) where n is the length of the longest sentence