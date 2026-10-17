# Leetcode 90. Subsets II
# Given an integer array nums that may contain duplicates, return all possible subsets (the power set).
# The solution set must not contain duplicate subsets. Return the solution in any order.

# Example 1:
# Input: nums = [1,2,2]
# Output: [[],[1],[1,2],[1,2,2],[2],[2,2]]

# Example 2:
# Input: nums = [0]
# Output: [[],[0]]
 
# Constraints:
# 1 <= nums.length <= 10
# -10 <= nums[i] <= 10


class Solution:
    def subsetsWithDup(self, nums: list[int]) -> list[list[int]]:
        """
            nums: list[int]
            rtype: list[list[int]
        """
        nums.sort()
        res = []

        def backtrack(start: int, path: list[int]):
            print(path)
            res.append(path)
            for i in range(start, len(nums)):
                if i > start and nums[i] == nums[i-1]:
                    continue
                backtrack(i+1, path + [nums[i]])

        backtrack(0, [])
        return res


import json
class OptimalSolution:
    def subsetsWithDup(self, nums: list[int]) -> list[list[int]]:
        nums.sort()
        res = []
        set_res = set()
        curr = []
        def dfs(i):
            if i==len(nums):
                a = str(curr.copy())
                set_res.add(a)
                return
            
            curr.append(nums[i])
            dfs(i+1)

            curr.pop()
            dfs(i+1)
        dfs(0)
        print(set_res)
        for i in set_res:
            res.append(json.loads(i))
        return res



# Validation
solution = Solution()
print(solution.subsetsWithDup([1,2,2])) # Expected output: [[],[1],[1,2],[1,2,2],[2],[2,2]]