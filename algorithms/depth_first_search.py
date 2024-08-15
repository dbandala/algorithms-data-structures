# Description: Implement a binary tree with recursive insert and contains methods.
# The insert method should insert a new node into the tree with the given value.
# The contains method should return True if the value is in the tree, False otherwise.
# The r_contains method should do the same as the contains method, but should be implemented recursively.
# The _r_contains method should be a helper method that is called by the r_contains method.
# The _r_contains method should take in a node and a value and return True if the value is in the tree, False otherwise.
# The r_contains method should call the _r_contains method with the root node and the value.
# The Node class should have a value, a left child, and a right child.

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
    
    def r_contains(self, value):
        return self._r_contains(self.root, value)
    
    def _r_contains(self, node, value):
        if node is None:
            return False
        if value < node.value:
            return self._r_contains(node.left, value)
        elif value > node.value:
            return self._r_contains(node.right, value)
        else:
            return True
        
    def r_insert(self, value):
        if self.root is None:
            self.root = Node(value)
        self._r_insert(self.root, value)

    def _r_insert(self, node, value):
        if node is None:
            return Node(value)
        if value < node.value:
            node.left = self._r_insert(node.left, value)
        elif value > node.value:
            node.right = self._r_insert(node.right, value)
        return node
    
    def __delete_node(self, current_node, value):
        if current_node is None:
            return None
        if value<current_node.value:
            current_node.left = self.__delete_node(current_node.left, value)
        elif value>current_node.value:
            current_node.right = self.__delete_node(current_node.right, value)
        else:
            if current_node.left == None and current_node.right == None: # if node is leaf
                return None
            elif current_node.left == None: # if node has one child
                current_node = current_node.right
            elif current_node.right == None: # if node has one child
                current_node = current_node.left
            else: # if node has two children
                sub_tree_min = self.min_value(current_node.right)
                current_node.value = sub_tree_min
                current_node.right = self.__delete_node(current_node.right, sub_tree_min)
        return current_node
    
    def delete_node(self, value):
        if self.root is None:
            return None
        self.__delete_node(self.root, value)

    def min_value(self, current_node):
        if current_node.left is None:
            return current_node.value
        return self.min_value(current_node.left)
    

    # method for depth first search
    def dfs_pre_order(self):
        result = []
        def traverse(current_node):
            result.append(current_node.value)
            if current_node.left:
                traverse(current_node.left)
            if current_node.right:
                traverse(current_node.right)
        traverse(self.root)
        return result

    def dfs_post_order(self):
        result = []
        def traverse(current_node):
            if current_node.left:
                traverse(current_node.left)
            if current_node.right:
                traverse(current_node.right)
            result.append(current_node.value)
        traverse(self.root)
        return result
    
    def dfs_in_order(self):
        result = []
        def traverse(current_node):
            if current_node.left:
                traverse(current_node.left)
            result.append(current_node.value)
            if current_node.right:
                traverse(current_node.right)
        traverse(self.root)
        return result


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

# print(tree.root.value) # 10
# print(tree.root.left.value) # 5
# print(tree.root.right.value) # 15

# print(tree.contains(10)) # True
# print(tree.contains(5)) # True
# print(tree.contains(15)) # True
# print(tree.contains(50)) # False

# print(tree.r_contains(10)) # True
# print(tree.r_contains(5)) # True

# tree.r_insert(50)
# print(tree.contains(50)) # True
# print(tree.r_contains(50)) # True

print(tree.dfs_pre_order()) # [10, 5, 2, 7, 15, 12, 17]
print(tree.dfs_post_order()) # [2, 7, 5, 12, 17, 15, 10]
