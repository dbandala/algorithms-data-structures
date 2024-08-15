# implementaion of bubble sort algorithm
# bubble sort is a simple sorting algorithm that repeatedly steps through the list, compares adjacent elements and swaps them if they are in the wrong order.
# The pass through the list is repeated until the list is sorted.

# bubble sort algorithm
def bubble_sort(my_list):
    for i in range(len(my_list)-1, 0, -1):
        for j in range(len(my_list)-1):
            if my_list[j] > my_list[j+1]:
                my_list[j], my_list[j+1] = my_list[j+1], my_list[j] # swap
    return my_list

# test the bubble sort algorithm
my_list = [5, 3, 8, 6, 7, 2]
print(bubble_sort(my_list)) # [2, 3, 5, 6, 7, 8]
