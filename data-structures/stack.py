# Description: Implementing a stack data structure in Python
# The Stack class should have the following methods:
# __init__ - Initializes the stack with a specified value.
# print_stack - Prints the stack.
# push - Pushes a new value onto the stack.
# pop - Pops the top value off the stack.
# The Node class should have a value and a next pointer.
# The stack should keep track of the height of the stack.

class Stack:
    def __init__(self, value):
        new_node = Node(value)
        self.top = new_node
        self.height = 1

    def print_stack(self):
        temp = self.top
        while temp is not None:
            print(temp.value)
            temp = temp.next
        print("height: ", self.height)
        print("")

    def push(self, value):
        new_node = Node(value)
        if self.height==0 or self.top is None:
            self.top = new_node
        else:
            new_node.next = self.top
            self.top = new_node
        self.height += 1
        return True
    
    def pop(self):
        if self.height==0:
            return None
        temp = self.top
        self.top = self.top.next
        temp.next = None
        self.height -= 1
        return temp.value
    
class Node:
    def __init__(self, value):
        self.value = value
        self.next = None

# Test cases
stack = Stack(0)
stack.push(1)
stack.push(2)
stack.push(3)

stack.print_stack()
print("POP: ",stack.pop()) # 3
stack.print_stack()

stack.push(4)
stack.print_stack()
