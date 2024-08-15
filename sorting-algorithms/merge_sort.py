# implementation of merge sort algorithm
# merge sort is a divide and conquer algorithm that was invented by John von Neumann in 1945.
# It is an efficient, general-purpose, comparison-based sorting algorithm.
# Space complexity is O(n) and time complexity is O(n log n)

# merge sort algorithm
def merge_sort(arr):
    if len(arr) <= 1:
        return arr
    
    mid = len(arr) // 2
    left_half = arr[:mid]
    right_half = arr[mid:]
    
    left_half = merge_sort(left_half)
    right_half = merge_sort(right_half)
    
    return merge(left_half, right_half)

def merge(left, right):
    merged = []
    left_index = 0
    right_index = 0
    
    while left_index < len(left) and right_index < len(right):
        if left[left_index] < right[right_index]:
            merged.append(left[left_index])
            left_index += 1
        else:
            merged.append(right[right_index])
            right_index += 1
    
    while left_index < len(left):
        merged.append(left[left_index])
        left_index += 1
    
    while right_index < len(right):
        merged.append(right[right_index])
        right_index += 1
    
    return merged

# Test cases
my_list = [5, 3, 8, 6, 7, 2]
print(merge_sort(my_list)) # [2, 3, 5, 6, 7, 8]