# Description: This file contains the implementation of a heap data structure.
# 
# The heap data structure is a complete binary tree that satisfies the heap property. The heap property states that the value of a parent node is greater than or equal to the value of its children. The heap data structure is commonly used to implement priority queues.

# left_child_index = parent_index * 2
# right_child_index = parent_index * 2 + 1

class MaxHeap:
    def __init__(self):
        self.heap = []

    def _left_child(self, index):
        return index * 2 + 1
    
    def _right_child(self, index):
        return index * 2 + 2
    
    def _parent(self, index):
        return (index - 1) // 2
    
    def _swap(self, index1, index2):
        self.heap[index1], self.heap[index2] = self.heap[index2], self.heap[index1]
    
    def insert(self, value):
        self.heap.append(value)
        self.bubble_up(len(self.heap) - 1)

    def bubble_up(self, index):
        parent_index = self._parent(index)
        if index > 0 and self.heap[index] > self.heap[parent_index]:
            self._swap(index, parent_index)
            self.bubble_up(parent_index)

    def remove(self):
        if len(self.heap) == 0:
            return None
        if len(self.heap) == 1:
            return self.heap.pop()
        self._swap(0, len(self.heap) - 1)
        max_value = self.heap.pop()
        self.bubble_down(0)
        return max_value
    
    def bubble_down(self, index):
        left_child_index = self._left_child(index)
        right_child_index = self._right_child(index)
        largest = index
        if left_child_index < len(self.heap) and self.heap[left_child_index] > self.heap[largest]:
            largest = left_child_index
        if right_child_index < len(self.heap) and self.heap[right_child_index] > self.heap[largest]:
            largest = right_child_index
        if largest != index:
            self._swap(index, largest)
            self.bubble_down(largest)
        
        


# Test cases
max_heap = MaxHeap()
max_heap.insert(5)
max_heap.insert(3)
max_heap.insert(8)
max_heap.insert(1)
print(max_heap.heap) # [8, 5, 3, 1]

print(max_heap.remove()) # 8
print(max_heap.heap) # [5, 3, 1]