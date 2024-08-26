# Leetcode 145. Binary Tree Postorder Traversal
# Given the root of a binary tree, return the postorder traversal of its nodes' values.

# Example 1:
# Input: root = [1,null,2,3]
# Output: [3,2,1]

# Definition for a binary tree node.
# class TreeNode(object):
#     def __init__(self, val=0, left=None, right=None):
#         self.val = val
#         self.left = left
#         self.right = right

class Solution(object):
    def postorderTraversal(self, root):
        """
        :type root: TreeNode
        :rtype: List[int]
        """
        if root is None:
            return []
        if root.right is None and root.left is None:
            return []
        if root.right is None:
            return self.postorderTraversal(root.left) + [root.val]
        if root.left is None:
            return self.postorderTraversal(root.right) + [root.val]
        
        return self.postorderTraversal(root.left) + self.postorderTraversal(root.right) + [root.val]
    

# The time complexity is O(n) where n is the number of nodes in the binary tree. The space complexity is also O(n) because of the recursive calls.

# Test cases
sol = Solution()
root = [1,None,2,3]
print(sol.postorderTraversal(root)) # [3,2,1]



        