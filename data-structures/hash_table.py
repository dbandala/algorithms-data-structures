# Description: Hash Table implementation in Python
# The HashTable class should have the following methods:
# __init__ - Initializes the hash table with a specified size.
# __hash - Hashes the key using a simple hash function.
# print_table - Prints the hash table.
# set_item - Sets the value of the key in the hash table.
# get_item - Gets the value of the key in the hash table.
# keys - Returns a list of all the keys in the hash table.
# The hash table should handle collisions by using separate chaining.
# The hash table should have a default size of 7.
# The hash function should be the length of the key modulo the size of the hash table.
# The hash function should use a prime number to reduce collisions.
# The hash function should return the hash value.

class HashTable:
    def __init__(self, size=7):
        self.data_map = [None] * size
        self.size = size

    def __hash(self, key):
        my_hash = 0
        for letter in key:
            my_hash = (my_hash + ord(letter) * 23) % self.size # 23 is a prime number to reduce collisions % self.size to keep it within the size of the array
        return my_hash
        #return len(key) % self.size

    def print_table(self):
        #print(self.data_map)
        for i, val in enumerate(self.data_map):
            print(i, ":", val)

    def set_item(self, key, value):
        index = self.__hash(key)
        if self.data_map[index] is None:
            self.data_map[index] = []
        self.data_map[index].append([key, value])

    def get_item(self, key):
        index = self.__hash(key)
        if self.data_map[index] is None:
            return None
        for item in self.data_map[index]:
            if item[0] == key:
                return item[1]
        return None
    
    def keys(self):
        keys_array = []
        for item in self.data_map:
            if item:
                for key, value in item:
                    keys_array.append(key)
        return keys_array


# Test cases
myHashTable = HashTable()
# myHashTable.print_table()
# myHashTable.add("grapes", 10000)
# myHashTable.print_table()
# myHashTable.add("apples", 20000)
# myHashTable.print_table()

myHashTable.set_item("grapes", 10000)
myHashTable.print_table()
myHashTable.set_item("apples", 20000)
myHashTable.print_table()

print(myHashTable.get_item("grapes")) # 10000
print(myHashTable.get_item("apples")) # 20000

print(myHashTable.keys()) # ['grapes', 'apples']