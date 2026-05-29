# Leetcode 1074. Number of Submatrices That Sum to Target
# Given a matrix and a target, return the number of non-empty submatrices that sum to target.
# A submatrix x1, y1, x2, y2 is the set of all cells matrix[x][y] with x1 <= x <= x2 and y1 <= y <= y2.
# Two submatrices (x1, y1, x2, y2) and (x1', y1', x2', y2') are different if they have some coordinate that is different: for example, if x1 != x1'.

# Example 1:
# Input: matrix = [[0,1,0],[1,1,1],[0,1,0]], target = 0
# Output: 4
# Explanation: The four 1x1 submatrices that only contain 0.

# Example 2:
# Input: matrix = [[1,-1],[-1,1]], target = 0
# Output: 5
# Explanation: The two 1x2 submatrices, plus the two 2x1 submatrices, plus the 2x2 submatrix.

# Example 3:
# Input: matrix = [[904]], target = 0
# Output: 0

# Constraints:
# 1 <= matrix.length <= 100
# 1 <= matrix[0].length <= 100
# -1000 <= matrix[i][j] <= 1000
# -10^8 <= target <= 10^8

from collections import defaultdict


class Solution(object):
    def numSubmatrixSumTarget(self, matrix, target):
        """
        Return how many non-empty submatrices sum to ``target``.

        For each top/bottom row pair, treat column totals between those rows as a
        one-dimensional array; each valid vertical strip becomes counting subarrays
        with sum ``target`` (prefix sums + frequency map).

        Time complexity: O(rows^2 * cols). Space complexity: O(cols).

        :type matrix: List[List[int]]
        :type target: int
        :rtype: int
        """
        rows, cols = len(matrix), len(matrix[0])
        count = 0

        for top in range(rows):
            column_sums = [0] * cols
            for bottom in range(top, rows):
                for c in range(cols):
                    column_sums[c] += matrix[bottom][c]
                # column_sums is a 1D array of the sum of the submatrix from the top to the bottom row
                # column_sums[0] = matrix[top][0] + matrix[top+1][0] + ... + matrix[bottom][0]
                # column_sums[1] = matrix[top][1] + matrix[top+1][1] + ... + matrix[bottom][1]
                # ...
                # column_sums[cols-1] = matrix[top][cols-1] + matrix[top+1][cols-1] + ... + matrix[bottom][cols-1]
                # we can treat this as a 1D array and use the _count_subarrays_with_sum function to count the number of subarrays that sum to target
                count += self._count_subarrays_with_sum(column_sums, target)

        return count

    def _count_subarrays_with_sum(self, nums, target):
        """
        Count contiguous subarrays of ``nums`` whose sum equals ``target``.

        Maintains a running prefix sum and a map from prefix value to how many
        times it has appeared; ``prefix - target`` lookups count valid endings.

        Time complexity: O(len(nums)). Space complexity: O(len(nums)) in the worst case.

        :type nums: List[int]
        :type target: int
        :rtype: int
        """
        prefix_count = defaultdict(int)
        prefix_count[0] = 1
        prefix = 0
        result = 0

        for value in nums:
            prefix += value
            result += prefix_count[prefix - target]
            prefix_count[prefix] += 1

        return result


# Test cases
sol = Solution()
print(sol.numSubmatrixSumTarget([[0, 1, 0], [1, 1, 1], [0, 1, 0]], 0))  # 4
print(sol.numSubmatrixSumTarget([[1, -1], [-1, 1]], 0))  # 5
print(sol.numSubmatrixSumTarget([[904]], 0))  # 0
