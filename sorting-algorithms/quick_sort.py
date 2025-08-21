# implementation of quick sort algorithm
# quick sort is a divide and conquer algorithm that was invented by Tony Hoare in 1960.
# It is an efficient, general-purpose, comparison-based sorting algorithm.
# Complexity: O(n log n)
# Space complexity: O(log n)

# quick sort algorithm
def quick_sort(arr):
    if len(arr) <= 1:
        return arr
    pivot = arr[len(arr) // 2]
    left = [x for x in arr if x < pivot]
    middle = [x for x in arr if x == pivot]
    right = [x for x in arr if x > pivot]
    return quick_sort(left) + middle + quick_sort(right)

# Test cases
my_list = [5, 3, 8, 6, 7, 2, 6, 2, 8, 8, 1, 4]
print(quick_sort(my_list)) # [1, 2, 2, 3, 4, 5, 6, 6, 7, 8, 8, 8]