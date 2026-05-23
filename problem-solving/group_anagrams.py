# Group Anagrams
# Given an array of strings strs, group the anagrams together. You can return the answer in any order.
# An Anagram is a word or phrase formed by rearranging the letters of a different word or phrase, typically using all the original letters exactly once.

# complexity: O(n * k * log(k))
class Solution(object):
    def groupAnagrams(self, strs):
        """
        :type strs: List[str]
        :rtype: List[List[str]]
        """
        anagrams = {}
        for str in strs:
            sorted_str = ''.join(sorted(str), key=lambda x: x)
            if sorted_str in anagrams:
                anagrams[sorted_str].append(str)
            else:
                anagrams[sorted_str] = [str]
        return list(anagrams.values())

# Test cases
sol = Solution()
print(sol.groupAnagrams(["eat","tea","tan","ate","nat","bat"])) # [["eat","tea","ate"],["tan","nat"],["bat"]]
print(sol.groupAnagrams([""])) # [[""]]
print(sol.groupAnagrams(["a"])) # [["a"]]