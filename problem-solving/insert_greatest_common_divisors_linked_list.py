# Leetcode 2807. Insert Greatest Common Divisors in Linked List
# Given the head of a linked list head, in which each node contains an integer value.
# Between every pair of adjacent nodes, insert a new node with a value equal to the greatest common divisor of them.
# Return the linked list after insertion.
# The greatest common divisor of two numbers is the largest positive integer that evenly divides both numbers.

# Example 1:
# Input: head = [18,6,10,3]
# Output: [18,6,6,2,10,1,3]
# Explanation: The 1st diagram denotes the initial linked list and the 2nd diagram denotes the linked list after inserting the new nodes (nodes in blue are the inserted nodes).
# - We insert the greatest common divisor of 18 and 6 = 6 between the 1st and the 2nd nodes.
# - We insert the greatest common divisor of 6 and 10 = 2 between the 2nd and the 3rd nodes.
# - We insert the greatest common divisor of 10 and 3 = 1 between the 3rd and the 4th nodes.
# There are no more adjacent nodes, so we return the linked list.

# Example 2:
# Input: head = [7]
# Output: [7]
# Explanation: The 1st diagram denotes the initial linked list and the 2nd diagram denotes the linked list after inserting the new nodes.
# There are no pairs of adjacent nodes, so we return the initial linked list.

# Constraints:
# The number of nodes in the list is in the range [1, 5000].
# 1 <= Node.val <= 1000

# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution(object):
    def insertGreatestCommonDivisors(self, head):
        """
        :type head: Optional[ListNode]
        :rtype: Optional[ListNode]
        """
        # verify empty list
        if head is None:
            return None
        
        # create a pointer to the head of the linked list
        current = head

        def _gcd(a, b):
            # calculate the greatest common divisor between two numbers
            while b:
                a, b = b, a % b
            return a

        # iterate through the linked list
        while current:
            # verify if the next node exists
            if current.next:
                # calculate the greatest common divisor between the current node and the next node
                gcd = _gcd(current.val, current.next.val)
                # create a new node with the greatest common divisor
                new_node = ListNode(gcd)
                # insert the new node between the current node and the next node
                new_node.next = current.next
                current.next = new_node
                # move the current pointer to the next node
                current = current.next.next
            else:
                # move the current pointer to the next node
                current = current.next

        return head
    
# For example, the linked list 18 -> 6 -> 10 -> 3 should return 18 -> 6 -> 6 -> 2 -> 10 -> 1 -> 3
# create the linked list
head = ListNode(18)
head.next = ListNode(6)
head.next.next = ListNode(10)
head.next.next.next = ListNode(3)
sol = Solution()
result = sol.insertGreatestCommonDivisors(head)
# print the linked list
while result:
    print(result.val, end=" -> ")
    result = result.next


