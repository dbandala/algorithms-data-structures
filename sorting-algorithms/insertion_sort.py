# Implementation of the insertion sort algorithm
# insertion sort is a simple sorting algorithm that builds the final sorted list one item at a time.
# It is much less efficient on large lists than more advanced algorithms such as quicksort, heapsort, or merge sort.

# insertion sort algorithm
def insertion_sort(my_list):
    for i in range(1, len(my_list)):
        current_value = my_list[i]
        position = i
        while position > 0 and my_list[position-1] > current_value:
            my_list[position] = my_list[position-1]
            position = position - 1
        my_list[position] = current_value
    return my_list

# test the insertion sort algorithm
my_list = [5, 3, 8, 6, 7, 2]
print(insertion_sort(my_list)) # [2, 3, 5, 6, 7, 8]