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
        return True
    
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
        return True
    
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



class Node:
    def __init__(self, value):
        self.value = value
        self.next = None
        self.prev = None


myDoubleLinkedList = DoubleLinkedList(10)
myDoubleLinkedList.append(5)
myDoubleLinkedList.append(16)

myDoubleLinkedList.print_list() # 10, 5, 16
myDoubleLinkedList.pop()
myDoubleLinkedList.print_list() # 10, 5

myDoubleLinkedList.prepend(1)
myDoubleLinkedList.print_list() # 1, 10, 5

myDoubleLinkedList.pop_first()
myDoubleLinkedList.print_list() # 10, 5

myDoubleLinkedList.append(12)
myDoubleLinkedList.append(16)
myDoubleLinkedList.append(18)
myDoubleLinkedList.print_list() # 10, 5, 12, 16, 18
print(myDoubleLinkedList.get(2)) # 16
print(myDoubleLinkedList.get(2).value) # 16

myDoubleLinkedList.set_value(2, 20)
myDoubleLinkedList.print_list() # 10, 5, 20, 16, 18

myDoubleLinkedList.insert(2, 25)
myDoubleLinkedList.print_list() # 10, 5, 25, 20, 16, 18

myDoubleLinkedList.remove(2)
myDoubleLinkedList.print_list() # 10, 5, 20, 16, 18
