# 873. Length of Longest Fibonacci Subsequence
# A sequence x1, x2, ..., xn is Fibonacci-like if:
# n >= 3
# xi + xi+1 == xi+2 for all i + 2 <= n

# Given a strictly increasing array arr of positive integers forming a sequence, return the length of the longest Fibonacci-like subsequence of arr. If one does not exist, return 0.
# A subsequence is derived from another sequence arr by deleting any number of elements (including none) from arr, without changing the order of the remaining elements. For example, [3, 5, 8] is a subsequence of [3, 4, 5, 6, 7, 8].

# Example 1:
# Input: arr = [1,2,3,4,5,6,7,8]
# Output: 5
# Explanation: The longest subsequence that is fibonacci-like: [1,2,3,5,8].

# Example 2:
# Input: arr = [1,3,7,11,12,14,18]
# Output: 3
# Explanation: The longest subsequence that is fibonacci-like: [1,11,12], [3,11,14] or [7,11,18].

# Constraints:
# 3 <= arr.length <= 1000
# 1 <= arr[i] < arr[i + 1] <= 109

class Solution:
    def lenLongestFibSubseq(self, arr: list[int]) -> int:
        index = {x: i for i, x in enumerate(arr)}
        n = len(arr)
        longest = {}
        max_length = 0
        
        for k in range(n):
            for j in range(k):
                i_val = arr[k] - arr[j]
                if i_val < arr[j] and i_val in index:
                    i = index[i_val]
                    longest[j, k] = longest.get((i, j), 2) + 1
                    max_length = max(max_length, longest[j, k])
        
        return max_length if max_length >= 3 else 0

class NaiveSolution:
    def lenLongestFibSubseq(self, arr: list[int]) -> int:
        n = len(arr)
        max_length = 0
        
        for i in range(n):
            for j in range(i + 1, n):
                a, b = arr[i], arr[j]
                length = 2
                while a + b in arr:
                    a, b = b, a + b
                    length += 1
                if length >= 3:
                    max_length = max(max_length, length)
        
        return max_length if max_length >= 3 else 0

# Test cases
sol = Solution()
arr = [1,2,3,4,5,6,7,8]
print(sol.lenLongestFibSubseq(arr))  # Output: 5
arr = [1,3,7,11,12,14,18]
print(sol.lenLongestFibSubseq(arr))  # Output: 3
