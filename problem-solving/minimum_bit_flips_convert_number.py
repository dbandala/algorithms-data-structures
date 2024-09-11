# Leetcode 2220. Minimum Bit Flips to Convert Number
# A bit flip of a number x is choosing a bit in the binary representation of x and flipping it from either 0 to 1 or 1 to 0.
# For example, for x = 7, the binary representation is 111 and we may choose any bit (including any leading zeros not shown) and flip it. We can flip the first bit from the right to get 110, flip the second bit from the right to get 101, flip the fifth bit from the right (a leading zero) to get 10111, etc.
# Given two integers start and goal, return the minimum number of bit flips to convert start to goal.

# Example 1:
# Input: start = 10, goal = 7
# Output: 3
# Explanation: The binary representation of 10 and 7 are 1010 and 0111 respectively. We can convert 10 to 7 in 3 steps:
# - Flip the first bit from the right: 1010 -> 1011.
# - Flip the third bit from the right: 1011 -> 1111.
# - Flip the fourth bit from the right: 1111 -> 0111.
# It can be shown we cannot convert 10 to 7 in less than 3 steps. Hence, we return 3.

# Example 2:
# Input: start = 3, goal = 4
# Output: 3
# Explanation: The binary representation of 3 and 4 are 011 and 100 respectively. We can convert 3 to 4 in 3 steps:
# - Flip the first bit from the right: 011 -> 010.
# - Flip the second bit from the right: 010 -> 000.
# - Flip the third bit from the right: 000 -> 100.
# It can be shown we cannot convert 3 to 4 in less than 3 steps. Hence, we return 3.
 
# Constraints:
# 0 <= start, goal <= 109


class NaiveSolution(object):
    def minBitFlips(self, start, goal):
        """
        :type start: int
        :type goal: int
        :rtype: int
        """
        # approach: use a pointer to iterate through the binary strings
        # increment a counter when the bits are different
        # time complexity: O(n)
        # space complexity: O(1)

        # convert the start and goal numbers to binary strings
        start = bin(start)[2:]
        goal = bin(goal)[2:] # remove the '0b' prefix

        # fullfill the binary strings with leading zeros
        if len(start) < len(goal):
            start = '0' * (len(goal) - len(start)) + start
        if len(goal) < len(start):
            goal = '0' * (len(start) - len(goal)) + goal
        
        # initialize the number of flips needed
        flips = 0
        # initialize a pointer to iterate through the binary strings
        i = 0
        while i < len(start):
            # verify if the bits are different
            if start[i] != goal[i]:
                # increment the number of flips needed
                flips += 1
            # move the pointer to the next bit
            i += 1

        return flips


class Solution(object):
    def minBitFlips(self, start, goal):
        print(bin(start))
        print(bin(goal))
        n=start^goal
        c=0
        while n!=0:
            print(bin(n))
            n=n&n-1
            c+=1
        return c



# Time: O(n)
# Space: O(1)

# Test cases
if __name__ == "__main__":
    s = Solution()
    # Test case 1
    start = 10
    goal = 7
    # Output: 3
    print(s.minBitFlips(start, goal))


