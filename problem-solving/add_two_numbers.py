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

class LinkedList():
    def __init__(self):
        self.head = None
        self.tail = None
        self.length = 0
    
    def append(self, value):
        new_node = ListNode(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            self.tail = new_node
        self.length += 1
        return new_node
    
    def print_list(self):
        temp = self.head
        while temp is not None:
            print(temp.val)
            temp = temp.next
        print("length: ", self.length)
        print("")

    def to_list(self):
        temp = self.head
        result = []
        while temp is not None:
            result.append(temp.val)
            temp = temp.next
        return result
    
    def from_list(self, l, reverse=False):
        if reverse:
            l = l[::-1]
        self.head = ListNode(l[0])
        self.tail = self.head
        self.length = 1
        for i in range(1, len(l)):
            self.append(l[i])

    def read_from_right(self):
        temp = self.head
        result = 0
        i = 0
        while temp is not None:
            result += temp.val * 10**i
            temp = temp.next
            i += 1
        return result

class Solution(object):
    def addTwoNumbers(self, l1, l2):
        """
        :type l1: ListNode
        :type l2: ListNode
        :rtype: ListNode
        """
        # verify edge cases
        if l1 is None or len(l1)==0:
            return l2
        if l2 is None or len(l2)==0:
            return l1
        
        # initialize variables
        carry = 0
        l1_ll = LinkedList()
        l1_ll.from_list(l1, reverse=True)
        l2_ll = LinkedList()
        l2_ll.from_list(l2, reverse=True)

        l1_number = l1_ll.read_from_right()
        l2_number = l2_ll.read_from_right()

        sum_number = l1_number + l2_number

        return [int(d) for d in str(sum_number)][::-1]


# Test cases
sol = Solution()
l1 = [2,4,3]
l2 = [5,6,4]
print(sol.addTwoNumbers(l1, l2)) # [7,0,8]
l1 = [0]
l2 = [0]
print(sol.addTwoNumbers(l1, l2)) # [0]
