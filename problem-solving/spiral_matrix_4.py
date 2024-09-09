# Leetcode 2326. Spiral Matrix IV
# Generate an m x n matrix that contains the integers in the linked list presented in spiral order (clockwise), starting from the top-left of the matrix. If there are remaining empty spaces, fill them with -1.
# Return the generated matrix.

# Example 1:
# Input: m = 3, n = 5, head = [3,0,2,6,8,1,7,9,4,2,5,5,0]
# Output: [[3,0,2,6,8],[5,0,-1,-1,1],[5,2,4,9,7]]
# Explanation: The diagram above shows how the values are printed in the matrix.
# Note that the remaining spaces in the matrix are filled with -1.

# Example 2:
# Input: m = 1, n = 4, head = [0,1,2]
# Output: [[0,1,2,-1]]
# Explanation: The diagram above shows how the values are printed from left to right in the matrix.
# The last space in the matrix is set to -1.

# Constraints:
# 1 <= m, n <= 105
# 1 <= m * n <= 105
# The number of nodes in the list is in the range [1, m * n].
# 0 <= Node.val <= 1000


# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution(object):
    def spiralMatrix(self, m, n, head):
        """
        :type m: int
        :type n: int
        :type head: Optional[ListNode]
        :rtype: List[List[int]]
        """
        # approach: create a matrix with m rows and n columns (MxN)
        # iterate through the linked list and fill the matrix in spiral order
        # return the matrix

        # verify edge scenarios
        if not head:
            return None
        
        # create a matrix with m rows and n columns
        matrix = [[-1 for _ in range(n)] for _ in range(m)]

        # create a pointer to the head of the linked list
        current = head

        # create pointers to the top, bottom, left, and right boundaries of the matrix
        top, bottom, left, right = 0, m - 1, 0, n - 1

        # iterate through the matrix in spiral order
        while current:
            # iterate from left to right
            for i in range(left, right + 1):
                matrix[top][i] = current.val
                current = current.next
                if not current:
                    return matrix
            top += 1

            # iterate from top to bottom
            for i in range(top, bottom + 1):
                matrix[i][right] = current.val
                current = current.next
                if not current:
                    return matrix
            right -= 1

            # iterate from right to left
            for i in range(right, left - 1, -1):
                matrix[bottom][i] = current.val
                current = current.next
                if not current:
                    return matrix
            bottom -= 1

            # iterate from bottom to top
            for i in range(bottom, top - 1, -1):
                matrix[i][left] = current.val
                current = current.next
                if not current:
                    return matrix
            left += 1

        return matrix
    
# Time complexity: O(m*n)
# Space complexity: O(m*n)

# Test cases
if __name__ == "__main__":
    # Example 1
    m = 3
    n = 5
    


        
