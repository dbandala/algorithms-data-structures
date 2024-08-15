# Design a data structure that follows the constraints of a Least Recently Used (LRU) cache.
# Implement the LRUCache class:

# LRUCache(int capacity) Initialize the LRU cache with positive size capacity.
# int get(int key) Return the value of the key if the key exists, otherwise return -1.
# void put(int key, int value) Update the value of the key if the key exists. Otherwise, add the key-value pair to the cache. If the number of keys exceeds the capacity from this # operation, evict the least recently used key.
# The functions get and put must each run in O(1) average time complexity.

# Example 1:
# Example 1:

# Input
# ["LRUCache", "put", "put", "get", "put", "get", "put", "get", "get", "get"]
# [[2], [1, 1], [2, 2], [1], [3, 3], [2], [4, 4], [1], [3], [4]]
# Output
# [null, null, null, 1, null, -1, null, -1, 3, 4]

# Explanation
# LRUCache lRUCache = new LRUCache(2);
# lRUCache.put(1, 1); // cache is {1=1}
# lRUCache.put(2, 2); // cache is {1=1, 2=2}
# lRUCache.get(1);    // return 1
# lRUCache.put(3, 3); // LRU key was 2, evicts key 2, cache is {1=1, 3=3}
# lRUCache.get(2);    // returns -1 (not found)
# lRUCache.put(4, 4); // LRU key was 1, evicts key 1, cache is {4=4, 3=3}
# lRUCache.get(1);    // return -1 (not found)
# lRUCache.get(3);    // return 3
# lRUCache.get(4);    // return 4

class LRUCache(object):

    def __init__(self, capacity):
        """
        :type capacity: int
        """
        self.capacity = capacity
        # use a dictionary
        self.cache = {}
        # lru stack
        self.queue = DoubleLinkedList(None)


    def get(self, key):
        """
        :type key: int
        :rtype: int
        """
        # if the key is in the cache
        if key in self.cache:
            self.queue.move_to_head(self.cache[key]['node'])
            # return the value
            return self.cache[key]['value']
        else:
            return -1
        

    def put(self, key, value):
        """
        :type key: int
        :type value: int
        :rtype: None
        """
        if key not in self.cache:
            # add the key to the queue
            queue_node = self.queue.prepend(key)
            # if the cache is full
            if len(self.cache) >= self.capacity:
                # remove the least recently used key from cache and queue
                lru_key = self.queue.pop()
                if lru_key is not None:
                    self.cache.pop(lru_key)
            # add node to the cache
            self.cache[key] = {'value': value, 'node': queue_node}
        else:
            self.cache[key]['value'] = value
        self.queue.move_to_head(self.cache[key]['node'])
        





# double linked list implementation
# Type: Double Linked List
# The DoubleLinkedList class is a class that represents a double linked list. It has the following methods:

# append(value): adds a new node with the given value at the end of the list.
# pop(): removes the last node from the list and returns its value.
# prepend(value): adds a new node with the given value at the beginning of the list.
# pop_first(): removes the first node from the list and returns its value.
# get(index): returns the node at the given index.
# set_value(index, value): sets the value of the node at the given index.
# insert(index, value): inserts a new node with the given value at the given index.
# remove(index): removes the node at the given index and returns its value.
# The Node class is a class that represents a node in the double linked list. It has the following attributes:

class DoubleLinkedList:
    def __init__(self, value):
        if value is None:
            self.head = None
            self.tail = None
            self.length = 0
        else:
            new_node = Node(value)
            self.head = new_node
            self.tail = new_node
            self.length = 1
    
    def print_list(self):
        temp = self.head
        while temp is not None:
            print(temp.value)
            temp = temp.next
        print("length: ", self.length)
        print("")

    def append(self, value):
        new_node = Node(value)
        if self.head is None:
            self.head = new_node
            self.tail = new_node
        else:
            self.tail.next = new_node
            new_node.prev = self.tail
            self.tail = new_node
        self.length += 1
        return new_node
    
    def pop(self):
        if self.length==0:
            return None
        temp = self.tail
        if self.length==1:
            self.head = None
            self.tail = None
        else:
            self.tail = self.tail.prev
            self.tail.next = None
            temp.prev = None
        self.length -= 1
        return temp.value
    
    def prepend(self, value):
        new_node = Node(value)
        if (self.length==0):
            self.head = new_node
            self.tail = new_node
        else:
            self.head.prev = new_node
            new_node.next = self.head
            self.head = new_node
        self.length += 1
        return new_node
    
    def pop_first(self):
        if self.length==0:
            return None
        temp = self.head
        if self.length==1:
            self.head = None
            self.tail = None
        else:
            self.head = self.head.next
            self.head.prev = None
            temp.next = None
        self.length -= 1
        return temp.value
    
    def get(self, index):
        if index<0 or index>=self.length:
            return None
        temp = self.head
        if index<self.length/2:
            for _ in range(index):
                temp = temp.next
        else:
            temp = self.tail
            for _ in range(self.length-1, index, -1):
                temp = temp.prev
        return temp
    
    def set_value(self, index, value):
        temp = self.get(index)
        if temp:
            temp.value = value
            return True
        return False
    
    def insert(self, index, value):
        if index<0 or index>self.length:
            return None
        if index==0:
            return self.prepend(value)
        if index==self.length:
            return self.append(value)
        
        new_node = Node(value)
        before = self.get(index-1)
        after = before.next

        new_node.prev = before
        new_node.next = after
        before.next = new_node
        after.prev = new_node

        self.length += 1

    def remove(self, index):
        if index<0 or index>self.length:
            return None
        if index==0:
            return self.pop_first()
        if index==self.length-1:
            return self.pop()
        
        temp = self.get(index)
        before = temp.prev
        after = temp.next

        # unlink from structure
        temp.next = None
        temp.prev = None
        before.next = after
        after.prev = before

        self.length -= 1
        return temp
    
    def move_to_head(self, node):
        if self.head==node:
            return True
        # remove the node
        if node.prev is not None:
            node.prev.next = node.next
        if node.next is not None:
            node.next.prev = node.prev
        # if the node is the tail
        if node==self.tail:
            self.tail = node.prev
        # move the node to the head
        node.prev = None
        node.next = self.head
        self.head.prev = node
        self.head = node

class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None



# Test cases
result = []
# lRUCache = LRUCache(2)
# result.append(lRUCache.get(2))
# result.append(lRUCache.put(2, 6)) # cache is {1=1}
# result.append(lRUCache.get(1)) # return -1
# result.append(lRUCache.put(1, 5))
# result.append(lRUCache.put(1, 2))
# result.append(lRUCache.get(1)) # return 2
# result.append(lRUCache.get(2)) # return 6

# print("Solution output: ", result) # [-1,null,-1,null,null,2,6]

# Test case 2
# ["LRUCache","put","put","get","put","get","put","get","get","get"]
# [[2],[1,1],[2,2],[1],[3,3],[2],[4,4],[1],[3],[4]]
lRUCache = LRUCache(2)
result.append(lRUCache.put(1, 1))
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.put(2, 2))
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.get(1)) # return 1
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.put(3, 3)) # LRU key was 2, evicts key 2, cache is {1=1, 3=3}
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.get(2)) # returns -1 (not found)
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.put(4, 4)) # LRU key was 1, evicts key 1, cache is {4=4, 3=3}
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.get(1)) # return -1 (not found)
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.get(3)) # return 3
print(lRUCache.cache)
print(lRUCache.queue.print_list())
result.append(lRUCache.get(4)) # return 4
print(lRUCache.cache)
print(lRUCache.queue.print_list())
print("Solution output: ", result) # [null,null,null,1,null,-1,null,-1,3,4]
