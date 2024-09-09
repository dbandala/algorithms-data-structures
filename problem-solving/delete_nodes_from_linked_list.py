# Leetcode 3217. Delete Nodes From Linked List Present in Array
# You are given an array of integers nums and the head of a linked list. Return the head of the modified linked list after removing all nodes from the linked list that have a value that exists in nums.

# Example 1:
# Input: nums = [1,2,3], head = [1,2,3,4,5]
# Output: [4,5]
# Explanation:
# Remove the nodes with values 1, 2, and 3.

# Example 2:
# Input: nums = [1], head = [1,2,1,2,1,2]
# Output: [2,2,2]
# Explanation:
# Remove the nodes with value 1.

# Example 3:
# Input: nums = [5], head = [1,2,3,4]
# Output: [1,2,3,4]
# Explanation:
# No node has value 5.

# Constraints:
# 1 <= nums.length <= 105
# 1 <= nums[i] <= 105
# All elements in nums are unique.
# The number of nodes in the given list is in the range [1, 105].
# 1 <= Node.val <= 105
# The input is generated such that there is at least one node in the linked list that has a value not present in nums.


# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution(object):
    def modifiedList(self, nums, head):
        """
        :type nums: List[int]
        :type head: Optional[ListNode]
        :rtype: Optional[ListNode]
        """
        # approach: create a dummy node and iterate through the linked list
        # if the value of the node is not in the nums array, add it to the dummy node
        # return the dummy node

        # verify edge scenarios
        if not head:
            return None
        
        # create a set from nums list (hash table)
        s = set(nums)
        
        # create a dummy node
        dummy = ListNode(0)
        dummy.next = head

        # create a pointer to the dummy node
        prev = dummy

        # iterate through the linked list
        while head:
            if head.val in s:
                prev.next = head.next
            else:
                prev = head
            head = head.next

        return dummy.next


# Time complexity: O(n)
# Space complexity: O(1)

# Test cases
if __name__ == "__main__":
    # Example 1
    nums = [1,2,3]
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4, ListNode(5)))))
    solution = Solution()
    result = solution.modifiedList(nums, head)
    while result:
        print(result.val)
        result = result.next

    # Example 2
    nums = [1]
    head = ListNode(1, ListNode(2, ListNode(1, ListNode(2, ListNode(1, ListNode(2))))))
    solution = Solution()
    result = solution.modifiedList(nums, head)
    while result:
        print(result.val)
        result = result.next

    # Example 3
    nums = [5]
    head = ListNode(1, ListNode(2, ListNode(3, ListNode(4))))
    solution = Solution()
    result = solution.modifiedList(nums, head)
    while result:
        print(result.val)
        result = result.next








