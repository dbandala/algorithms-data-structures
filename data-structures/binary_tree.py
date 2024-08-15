# Description: Implement a binary tree with insert and contains methods
# The insert method should insert a new node into the tree with the given value.
# The contains method should return True if the value is in the tree, False otherwise.
# The Node class should have a value, a left child, and a right child.
#

class BinaryTree:
    def __init__(self):
        self.root = None

    def insert(self, value):
        new_node = Node(value)
        if self.root is None:
            self.root = new_node
            return True
        else:
            current = self.root
            while True:
                if value < current.value:
                    if current.left is None:
                        current.left = new_node
                        return True
                    else:
                        current = current.left
                elif value > current.value:
                    if current.right is None:
                        current.right = new_node
                        return True
                    else:
                        current = current.right
                else:
                    return False
                
    def contains(self, value):
        if self.root is None:
            return False
        current = self.root
        while current:
            if value < current.value:
                current = current.left
            elif value > current.value:
                current = current.right
            else:
                return True
        return False

class Node:
    def __init__(self, value):
        self.value = value
        self.left = None
        self.right = None

# Test cases
tree = BinaryTree()
tree.insert(10)
tree.insert(5)
tree.insert(15)
tree.insert(2)
tree.insert(7)
tree.insert(12)
tree.insert(17)

print(tree.root.value) # 10
print(tree.root.left.value) # 5
print(tree.root.right.value) # 15

print(tree.contains(10)) # True
print(tree.contains(5)) # True
print(tree.contains(15)) # True
print(tree.contains(50)) # False
