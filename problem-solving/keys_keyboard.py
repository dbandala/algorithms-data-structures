# Leetcode 650. 2 Keys Keyboard
# There is only one character 'A' on the screen of a notepad. You can perform one of two operations on this notepad for each step:

# Copy All: You can copy all the characters present on the screen (a partial copy is not allowed).
# Paste: You can paste the characters which are copied last time.
# Given an integer n, return the minimum number of operations to get the character 'A' exactly n times on the screen.


# Example 1:

# Input: n = 3
# Output: 3
# Explanation: Initially, we have one character 'A'.
# In step 1, we use Copy All operation.
# In step 2, we use Paste operation to get 'AA'.
# In step 3, we use Paste operation to get 'AAA'.
# Example 2:

# Input: n = 1
# Output: 0

# Constraints:
# 1 <= n <= 1000

import collections

class Solution(object):
    def minSteps(self, n):
        """
        :type n: int
        :rtype: int
        """
        # verify edge cases
        if n==0:
            return 0
        if n==1:
            return 0
        
        # number of caracteres in the screen
        # number of caracteres in the clipboard
        start = (1, 0)

        q = collections.deque([start])
        distance = {}
        distance[start] = 0

        while len(q) > 0:

            print(q)

            screen, clipboard = q.popleft()
            d = distance[(screen, clipboard)]
            if screen == n:
                return distance[(screen, clipboard)]
            # copy all
            if (screen, screen) not in distance:
                distance[(screen, screen)] = d + 1
                q.append((screen, screen))

            # use paste
            if clipboard > 0 and (screen+clipboard)<=n and (screen + clipboard, clipboard) not in distance:
                distance[(screen + clipboard, clipboard)] = d + 1
                q.append((screen + clipboard, clipboard))
                
        return -1

# Solution 2
# Approach: Prime Factorization
# Intuition
# Let's say n is the number of characters on the screen. We can get n by copying n/2 characters and pasting it twice. This is the optimal way to get n characters on the screen. So, the number of operations required to get n characters on the screen is the sum of the number of operations required to get n/2 characters on the screen and the number of operations required to paste it twice.

# When we look at the problem, the main challenge is to minimize the number of operations required to produce exactly n characters 'A' using only "Copy All" and "Paste" operations. Since "Copy All" copies everything on the screen, it suggests that we should think in terms of copying when we have a beneficial number of 'A's that will allow us to reach n through multiple pastes. This leads us to consider the factors of n because these represent meaningful points at which we can perform a "Copy All" to maximize efficiency.

class Solution2:
    def minSteps(self, n: int) -> int:
        if n == 1:
            return 0
        
        steps = 0
        factor = 2
        
        while n > 1:
            while n % factor == 0:
                steps += factor
                n //= factor
            factor += 1
            
        return steps
        
        
    
# Test cases
sol = Solution2()
print(sol.minSteps(3)) # 3
# print(sol.minSteps(1)) # 0
# print(sol.minSteps(2)) # 2
# print(sol.minSteps(4)) # 4
# print(sol.minSteps(5)) # 5
# print(sol.minSteps(6)) # 5
# print(sol.minSteps(7)) # 7
print(sol.minSteps(8)) # 6