#!/bin/python3

# Amazaon interview question
# Complete the 'findRequestsInQueue' function below.
#
# The function is expected to return an INTEGER_ARRAY.
# The function accepts INTEGER_ARRAY wait as parameter.
#

def findRequestsInQueue(wait):
    # verify edge cases
    n = len(wait)
    if n==0:
        return []
    
    if n==1:
        return [1]

    request_in_queue = [n]
    
    time = 1    
    while len(wait)>0:
        wait.pop(0)
        for i in range(len(wait)):
            if i in wait and wait[i]<=time:
                del wait[i]
        
        request_in_queue.append(len(wait))
        time += 1
    
    return request_in_queue

# Test cases
# Test case 1
wait = [2, 2, 3, 1]
# Expected output: [4, 3, 2, 1]
print(findRequestsInQueue(wait))

# Test case 2
wait = [3, 1, 2, 1]
# Expected output: [4, 2, 1]
print(findRequestsInQueue(wait))

# Test case 3
wait = [4, 1, 2, 3]
# Expected output: [4, 3, 2, 1]
print(findRequestsInQueue(wait))

