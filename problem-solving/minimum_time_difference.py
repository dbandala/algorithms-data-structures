# Leetcode 539. Minimum Time Difference
# Given a list of 24-hour clock time points in "HH:MM" format, return the minimum minutes difference between any two time-points in the list.

# Example 1:
# Input: timePoints = ["23:59","00:00"]
# Output: 1

# Example 2:
# Input: timePoints = ["00:00","23:59","00:00"]
# Output: 0

# Constraints:
# 2 <= timePoints.length <= 2 * 104
# timePoints[i] is in the format "HH:MM".


class Solution(object):
    def findMinDifference(self, timePoints):
        """
        :type timePoints: List[str]
        :rtype: int
        """
        # approach: order timepoints and return difference between first and last timepoint
        timePointsMinutes = sorted([self.toMinutes(time) for time in timePoints])

        # add the first timepoint to the end of the list to account for the circular nature of the clock
        timePointsMinutes.append(timePointsMinutes[0] + 24 * 60)
        
        # find the minimum difference between any two timepoints
        min_diff = 24 * 60
        
        for i in range(1, len(timePointsMinutes)):
            min_diff = min(min_diff, abs(timePointsMinutes[i]-timePointsMinutes[i-1]))

        return min_diff
    
    def toMinutes(self, time):
        h, m = map(int, time.split(':'))
        return h * 60 + m 

# Test cases
sol = Solution()
print(sol.findMinDifference(["23:59","00:00"])) # 1
print(sol.findMinDifference(["00:00","23:59","00:00"])) # 0
        





