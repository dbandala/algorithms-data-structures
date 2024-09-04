# Leetcode 100. Same Tree
# Given the roots of two binary trees p and q, write a function to check if they are the same or not.
# Two binary trees are considered the same if they are structurally identical, and the nodes have the same value.

# Example 1:
# Input: p = [1,2,3], q = [1,2,3]
# Output: true

# Definition for a binary tree node.
class TreeNode(object):
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

class Solution(object):
    def isSameTree(self, p, q):
        """
        :type p: TreeNode
        :type q: TreeNode
        :rtype: bool
        """
        # verify edge scenarios
        if p is None and q is None:
            return True
        if p is None or q is None:
            return False
        
        # check if the values of the nodes are the same
        if p.val != q.val:
            return False
        
        # recursively check the left and right subtrees
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)
    

# Test cases
if __name__ == "__main__":
    # Test case 1
    p = TreeNode(1)
    p.left = TreeNode(2)
    p.right = TreeNode(3)
    q = TreeNode(1)
    q.left = TreeNode(2)
    q.right = TreeNode(3)
    # Expected output: True
    print(Solution().isSameTree(p, q)) # True

    # Test case 2
    p = TreeNode(1)
    p.left = TreeNode(2)
    q = TreeNode(1)
    q.right = TreeNode(2)
    # Expected output: False
    print(Solution().isSameTree(p, q)) # False

    # Test case 3
    p = TreeNode(1)
    p.left = TreeNode(2)
    p.right = TreeNode(1)
    q = TreeNode(1)
    q.left = TreeNode(1)
    q.right = TreeNode(2)
    # Expected output: False
    print(Solution().isSameTree(p, q)) # False
