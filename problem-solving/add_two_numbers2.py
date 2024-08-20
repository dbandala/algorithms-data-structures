# Leetcode 2. Add Two Numbers
# You are given two non-empty linked lists representing two non-negative integers. The digits are stored in reverse order, and each of their nodes contains a single digit. Add the two numbers and return the sum as a linked list.

# You may assume the two numbers do not contain any leading zero, except the number 0 itself.

# Example
# Input: l1 = [2,4,3], l2 = [5,6,4]
# Output: [7,0,8]
# Explanation: 342 + 465 = 807.
# Example 2:

# Input: l1 = [0], l2 = [0]
# Output: [0]
# Example 3:

# Input: l1 = [9,9,9,9,9,9,9], l2 = [9,9,9,9]
# Output: [8,9,9,9,0,0,0,1]

# Constraints:
# The number of nodes in each linked list is in the range [1, 100].
# 0 <= Node.val <= 9
# It is guaranteed that the list represents a number that does not have leading zeros.

# Definition for singly-linked list.
class ListNode(object):
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

class Solution(object):
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        # verify edge cases
        if l1 is None:
            return l2
        if l2 is None:
            return l1
        
        # convert ListNode into a list
        def ll_to_number(ll):
            number = 0
            factor = 1
            while ll is not None:
                number += int(ll.val) * factor
                factor *= 10
                ll = ll.next
            return number
        
        number_1 = ll_to_number(l1)
        number_2 = ll_to_number(l2)
        sum_number = number_1 + number_2

        # convert the sum into a linked list
        prev_node = None
        for c in str(sum_number)[::-1]:
            curr_node = ListNode(int(c), prev_node)
            prev_node = curr_node
        return curr_node


        #return [int(d) for d in str(sum_number)][::-1]


# Solution 2
# Time complexity: O(max(m,n))
# Space complexity: O(max(m,n))
# where m is the number of nodes in l1 and n is the number of nodes in l2
# The Intuition is to iterate through two linked lists representing non-negative integers in reverse order, starting from the least significant digit. It performs digit-wise addition along with a carry value and constructs a new linked list to represent the sum. The process continues until both input lists and the carry value are exhausted. The resulting linked list represents the sum of the input numbers in the correct order.

class Solution2:
    def addTwoNumbers(self, l1: ListNode, l2: ListNode) -> ListNode:
        dummyHead = ListNode(0)
        tail = dummyHead
        carry = 0

        while l1 is not None or l2 is not None or carry != 0:
            digit1 = l1.val if l1 is not None else 0
            digit2 = l2.val if l2 is not None else 0

            sum = digit1 + digit2 + carry
            digit = sum % 10
            carry = sum // 10

            newNode = ListNode(digit)
            tail.next = newNode
            tail = tail.next

            l1 = l1.next if l1 is not None else None
            l2 = l2.next if l2 is not None else None

        result = dummyHead.next
        dummyHead.next = None
        return result


# Test cases
sol = Solution()
l1 = [2,4,3]
l2 = [5,6,4]
print(sol.addTwoNumbers(l1, l2)) # [7,0,8]
l1 = [0]
l2 = [0]
print(sol.addTwoNumbers(l1, l2)) # [0]
