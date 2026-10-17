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

from collections import OrderedDict

class LRUCache(object):
    def __init__(self, capacity):
        self.capacity = capacity
        self.cache = OrderedDict()

    def get(self, key):
        if key not in self.cache:
            return -1
        self.cache.move_to_end(key)
        return self.cache[key]

    def put(self, key, value):
        if key in self.cache:
            self.cache.move_to_end(key)
        self.cache[key] = value
        if len(self.cache) > self.capacity:
            self.cache.popitem(last=False)



from collections import deque

# The problem statement explicitly requires O(1) average time for both get and put. deque.remove(value) has to linearly scan the deque to find the value before removing it — that's O(n), not O(1). Both your get and the fixed put call this, so neither function actually meets the stated requirement, even though the logic is correct.

# This is the classic trap with this problem: a dict + deque/list "recency queue" gets the behavior right but not the complexity.
class LRUCacheSubOptimal(object):
    def __init__(self, capacity):
        """
        :type capacity: int
        """
        self.capacity = capacity
        # use a dictionary
        self.cache = {}
        # lru stack
        self.queue = deque()


    def get(self, key):
        """
        :type key: int
        :rtype: int
        """
        # if the key is in the cache
        if key in self.cache:
            self.queue.remove(key)
            self.queue.appendleft(key)
            # return the value
            return self.cache[key]
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
            self.queue.appendleft(key)
            # if the cache is full
            if len(self.cache) >= self.capacity:
                # remove the least recently used key from cache and queue
                lru_key = self.queue.pop()
                if lru_key is not None:
                    self.cache.pop(lru_key)
            # add node to the cache
            self.cache[key] = value
        else:
            self.queue.remove(key)
            self.queue.appendleft(key)
            self.cache[key] = value



# Test cases
result = []
lRUCache = LRUCache(2)
result.append(lRUCache.get(2))
result.append(lRUCache.put(2, 6)) # cache is {1=1}
result.append(lRUCache.get(1)) # return -1
result.append(lRUCache.put(1, 5))
result.append(lRUCache.put(1, 2))
result.append(lRUCache.get(1)) # return 2
result.append(lRUCache.get(2)) # return 6

print("Solution output: ", result) # [-1,null,-1,null,null,2,6]

# Test case 2
# ["LRUCache","put","put","get","put","get","put","get","get","get"]
# [[2],[1,1],[2,2],[1],[3,3],[2],[4,4],[1],[3],[4]]
result = []
lRUCache = LRUCache(2)
result.append(lRUCache.put(1, 1))
print(lRUCache.cache)
result.append(lRUCache.put(2, 2))
print(lRUCache.cache)
result.append(lRUCache.get(1)) # return 1
print(lRUCache.cache)
result.append(lRUCache.put(3, 3)) # LRU key was 2, evicts key 2, cache is {1=1, 3=3}
print(lRUCache.cache)
result.append(lRUCache.get(2)) # returns -1 (not found)
print(lRUCache.cache)
result.append(lRUCache.put(4, 4)) # LRU key was 1, evicts key 1, cache is {4=4, 3=3}
print(lRUCache.cache)
result.append(lRUCache.get(1)) # return -1 (not found)
print(lRUCache.cache)
result.append(lRUCache.get(3)) # return 3
print(lRUCache.cache)
result.append(lRUCache.get(4)) # return 4
print(lRUCache.cache)
print("Solution output: ", result) # [null,null,null,1,null,-1,null,-1,3,4]
