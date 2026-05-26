# 56. Merge Intervals
# Given an array of intervals where intervals[i] = [starti, endi], merge all overlapping intervals, and return an array of the non-overlapping intervals that cover all the intervals in the input.

# Example 1:
# Input: intervals = [[1,3],[2,6],[8,10],[15,18]]
# Output: [[1,6],[8,10],[15,18]]
# Explanation: Since intervals [1,3] and [2,6] overlap, merge them into [1,6].

# Example 2:
# Input: intervals = [[1,4],[4,5]]
# Output: [[1,5]]
# Explanation: Intervals [1,4] and [4,5] are considered overlapping.

# Example 3:
# Input: intervals = [[4,7],[1,4]]
# Output: [[1,7]]
# Explanation: Intervals [1,4] and [4,7] are considered overlapping.

# Constraints:
# 1 <= intervals.length <= 104
# intervals[i].length == 2
# 0 <= starti <= endi <= 104


class Solution(object):
    def merge(self, intervals: list[list[int]]):
        """
        type intervals: list[list[int]]
        rtype: list[list[in]]
        """
        
        merged = []

        # sort by start time
        intervals.sort(key=lambda x: x[0])

        for curr in intervals:
            if len(merged)==0:
                merged.append(curr)
            elif curr[0] <= merged[len(merged)-1][1]:
                max_end = max(merged[len(merged)-1][1], curr[1])
                merged[len(merged)-1][1] = max_end
            else:
                merged.append(curr)

        return merged


sol = Solution()
intervals = [[1,3],[2,6],[8,10],[15,18]]
sol.merge(intervals) # [[1,6],[8,10],[15,18]]