# Leetcode 6. Zigzag Conversion
# The string "PAYPALISHIRING" is written in a zigzag pattern on a given number of rows like this:
# P   A   H   N
# A P L S I I G
# Y   I   R
# And then read line by line: "PAHNAPLSIIGYIR"
# Write a function in Python that will take a string and a number of rows and return the zigzag pattern.

class Solution(object):
    def convert(self, s, numRows):
        """
        :type s: str
        :type numRows: int
        :rtype: str
        """
        if numRows == 1 or numRows >= len(s):
            return s
        
        zigzag = ['' for _ in range(numRows)]
        row = 0
        direction = 1
        
        for char in s:

            print("zigzag", zigzag)

            zigzag[row] += char
            row += direction
            if row == 0 or row == numRows - 1:
                direction *= -1
        
        return ''.join(zigzag)
    
# The time complexity is O(n) where n is the length of the input string. The space complexity is also O(n) because of the list used to store the zigzag pattern.

# Test cases
sol = Solution()
print(sol.convert("PAYPALISHIRING", 3)) # PAHNAPLSIIGYIR
print(sol.convert("PAYPALISHIRING", 4)) # PINALSIGYAHRPI
print(sol.convert("A", 1)) # A