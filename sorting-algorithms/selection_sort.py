# Implementation of selection sort algorithm
# Selection sort is a simple sorting algorithm that selects the smallest element from an unsorted list in each iteration and places that element at the beginning of the unsorted list.

# selection sort algorithm
def selection_sort(my_list):
    for i in range(len(my_list)):
        min_index = i
        for j in range(i+1, len(my_list)):
            if my_list[j] < my_list[min_index]:
                min_index = j
        if min_index != i:
            my_list[i], my_list[min_index] = my_list[min_index], my_list[i] # swap
    return my_list


# test the selection sort algorithm
my_list = [5, 3, 8, 6, 7, 2]
print(selection_sort(my_list)) # [2, 3, 5, 6, 7, 8]