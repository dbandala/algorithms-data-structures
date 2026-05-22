# Algortithm to check if two binary trees are the same

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
        if p is None and q is None:
            return True
        if p is None or q is None:
            return False
        if p.val != q.val:
            return False
        return self.isSameTree(p.left, q.left) and self.isSameTree(p.right, q.right)

# Test cases
# Test case 1
p = TreeNode(1)
p.left = TreeNode(2)
p.right = TreeNode(3)
q = TreeNode(1)
q.left = TreeNode(2)
q.right = TreeNode(3)
print(Solution().isSameTree(p, q)) # True

# Test case 2 - Hard case
p = TreeNode(1)
p.left = TreeNode(2)
p.right = TreeNode(1)
q = TreeNode(1)
q.left = TreeNode(1)
q.right = TreeNode(2)
print(Solution().isSameTree(p, q)) # False

# Test case 3 - Edge case
p = None
q = None
print(Solution().isSameTree(p, q)) # True

# Test case 4 - Big tree
p = TreeNode(1)
p.left = TreeNode(2)
p.right = TreeNode(3)
p.left.left = TreeNode(4)
p.left.right = TreeNode(5)
p.right.left = TreeNode(6)
p.right.right = TreeNode(7)
q = TreeNode(1)
q.left = TreeNode(2)
q.right = TreeNode(3)
q.left.left = TreeNode(4)
q.left.right = TreeNode(5)
q.right.left = TreeNode(6)
q.right.right = TreeNode(7)
print(Solution().isSameTree(p, q)) # True