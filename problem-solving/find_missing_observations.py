# Leetcode 2028. Find Missing Observations

# You have observations of n + m 6-sided dice rolls with each face numbered from 1 to 6. n of the observations went missing, and you only have the observations of m rolls. Fortunately, you have also calculated the average value of the n + m rolls.
# You are given an integer array rolls of length m where rolls[i] is the value of the ith observation. You are also given the two integers mean and n.
# Return an array of length n containing the missing observations such that the average value of the n + m rolls is exactly mean. If there are multiple valid answers, return any of them. If no such array exists, return an empty array.
# The average value of a set of k numbers is the sum of the numbers divided by k.
# Note that mean is an integer, so the sum of the n + m rolls should be divisible by n + m.


# Example 1:
# Input: rolls = [3,2,4,3], mean = 4, n = 2
# Output: [6,6]
# Explanation: The mean of all n + m rolls is (3 + 2 + 4 + 3 + 6 + 6) / 6 = 4.

# Example 2:
# Input: rolls = [1,5,6], mean = 3, n = 4
# Output: [2,3,2,2]
# Explanation: The mean of all n + m rolls is (1 + 5 + 6 + 2 + 3 + 2 + 2) / 7 = 3.

# Example 3:
# Input: rolls = [1,2,3,4], mean = 6, n = 4
# Output: []
# Explanation: It is impossible for the mean to be 6 no matter what the 4 missing rolls are.
 
# Constraints:
# m == rolls.length
# 1 <= n, m <= 105
# 1 <= rolls[i], mean <= 6


class Solution(object):
    def missingRolls(self, rolls, mean, n):
        """
        :type rolls: List[int]
        :type mean: int
        :type n: int
        :rtype: List[int]
        """
        # first approach: calculate the sum of all rolls
        # then calculate the sum of all rolls + missing rolls
        # then calculate the sum of all missing rolls
        # then calculate the average of all missing rolls
        # then calculate the missing rolls

        m = len(rolls)
        sum_m = sum(rolls)

        sum_n = mean * (m + n) - sum_m

        # check if the sum of all missing rolls is valid (between 1 and 6 * n inclusive for each dice side)
        if sum_n < n or sum_n > 6 * n:
            return []
        
        # calculate the average of all missing rolls
        avg_n = sum_n / n

        # calculate the missing rolls
        missing_rolls = []
        for i in range(n):
            roll = int(min(6, max(1, avg_n)))
            missing_rolls.append(roll)
            sum_n -= roll
            # dividing number
            div_num = (n - (i + 1))
            if div_num != 0:
                avg_n = sum_n / (n - (i + 1))

        return missing_rolls
    

# Time complexity: O(n)
# Space complexity: O(n)

# Test cases
if __name__ == "__main__":
    s = Solution()
    print(s.missingRolls([3,2,4,3], 4, 2)) # [6,6]
    print(s.missingRolls([1,5,6], 3, 4)) # [2,3,2,2]
    print(s.missingRolls([1,2,3,4], 6, 4)) # []




