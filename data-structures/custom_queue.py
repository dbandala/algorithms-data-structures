# Type: Custom Queue
class Queue:
    def __init__(self, value):
        new_node = Node(value)
        self.first = new_node
        self.last = new_node
        self.length = 1

    def print_queue(self):
        temp = self.first
        while temp is not None:
            print(temp.value)
            temp = temp.next
        print("length: ", self.length)
        print("")

    def enqueue(self, value):
        new_node = Node(value)
        if self.length==0:
            self.first = new_node
            self.last = new_node
        else:
            self.last.next = new_node
            self.last = new_node
        self.length += 1
        return True
    
    def dequeue(self):
        if self.length==0:
            return None
        temp = self.first
        if self.length==1:
            self.first = None
            self.last = None
        else:
            self.first = self.first.next
            temp.next = None
        self.length -= 1
        return temp.value


class Node:
    def __init__(self, value):
        self.value = value
        self.next = None


# Test cases

queue = Queue(0)

queue.print_queue()
queue.enqueue(1)
queue.enqueue(2)
queue.enqueue(3)

queue.print_queue()
print("DEQUEUE: ",queue.dequeue()) # 0
queue.print_queue()

