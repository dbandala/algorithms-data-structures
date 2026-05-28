# 57. Insert Interval
# You are given an array of non-overlapping intervals intervals where intervals[i] = [starti, endi] represent the start and the end of the ith interval and intervals is sorted in ascending order by starti. You are also given an interval newInterval = [start, end] that represents the start and end of another interval.

# Insert newInterval into intervals such that intervals is still sorted in ascending order by starti and intervals still does not have any overlapping intervals (merge overlapping intervals if necessary).

# Return intervals after the insertion.

# Note that you don't need to modify intervals in-place. You can make a new array and return it.


# Example 1:
# Input: intervals = [[1,3],[6,9]], newInterval = [2,5]
# Output: [[1,5],[6,9]]

# Example 2:
# Input: intervals = [[1,2],[3,5],[6,7],[8,10],[12,16]], newInterval = [4,8]
# Output: [[1,2],[3,10],[12,16]]
# Explanation: Because the new interval [4,8] overlaps with [3,5],[6,7],[8,10].
 
# Constraints:
# 0 <= intervals.length <= 104
# intervals[i].length == 2
# 0 <= starti <= endi <= 105
# intervals is sorted by starti in ascending order.
# newInterval.length == 2
# 0 <= start <= end <= 105

# complexity: O(n)
class Solution(object):
    def nonOverlappingIntervals(self, intervals: list[list[int]], new_interval: list[int]):
        """
        type intervals: list[list[int]]
        type new_interval: list[int]
        rtype: list[list[int]]
        """

        merged = []
        n = len(intervals)

        # edge case
        if n==0:
            return [new_interval]

        inserted = False
        i = 0

        while i<len(intervals):
            curr = intervals[i]
            if inserted:
                merged.append(curr)
            else:
                # overlapping zone 1
                if new_interval[1] < curr[0]:
                    # new interval is before the current interval
                    merged.append(new_interval)
                    merged.append(curr)
                # overlapping zone 2
                elif curr[1] < new_interval[0] :
                    # current interval is before the new interval
                    merged.append(curr)
                else:
                    # merge zone
                    new_start = min(curr[0], new_interval[0])
                    while i<n-1 and intervals[i+1][0] <= new_interval[1]:
                        i += 1
                    new_end = max(intervals[i][1], new_interval[1])
                    merged.append([new_start, new_end])
                    inserted = True
            i += 1

        if not inserted:
            merged.append(new_interval)


        return merged
        

sol = Solution()
intervals = [[1,3],[6,9]]
new_interval = [2,5]
print(sol.nonOverlappingIntervals(intervals, new_interval)) # [[1,5],[6,9]]

intervals = [[1,5],[6,9]]
new_interval = [2,5]
print(sol.nonOverlappingIntervals(intervals, new_interval)) # [[1,5],[6,9]]

