# 686. Repeated String Match

# Given two strings a and b, return the minimum number of times you should repeat string a so that string b is a substring of it. If it is impossible for b​​​​​​ to be a substring of a after repeating it, return -1.
# Notice: string "abc" repeated 0 times is "", repeated 1 time is "abc" and repeated 2 times is "abcabc".

# Example 1:
# Input: a = "abcd", b = "cdabcdab"
# Output: 3
# Explanation: We return 3 because by repeating a three times "abcdabcdabcd", b is a substring of it.

# Example 2:
# Input: a = "a", b = "aa"
# Output: 2

# Constraints:
# 1 <= a.length, b.length <= 104
# a and b consist of lowercase English letters.

class Solution:
    def repeatedStringMatch(self, a: str, b: str) -> int:
        if len(a) == 0 or len(b) == 0:
            return -1
        repeat_count = -(-len(b) // len(a))  # Ceiling division to get minimum repeats
        repeated_a = a * repeat_count
        if b in repeated_a:
            return repeat_count
        if b in repeated_a + a:
            return repeat_count + 1
        return -1
    

# Test cases
sol = Solution()
a = "abcd"
b = "cdabcdab"
print(sol.repeatedStringMatch(a, b))  # Output: 3

a = "a"
b = "aa"
print(sol.repeatedStringMatch(a, b))  # Output: 2

# difficult test case
a = "abc"
b = "cabcabca"
print(sol.repeatedStringMatch(a, b))  # Output: 4

# b wraps around a in a way that requires many repetitions and uses characters
# from the very end and very beginning of a across multiple cycles
a = "abcde"
b = "deabcdeabcdeabc"
print(sol.repeatedStringMatch(a, b))  # Output: 4

# b consists entirely of a single character that repeats more times than a contains it,
# requiring many repetitions; impossible case where b has a character not in a
a = "aabaab"
b = "aabaabaabaabaab"
print(sol.repeatedStringMatch(a, b))  # Output: 3

# edge cases
a = ""
b = "a"
print(sol.repeatedStringMatch(a, b))  # Output: -1

a = "a"
b = ""
print(sol.repeatedStringMatch(a, b))  # Output: -1

a = ""
b = ""
print(sol.repeatedStringMatch(a, b))  # Output: -1