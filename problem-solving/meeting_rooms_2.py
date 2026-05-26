# LC 253 Meeting Rooms II

# Given an array of meeting time intervals intervals where intervals[i] = [starti, endi], return the minimum number of conference rooms required.

# Example 1:
# Input: intervals = [[0,30],[5,10],[15,20]]
# Output: 2

# Example 2:
# Input: intervals = [[7,10],[2,4]]
# Output: 1

# Constraints:
# 1 <= intervals.length <= 104

import heapq

class Solution(object):
    def minMeetingRooms(self, intervals):
        """
        :type intervals: List[List[int]]
        :rtype: int
        """
        # sort meetings by start time
        intervals.sort(key=lambda x: x[0])

        # intervals heap
        ends_heap = []
        for meeting in intervals:
            s, e = meeting[0], meeting[1]
            if len(ends_heap)>0 and ends_heap[0] <= s:
                heapq.heappop(ends_heap)
            heapq.heappush(ends_heap, e)

        return len(ends_heap)


sol = Solution()
intervals = [[0,30],[5,10],[15,20]]
print(sol.minMeetingRooms(intervals)) # 2

intervals = [[7,10],[2,4]]
print(sol.minMeetingRooms(intervals)) # 1

intervals = [[1,5],[8,9],[8,9]]
print(sol.minMeetingRooms(intervals)) # 2
